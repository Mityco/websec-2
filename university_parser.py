import re
import requests

from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import date, datetime
from json import dump


def get_current_week():
    page = requests.get("https://ssau.ru/rasp?groupId=531873998&selectedWeek=1&selectedWeekday=1")
    soup = BeautifulSoup(page.text, "html.parser")
    first_date = soup.find("div", class_="week-nav-current_date").get_text(strip=True)
    first_date = datetime.strptime(first_date, '%d.%m.%Y').date()
    current_date = date.today()
    difference = current_date - first_date
    return int(difference.days/7)


def get_lesson(lesson_raw):
    name = lesson_raw.find("div", class_="body-text").get_text(strip=True, separator=" ")
    place = lesson_raw.find("div", class_="schedule__place").get_text(strip=True, separator=" ")
    staff_raw = lesson_raw.find("div", class_="schedule__teacher")
    staff = []
    staff_link = []
    if staff_raw is not None:
        temp = staff_raw.findAll("a")
        for i in range(len(temp)):
            staff.append(temp[i].get_text(strip=True, separator=" "))
            staff_link.append(temp[i].get("href"))
    groups_raw = lesson_raw.findAll("a", class_="schedule__group")
    groups = []
    if len(groups_raw) != 0:
        for i in range(len(groups_raw)):
            group = groups_raw[i].get_text(strip=True, separator=" ")
            groups.append(group)
    return {"name": name, "place": place, "staff": staff, "staff_link": staff_link, "groups": groups}


def get_schedule(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    owner_raw = soup.find("h1")
    owner = owner_raw.text.strip("Расписание, ")

    week = int(soup.find("span", class_="h3-text").get_text().strip(" неделя"))

    timetable_head_raw = soup.findAll("div", class_="schedule__head")
    timetable_head = [timetable_head_raw[0].get_text(strip=True)]
    for i in range(1, len(timetable_head_raw)):
        weekday = timetable_head_raw[i].find("div", class_="schedule__head-weekday").get_text(strip=True)
        weekday_date = timetable_head_raw[i].find("div", class_="schedule__head-date").get_text(strip=True)
        timetable_head.append({"weekday": weekday, "date": weekday_date})
    timetable_time_raw = soup.findAll("div", class_="schedule__time")
    timetable_time = []
    for time_cell in timetable_time_raw:
        timespan = time_cell.findAll("div", class_="schedule__time-item")
        str_timespan = str()
        for item in timespan:
            str_timespan += f"{item.get_text(strip=True)}\n"
        timetable_time.append(str_timespan)
    schedule_raw = soup.findAll("div", class_="schedule__item")
    schedule = []
    for index in range(7, len(schedule_raw)):
        cell = schedule_raw[index]
        lesson = cell.findAll("div", class_="schedule__lesson")
        if len(lesson) == 0:
            schedule.append("")
        else:
            lesson_cell = []
            for item in lesson:
                lesson_cell.append(get_lesson(item))
            schedule.append(lesson_cell)
    final_schedule = [timetable_head]
    for i in range(5):
        final_schedule.append([timetable_time[i], schedule[i*6:(i+1)*6]])
    with open("schedule.json", "w", encoding='utf-8') as file:
        dump({f"{owner} - {week}": final_schedule}, file, indent=4, ensure_ascii=False)


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

