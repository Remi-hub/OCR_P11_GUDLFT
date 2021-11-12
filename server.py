import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


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


@app.route("/book/<competition>/<club>", methods=["GET", "POST"])
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
    competition = [c for c in competitions if c["name"] == request.form["competition"]][0]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    club_reservation = club['reservation']
    places_required = int(request.form["places"])

    competition_name = competition['name']
    places_booked = 0
    # total_price is used to store the new price for the place required ( 3 club points for 1 place )
    total_price = places_required * 3
    local_time = datetime.now()
    competition_time = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")

    # checking if the club is registered for competition, if not we create it
    if competition_name in club_reservation:
        places_booked = club_reservation[competition_name]
    else:
        club_reservation.setdefault(competition_name, 0)

    # maximum places a club can book
    places_available_for_club = 12

    # listing our 5 conditions for clubs to book an event.
    club_has_enough_points = int(club['points']) >= total_price
    club_book_less_than_places_available = places_required <= places_available_for_club
    club_book_less_than_13_places = places_booked + places_required <= places_available_for_club
    competition_in_future = competition_time > local_time
    places_required_superior_to_0 = int(request.form["places"]) > 0

    club_can_book = club_has_enough_points and club_book_less_than_places_available\
                    and club_book_less_than_13_places and competition_in_future and places_required_superior_to_0

    if club_can_book:
        places_booked = places_booked + places_required
        club_reservation[competition_name] = places_booked
        competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
        points_left = int(club['points']) - total_price
        club['points'] = points_left
        flash('booking complete')
        return render_template("welcome.html", club=club, competitions=competitions)

    # if our conditions are False, we display an error message accordingly
    error = ''
    if not club_has_enough_points:
        error += " You don't have enough points. "
    if not club_book_less_than_13_places or not club_book_less_than_places_available:
        error += " You can't book more than 12 places. "
    if not competition_in_future:
        error += " This competition already took place"
    if not places_required_superior_to_0:
        error += " You must book one place or more"

    flash(error)
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



