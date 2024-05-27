import requests
import json
from datetime import datetime, timedelta
import time

# URL template
url_template = "https://iut-fbleau.fr/EDT/consulter/ajax/ep.php?p=50&start={start}&end={end}&_=1716807376784"

# Get the current date
start_date = datetime.now()

# Calculate the number of days left in the week (including today)
days_left_in_week = 4 - start_date.weekday()  # Monday is 0, ..., Friday is 4

# Dictionary to store courses for each day
weekly_courses = {}

# Function to get data for a specific day
def get_courses_for_day(start_date):
    end_date = start_date + timedelta(days=1)
    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    url = url_template.format(start=start_str, end=end_str)
    
    response = requests.get(url)
    if response.status_code == 200:
        courses = response.json()
        return courses
    else:
        return None



def get_week_courses():
    # Get courses for each remaining day of the week
    for i in range(days_left_in_week + 1):  # Including today
        current_date = start_date + timedelta(days=i)
        courses = get_courses_for_day(current_date)
        if courses is not None:
            weekly_courses[current_date.strftime("%Y-%m-%d")] = courses
    
    return weekly_courses



def get_grp_courses(grp : int, weekly_courses):
    grp_courses = {}
    i = 0
    for day, courses in weekly_courses.items():
        for course in courses:
            if course["numero"] == str(grp):
                grp_courses[i] = course
                i+=1

    sorted_grp_courses = sorted(grp_courses.items(), key=lambda x: x[1]['start'])

    return sorted_grp_courses



def split_courses(grp):
    splitted_courses = {}
    i = 0
    for index, courses in enumerate(grp):

        datetime_obj = datetime.strptime(courses[1]["start"], "%Y-%m-%d %H:%M:%S")
        # Extraire la date (garder la date)
        date_part = datetime_obj.date()
        # Extraire l'heure (garder l'heure)
        start_time_part = datetime_obj.time()


        hour1, minute1, second1 = start_time_part.hour, start_time_part.minute, start_time_part.second
        start = hour1 * 3600 + minute1 * 60 + second1

        datetime_obj = datetime.strptime(courses[1]["end"], "%Y-%m-%d %H:%M:%S")
        # Extraire la date (garder la date)
        date_part = datetime_obj.date()
        # Extraire l'heure (garder l'heure)
        end_time_part = datetime_obj.time()

        hour2, minute2, second2 = end_time_part.hour, end_time_part.minute, end_time_part.second
        end = hour2 * 3600 + minute2 * 60 + second2



        

        if end - start > 4500:
            
            mid = start + 4500

            # Calculer le nombre d'heures
            hours = mid // 3600
            # Calculer le nombre de minutes
            minutes = (mid % 3600) // 60
            # Calculer le nombre de secondes
            seconds = mid % 60
            hours = str(hours)
            minutes = str(minutes)
            seconds = str(seconds) + "0"
            if minutes == "0":
                minutes = "00"

            time_mid = f"{date_part} {hours}:{minutes}:{seconds}"
        
            first = {
                "resourceId" : courses[1]["resourceId"],
                "start" : courses[1]["start"],
                "end" : time_mid,
                "title" : courses[1]["title"],
                "numero" : courses[1]["numero"],
                "nomADE" : courses[1]["nomADE"],
                "salle" : courses[1]["salle"]
                }
            
            last = {
                "resourceId" : courses[1]["resourceId"],
                "start" : time_mid,
                "end" : courses[1]["end"],
                "title" : courses[1]["title"],
                "numero" : courses[1]["numero"],
                "nomADE" : courses[1]["nomADE"],
                "salle" : courses[1]["salle"]
                }
            splitted_courses[i] = first
            i+=1
            splitted_courses[i] = last
            i+=1
        else:
            splitted_courses[i] = courses[1]
            i+=1

    return splitted_courses



t = time.time()

weekly_courses = get_week_courses()
grp1 = split_courses(get_grp_courses(1, weekly_courses))
grp2 = split_courses(get_grp_courses(2, weekly_courses))
grp3 = split_courses(get_grp_courses(3, weekly_courses))
grp4 = split_courses(get_grp_courses(4, weekly_courses))
grp5 = split_courses(get_grp_courses(5, weekly_courses))
grp6 = split_courses(get_grp_courses(6, weekly_courses))



def create_html(grp):
    first = False
    # Création de la page HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emploi du temps de la semaine</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <h1>Emploi du temps de la semaine</h1>
        <table>
            <tr>
                <th>Heure/Jour</th>
                <th>Lundi</th>
                <th>Mardi</th>
                <th>Mercredi</th>
                <th>Jeudi</th>
                <th>Vendredi</th>
            </tr>
    """

    # Définition des plages horaires manuellement
    time_ranges = [
        ("08:45:00", "10:00:00"),
        ("10:00:00", "11:15:00"),
        ("11:15:00", "12:30:00"),
        ("12:30:00", "13:45:00"),
        ("13:45:00", "15:00:00"),
        ("15:00:00", "16:15:00"),
        ("16:15:00", "17:30:00")
    ]

    # Obtention de la date du jour
    date_du_jour = datetime.now().date()

    # Obtention du numéro du jour de la semaine (lundi = 0, mardi = 1, ..., dimanche = 6)
    jour_semaine_actuel = date_du_jour.weekday()

    # Calcul du décalage pour arriver à lundi (décalage de jour_semaine_actuel jours)
    decalage_lundi = timedelta(days=jour_semaine_actuel)

    # Obtention du lundi de la semaine en cours
    lundi = date_du_jour - decalage_lundi

    # Obtention des autres jours de la semaine
    mardi = lundi + timedelta(days=1)
    mercredi = lundi + timedelta(days=2)
    jeudi = lundi + timedelta(days=3)
    vendredi = lundi + timedelta(days=4)

    # Formatage des dates
    lundi_formatee = lundi.strftime("%Y-%m-%d")
    mardi_formatee = mardi.strftime("%Y-%m-%d")
    mercredi_formatee = mercredi.strftime("%Y-%m-%d")
    jeudi_formatee = jeudi.strftime("%Y-%m-%d")
    vendredi_formatee = vendredi.strftime("%Y-%m-%d")

    # Création des lignes pour chaque plage horaire
    for start_time, end_time in time_ranges:
        html_content += "<tr>"
        html_content += f"<td>{start_time} - {end_time}</td>"

        # Parcourir chaque jour de la semaine
        for day in [lundi_formatee, mardi_formatee, mercredi_formatee, jeudi_formatee, vendredi_formatee]:
            found_course = False
            # Vérifier si un cours est prévu pour cette plage horaire et ce jour
            for _, course in grp.items():
                course_start = course['start']
                course_end = course['end']
                course_day = course_start.split()[0]
                course_start_time = course_start.split()[1]
                course_end_time = course_end.split()[1]

                if course_start_time == start_time and \
                    course_day == day and \
                    course_end_time == end_time:
                    # Un cours est trouvé pour cette plage horaire et ce jour
                    html_content += f"""
                        <td>{course['title']}<br>
                        {course['nomADE']}<br>
                        {course['salle']}</td>
                    """
                    found_course = True
                    break
            if not found_course:
                if first:
                    html_content += "<td></td>"  # Pas de cours à cette plage horaire et ce jour
        html_content += "</tr>"

    # Fermeture de la page HTML
    html_content += """
        </table>
    </body>
    </html>
    """

    # Écriture du contenu HTML dans un fichier
    with open('emploi_du_temps.html', 'w') as file:
        file.write(html_content)



    

grp = str(input("Enter group : "))

group = "grp" + grp

create_html(globals()[group])



print("done in ", time.time()-t)