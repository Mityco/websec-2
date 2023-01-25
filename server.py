import re

from university_parser import get_current_week, get_schedule, get_group_list, get_staff_list
from flask import Flask, render_template, request
from json import load


app = Flask(__name__)


def search(req):
    found_items = {}
    if req and req != "":
        if len(re.findall(r"\d{4}-\d{6}[A-Z]", req)) != 0:
            with open("groups.json", "r", encoding='utf-8') as file:
                data = load(file)
            for faculty, items in data.items():
                for number, link in data[faculty]["groups"].items():
                    if number.strip() == req:
                        found_items[number] = link
        else:
            with open("staff.json", "r", encoding='utf-8') as file:
                data = load(file)
            for name, link in data.items():
                if name.strip() == req:
                    found_items[name] = link
    return found_items


@app.route('/')
def main_page():
    search_request = request.args.get('searchRequest')
    if search_request and search_request != "":
        found = search(search_request)
        if found != {}:
            return render_template("found_items.html", found=found)
        else:
            return render_template("found_items.html", found=found)
    with open("groups.json", "r", encoding='utf-8') as file:
        data = load(file)
    faculties = []
    for item in data.keys():
        id = data[item]["id"]
        faculties.append({"name": item, "link": f"/faculty/{id}"})
    return render_template("faculties.html", faculties=faculties)


@app.route('/faculty/<int:id>')
def faculty_page(id):
    search_request = request.args.get('searchRequest')
    if search_request and search_request != "":
        found = search(search_request)
        if found != {}:
            return render_template("found_items.html", found=found)
        else:
            return render_template("found_items.html", found=found)
    with open("groups.json", "r", encoding='utf-8') as file:
        data = load(file)
    groups_raw = {}
    for item in data.keys():
        if int(data[item]["id"]) == id:
            groups_raw = data[item]["groups"]
            break
        else:
            continue
    groups = []
    for number, link in groups_raw.items():
        groups.append({"number": number, "link": link})
    return render_template("groups.html", groups=groups, faculty=item)


@app.route('/rasp')
def schedule_page():
    search_request = request.args.get('searchRequest')
    if search_request and search_request != "":
        found = search(search_request)
        if found != {}:
            return render_template("found_items.html", found=found)
        else:
            return render_template("found_items.html", found=found)
    selected_week = request.args.get('selectedWeek')
    group_id = request.args.get('groupId')
    staff_id = request.args.get('staffId')

    if selected_week and selected_week != "":
        week = int(selected_week)
    else:
        week = get_current_week()

    if group_id and group_id != "":
        url = f"https://ssau.ru/rasp?groupId={group_id}&selectedWeek={week}&selectedWeekday=1"
        type = "groupId"
    elif staff_id and staff_id != "":
        url = f"https://ssau.ru/rasp?staffId={staff_id}&selectedWeek={week}&selectedWeekday=1"
        type = "staffId"
    get_schedule(url)
    with open("schedule.json", "r", encoding='utf-8') as file:
        data = load(file)
    owner = list(data.keys())[0]
    data["weeks"] = [week - 1, week, week + 1]
    data["weeks_links"] = [f"/rasp?{type}={group_id}&selectedWeek={week - 1}&selectedWeekday=1",
                           f"/rasp?{type}={group_id}&selectedWeek={week + 1}&selectedWeekday=1"]
    return render_template("schedule.html", owner=owner, schedule=data[owner], data=data)


if __name__ == "__main__":
    get_group_list()
    get_staff_list()
    app.run(debug=True)
