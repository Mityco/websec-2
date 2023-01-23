from university_parser import get_current_week, get_schedule, get_group_list, get_staff_list
from flask import Flask, render_template
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
    # get_group_list()
    # get_staff_list()
    get_current_week()
    app.run(debug=True)
