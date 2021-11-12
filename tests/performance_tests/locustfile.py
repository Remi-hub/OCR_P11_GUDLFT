from locust import HttpUser, task


class ProjectPerfTest(HttpUser):
    @task
    def home(self):
        self.client.get("/")

    @task()
    def login(self):
        self.client.post("/showSummary", data={'email': 'john@simplylift.co'})

    @task()
    def book(self):
        self.client.post('/purchasePlaces', data={'places': 1, 'club': 'club_test_1',
                                                  'competition': 'Test Competition'})
    @task()
    def show_club_points(self):
        self.client.get('/showPoints')
