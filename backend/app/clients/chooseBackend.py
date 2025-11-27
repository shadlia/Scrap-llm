import requests


class ChooseBackend:
    def __init__(self):
        self.url = "https://deals-api-314556487628.europe-west1.run.app/webhooks/deal-datasource-ready"

    def deal_scrap_ready(self, dealID: str, datasourceid: str):
        requests.post(self.url, json={"dealId": dealID, "dataSourceId": datasourceid})
