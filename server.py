import json
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["GET", "POST"])
def showSummary():
    if request.method == "POST":
        club_found = [club for club in clubs if club["email"] == request.form["email"]]
        if len(club_found) > 0:
            return render_template("welcome.html", club=club_found[0], competitions=competitions)
        else:
            flash("Sorry, that email wasn't found.", 'error')
            return render_template("index.html")
    if request.method == "GET":
        return render_template("index.html")

@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]
    if foundClub and foundCompetition:
        return render_template(
            "booking.html", club=foundClub, competition=foundCompetition
        )
    else:
        flash("Something went wrong-please try again")
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    placesRequired = int(request.form["places"])
    if placesRequired > 12:
        flash("Sorry, you can't buy more than 12 places")
        return redirect(f'book/{competition["name"]}/{club["name"]}')
    if placesRequired <= 12 and int(club['points']) > 0 and int(club['points']) >= int(request.form["places"]):
        club['points'] = int(club['points']) - placesRequired
        competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - placesRequired
        flash("Great-booking complete!")
    else:
        flash("You don't have enough points")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/showPoints")
def show_club_points():
    club_names = []
    for club in clubs:
        club_names.append(club['name'])

    club_points = []
    for club in clubs:
        club_points.append(club['points'])

    return render_template("showPoints.html", len=len(club_names), club_names=club_names,
                           club_points=club_points)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))

