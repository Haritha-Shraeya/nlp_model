import requests


class ElasticSearchHandle(object):

    def __init__(self):
        self.url = "http://127.0.0.1:8080"

    def store_extracted_text(self, text, params):
        response = requests.post(self.url + "/insertes", json={"text": text, "challenge_id": params["challenge_id"], "challenge_title": params["challenge_title"]})



