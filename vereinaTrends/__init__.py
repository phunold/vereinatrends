import logging
import requests
from bs4 import BeautifulSoup
import json
import azure.functions as func

# selector
klostersSelector = "#c26867 > div > div > div > table > tbody > tr:nth-child(3) > td:nth-child(2)"
sagliainsSelector = "#c26867 > div > div > div > table > tbody > tr:nth-child(3) > td:nth-child(3)"
# page source
url = "https://www.rhb.ch/en/car-transporter"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    res = requests.get(url)

    status_code = res.status_code
    logging.info(f"Request to {url}: [{status_code}]")

    if status_code != 200:
        return func.HttpResponse(f"Request failed to {url} [{status_code}]",
                                 status_code=status_code
                                 )

    # scrape wait times (both directions)
    soup = BeautifulSoup(res.content, 'html.parser')

    kl_resultSet = soup.select(klostersSelector)
    sa_resultSet = soup.select(sagliainsSelector)

    if len(kl_resultSet) != 1 or len(sa_resultSet) != 1:
        return func.HttpResponse(f"Failed to scrape wait times, html/selector may have changed.",
                                 status_code=404
                                 )

    kl_wait = kl_resultSet[0].get_text()
    sa_wait = sa_resultSet[0].get_text()
    data = {
        "waiting_times": {
            "klosters": kl_wait,
            "sagliains": sa_wait,
        }
    }
    return func.HttpResponse(json.dumps(data), status_code=200, headers={"Content-Type": "application/json"})
