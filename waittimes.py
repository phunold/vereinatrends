import requests
from bs4 import BeautifulSoup

# selector
klostersSelector = "#c26867 > div > div > div > table > tbody > tr:nth-child(3) > td:nth-child(2)"
sagliainsSelector = "#c26867 > div > div > div > table > tbody > tr:nth-child(3) > td:nth-child(3)"
url = "https://www.rhb.ch/en/car-transporter#vereina"
page = requests.get(url)

print(f"Request to {url}: [{page.status_code}]")

soup = BeautifulSoup(page.content, 'html.parser')

klostersWait = soup.select(klostersSelector)[0].get_text()
print(f"Klosters Wait: {klostersWait}")
sagliainsWait = soup.select(sagliainsSelector)[0].get_text()
print(f"Sagliains Wait: {sagliainsWait}")
