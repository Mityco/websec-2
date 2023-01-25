from university_parser import get_current_week, get_schedule, get_group_list, get_staff_list
from flask import Flask, render_template, request
from json import load


app = Flask(__name__)


@app.route('/')
def index():
    with open("groups.json", "r", encoding='utf-8') as file:
        data = load(file)
    faculties = []
    for item in data.keys():
        id = data[item]["id"]
        faculties.append({"name": item, "link": f"/faculty/{id}"})
    return render_template("faculties.html", faculties=faculties)


@app.route('/faculty/<int:id>')
def faculty(id):
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
def group_default_schedule():
    id = request.args.get('groupId')
    selected_week = request.args.get('selectedWeek')
    if selected_week and selected_week != "":
        week = int(selected_week)
    else:
        week = get_current_week()
    url = f"https://ssau.ru/rasp?groupId={id}&selectedWeek={week}&selectedWeekday=1"
    get_schedule(url)
    with open("schedule.json", "r", encoding='utf-8') as file:
        data = load(file)
    group = list(data.keys())[0]
    data["weeks"] = [week - 1, week, week + 1]
    data["weeks_links"] = [f"/rasp?groupId={id}&selectedWeek={week - 1}&selectedWeekday=1",
                           f"/rasp?groupId={id}&selectedWeek={week + 1}&selectedWeekday=1"]
    return render_template("group_schedule.html", group=group, schedule=data[group], data=data)


if __name__ == "__main__":
    # get_group_list()
    # get_staff_list()
    # url = f"https://ssau.ru/rasp?groupId=531873998&selectedWeek=18&selectedWeekday=1"
    # url = f" https://ssau.ru/rasp?groupId=802492112&selectedWeek=18&selectedWeekday=1"
    # get_schedule(url)
    app.run(debug=True)
