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


class TestIntegration(TestClient):

    def test_client_can_login_and_is_redirected_on_logout(self, test_client):
        login_page = test_client.get("/")
        can_login = test_client.get("/", data={'email': 'john@simplylift.co'})
        can_logout = test_client.get("/logout")

        assert login_page.status_code == 200
        assert can_login.status_code == 200
        assert can_logout.status_code == 302

    def test_client_login_and_book_places_for_event_club_points_are_deducted(self, test_client):
        """
        Check the club's numbers of points after booking
        """
        test_client.get("/")
        test_client.get("/", data={'email': 'club@test2.co'})
        test_client.get("/showSummary")
        test_client.get("book/Test%20Competition/club_test_2")

        # the club has a total of 13 points
        club_points = server.clubs[4]['points']

        # the club is booking one place, with a value of 3 points
        test_client.post("/purchasePlaces",  data={'places': 1, 'club': 'club_test_2',
                                                   'competition': 'Test Competition'},
                         follow_redirects=True)

        club_points_after_booking = server.clubs[4]['points']

        # we check if the club points are well deducted, 10 in this case.
        assert club_points_after_booking == 10

    def test_client_login_and_book_places_for_event_competition_places_are_deducted(self, test_client):
        """
        Check the competition number of places left after booking
        """
        test_client.get("/")
        test_client.get("/", data={'email': 'club@test2.co'})
        test_client.get("/showSummary")
        test_client.get("book/Test%20Competition/club_test_2")

        # the competition has a total of 13 places
        competition_places = server.competitions[2]['numberOfPlaces']

        # the club is booking one place
        test_client.post("/purchasePlaces", data={'places': 1, 'club': 'club_test_2',
                                                  'competition': 'Test Competition'},
                         follow_redirects=True)

        competition_places_after_booking = server.competitions[2]['numberOfPlaces']

        # we check if the competition places are well deducted, 12 in this case.
        assert competition_places_after_booking == 12

