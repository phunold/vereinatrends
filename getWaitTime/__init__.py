import re
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


def normalize_time(time_string):
    """
    normalize wait time on site into minutes
    sample strings from site are:
    "no waiting time"
    "up to 30 mins"
    "up to 60 mins"
    "up to 90 mins"
    "up to 2 h"
    "up to 3 h"
    """
    # set default wait duration to '0' minutes
    total_minutes = 0

    lower_case_time_string = time_string.lower()
    time_regex = re.compile(r"up to (\d+) (mins|h)")
    match = time_regex.match(lower_case_time_string)

    if match:
        duration = int(match.group(1))
        unit = match.group(2)

        if unit == 'mins':
            total_minutes = duration
        elif unit == 'h':
            total_minutes = duration * 60
        else:
            logging.error(
                f'PPP ValueError Invalid time unit in function normalize_time {time_string}')
    elif lower_case_time_string == "no waiting time":
        return 0

    return total_minutes


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        response = requests.get(url)
        status_code = response.status_code
        response.raise_for_status()

    except requests.exceptions.HTTPError as err:
        logging.error(f"PPP HTTPError: [{err}]")
        return func.HttpResponse(f"Request failed: [{err}]", status_code=status_code)

    except requests.exceptions.RequestException as err:
        logging.error(f"PPP RequestException: [{err}]")
        return func.HttpResponse(f"Request failed: [{err}]", status_code=500)

    # scrape wait times (both directions)
    soup = BeautifulSoup(response.content, 'html.parser')

    kl_resultSet = soup.select(klostersSelector)
    sa_resultSet = soup.select(sagliainsSelector)

    if len(kl_resultSet) != 1 or len(sa_resultSet) != 1:
        return func.HttpResponse(f"Failed to scrape wait times, html/selector may have changed.",
                                 status_code=404
                                 )

    # extract wait times as text
    kl_wait_str = kl_resultSet[0].get_text()
    sa_wait_str = sa_resultSet[0].get_text()
    # normalize time into minutes
    kl_wait_normalized = normalize_time(kl_wait_str)
    sa_wait_normalized = normalize_time(sa_wait_str)

    data = {
        "waiting_times": {
            "klosters": kl_wait_normalized,
            "sagliains": sa_wait_normalized,
        }
    }
    return func.HttpResponse(json.dumps(data), status_code=200, headers={"Content-Type": "application/json"})
