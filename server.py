import re
import requests

from flask import Flask
from bs4 import BeautifulSoup
from tqdm import tqdm

app = Flask(__name__)


def get_schedule(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    owner_raw = soup.find("h1")
    owner = owner_raw.text.strip("Расписание, ")

    items = soup.findAll("div", class_="schedule__item")
    lessons_list = []
    for index in range(7, len(items)):
        temp = items[index].get_text(strip=True, separator="|")
        lessons_list.append(temp.split("|"))

    week = int(soup.find("span", class_="h3-text").get_text().strip(" неделя"))
    return week, owner, lessons_list


def get_group_list():
    page = requests.get("https://ssau.ru/rasp")
    soup = BeautifulSoup(page.text, "html.parser")
    faculties_raw = soup.find("div", class_="faculties").findAll("a", class_="h3-text")
    faculties = {}
    for faculty in faculties_raw:
        temp = faculty.get("href")
        temp = temp.strip("1")
        groups = {}
        for i in range(1, 7):
            faculty_page = requests.get(f"https://ssau.ru{temp}{i}")
            faculty_soup = BeautifulSoup(faculty_page.text, "html.parser")
            groups_raw = faculty_soup.findAll("a", class_="group-catalog__group")
            for group in groups_raw:
                groups[group.text] = group.get("href")
        faculties[faculty.text] = groups
    return faculties


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
        # https://ssau.ru/rasp?staffId=


if __name__ == "__main__":
    url = "https://ssau.ru/rasp?groupId=531873998&selectedWeek=18&selectedWeekday=1"
    # get_schedule(url)
    # get_group_list()
    get_staff_list()
    # app.run(debug=True)
