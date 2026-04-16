from locust import HttpUser, task, between


class LoadTest(HttpUser):
    wait_time = between(1, 2)

    @task
    def test_endpoint(self):
        self.client.get("/async/")  # change this to test each endpoint
