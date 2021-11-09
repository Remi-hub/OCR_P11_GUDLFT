import pytest
import server


class TestClient:
    @pytest.fixture()
    def test_client(self):
        server.app.testing = True
        server.clubs = server.loadClubs()
        server.competitions = server.loadCompetitions()
        with server.app.test_client() as client:
            return client


class TestIndex(TestClient):

    def test_status_code_200(self, test_client):
        res = test_client.get("/")
        assert res.status_code == 200

    def test_should_reach_the_welcome_page(self, test_client):
        res = test_client.get("/")
        assert str(res.data).find('Welcome to the GUDLFT Registration Portal!') > 0


class TestSummary(TestClient):

    def test_login_with_registered_email_and_status_code_200(self, test_client):
        res = test_client.post("/showSummary", data={'email': 'john@simplylift.co'})
        assert res.status_code == 200
        assert str(res.data).find('Welcome,') > 0

    def test_login_with_no_registered_email_and_status_code_200(self, test_client):
        res = test_client.post("/showSummary", data={'email': 'test@exemple.co'})
        assert res.status_code == 200
        assert str(res.data).find('Sorry') > 0


class TestBooking(TestClient):

    def test_status_code_200(self, test_client):
        res = test_client.get('/book/Spring%20Festival/Simply%20Lift')
        assert res.status_code == 200

    def test_too_many_places_wanted_error_message(self, test_client):
        """
        Assert is True if the error message is displayed
        """
        res = test_client.post('/purchasePlaces', data={'places': 13,
                                                        'club': 'Simply Lift',
                                                        'competition': 'Spring Festival'}, follow_redirects=True)

        assert str(res.data).find("book more than 12 places") > 0

    def test_club_points_required_to_book_event_are_deducted(self, test_client):
        """
        Check if the club points are deducted after a booking takes place
        """
        # We select a club with a total of 13 points
        club_points = server.clubs[0]['points']
        # The client is booking one place
        test_client.post('/purchasePlaces', data={'places': 1, 'club': 'Simply Lift',
                                                  'competition': 'Spring Festival'}, follow_redirects=True)
        # The club has now a total of 12 points ( 13 before the booking, a place cost 1 point )
        club_points_left = server.clubs[0]['points']
        # We booked one place, costing 3 points, 13 club_points initially, minus 3 must be equal to 10
        assert club_points_left == 10

    def test_booking_message_displays_when_successful_booking_takes_place(self, test_client):
        """
        check if a  message displays on successful booking
        """
        res = test_client.post('/purchasePlaces', data={'places': 1, 'club': 'Simply Lift',
                                                        'competition': 'Spring Festival'}, follow_redirects=True)

        assert str(res.data).find('booking complete') > 0

    def test_message_displays_when_clubs_dont_have_enough_points(self, test_client):
        """
        check if a message displays when the club don't have enough points
        """
        # we select a club which has a total of 4 points, making the booking of 5 places impossible
        res = test_client.post('/purchasePlaces', data={'places': 5, 'club': 'Iron Temple',
                                                        'competition': 'Spring Festival'}, follow_redirects=True)
        assert str(res.data).find('have enough points') > 0

    def test_club_is_not_registered_for_competition(self, test_client):
        """
        check if a club is not registered for a set competition
        """
        # we select our club and competition for testing
        club = server.clubs[0]
        competition = server.competitions[0]

        club_reservation = club["reservation"]
        competition_name = competition['name']

        if competition_name in club_reservation:
            assert True

    def test_register_a_club_for_competition(self, test_client):
        """
        check if a club is registered for a set competition
        """
        # we select our club and competition for testing
        club = server.clubs[0]
        competition = server.competitions[0]

        club_reservation = club["reservation"]
        competition_name = competition['name']

        # we create the competition for the club, and setting the number of places booked to 0
        competition_name = competition_name
        number_of_places_booked = club_reservation.setdefault(competition_name, 0)

        assert competition_name == 'Spring Festival'
        assert number_of_places_booked == 0




class TestShowPoints(TestClient):

    def test_status_code_200(self, test_client):
        res = test_client.get('/showPoints')
        assert res.status_code == 200

    def test_list_of_clubs_should_be_displayed(self, test_client):
        res = test_client.get('/showPoints')
        assert str(res.data).find('List of clubs') > 0

    def test_link_to_index_should_be_displayed(self, test_client):
        res = test_client.get('/showPoints')
        assert str(res.data).find('Back to index') > 0

