from locust import HttpUser, task, between

class SiteUser(HttpUser):
    wait_time = between(0.1, 0.5)
    host = "https://antiddos.duckdns.org"

    @task
    def load_homepage(self):
        self.client.get("/", verify=False)
