import re
import requests

from flask import Flask, render_template
from bs4 import BeautifulSoup
from tqdm import tqdm
from json import dump, load
from datetime import date, datetime

app = Flask(__name__)


def get_current_week():
    page = requests.get("https://ssau.ru/rasp?groupId=531873998&selectedWeek=1&selectedWeekday=1")
    soup = BeautifulSoup(page.text, "html.parser")
    first_date = soup.find("div", class_="week-nav-current_date").get_text(strip=True)
    first_date = datetime.strptime(first_date, '%d.%m.%Y').date()
    current_date = date.today()
    difference = current_date - first_date
    return int(difference.days/7)


def get_schedule(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    owner_raw = soup.find("h1")
    owner = owner_raw.text.strip("Расписание, ")

    items = soup.findAll("div", class_="schedule__item")
    lessons_list = []
    for index in range(7, len(items)):
        temp = items[index].get_text(strip=True, separator="|")
        cell = temp.split("|")
        staff = items[index].find("a", class_="caption-text")
        if staff is None:
            lessons_list.append(cell)
            continue
        staff_link = staff.get("href")
        if len(cell) == 3:
            lesson = {"title": cell[0], "place": cell[1], "staff_name": cell[2], "staff_id": staff_link}
            lessons_list.append(lesson)
        elif 3 < len(cell) < 8:
            lesson = {"title": cell[0], "place": cell[1], "staff_name": cell[2], "staff_id": staff_link,
                      "groups": cell[3:]}
            lessons_list.append(lesson)
        elif len(cell) == 8:
            lesson = [{"title": cell[0], "place": cell[1], "staff_name": cell[2], "staff_id": staff_link,
                       "groups": cell[3]}, {"title": cell[4], "place": cell[5], "staff_name": cell[6],
                                            "staff_id": staff_link, "groups": cell[7]}]
            lessons_list.append(lesson)
    week = int(soup.find("span", class_="h3-text").get_text().strip(" неделя"))
    return week, owner, lessons_list


def get_group_list():
    page = requests.get("https://ssau.ru/rasp")
    soup = BeautifulSoup(page.text, "html.parser")
    faculties_raw = soup.find("div", class_="faculties").findAll("a", class_="h3-text")
    faculties = {}
    for faculty in faculties_raw:
        temp = faculty.get("href")
        id = re.search(r'\d{9}', temp).group()
        temp = temp.strip("1")
        groups = {}
        for i in range(1, 7):
            faculty_page = requests.get(f"https://ssau.ru{temp}{i}")
            faculty_soup = BeautifulSoup(faculty_page.text, "html.parser")
            groups_raw = faculty_soup.findAll("a", class_="group-catalog__group")
            for group in groups_raw:
                groups[group.text] = group.get("href")
        faculty_data = {"id": id, "groups": groups}
        faculties[faculty.text] = faculty_data
    with open("groups.json", "w", encoding='utf-8') as file:
        dump(faculties, file, indent=4, ensure_ascii=False)


def get_staff_list():
    staff_list = {}
    for i in tqdm(range(1, 114)):
        page = requests.get(f"https://ssau.ru/staff?page={i}&letter=0")
        soup = BeautifulSoup(page.text, "html.parser")
        staff_raw = soup.findAll("li", class_="list-group-item list-group-item-action")
        for staff in staff_raw:
            temp = staff.find("a")
            id = temp.get("href")
            id = re.search(r'\d{7,9}', id)
            if id is not None:
                id = id.group()
                name = temp.get_text().split(" ")
                if len(name) == 3:
                    name = str(f"{name[0]} {name[1][0]}.{name[2][0]}.")
                else:
                    name = str(f"{name[0]} {name[1][0]}.")
                staff_list[name] = str(f"/rasp?staffId={id}")
            else:
                continue
    with open("staff.json", "w", encoding='utf-8') as file:
        dump(staff_list, file, indent=4, ensure_ascii=False)


@app.route('/')
def index():
    with open("groups.json", "r", encoding='utf-8') as file:
        data = load(file)
    faculties = []
    for item in data.keys():
        id = data[item]["id"]
        faculties.append({"name": item, "link": f"/faculty/{id}"})
    return render_template("faculties.html", faculties=faculties)


@app.route('/faculty/<id>')
def faculty(id):
    with open("groups.json", "r", encoding='utf-8') as file:
        data = load(file)
    groups_raw = {}
    for item in data.keys():
        if data[item]["id"] == id:
            groups_raw = data[item]["groups"]
            break
        else:
            continue
    groups = []
    for i in groups_raw.keys():
        groups.append({"number": i, "link": groups_raw[i]})
    return render_template("groups.html", groups=groups, faculty=item)


if __name__ == "__main__":
    url = "https://ssau.ru/rasp?groupId=531873998&selectedWeek=18&selectedWeekday=1"
    # get_schedule(url)
    # get_group_list()
    # get_staff_list()
    get_current_week()
    app.run(debug=True)
