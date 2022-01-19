import requests
from bs4 import BeautifulSoup

LIBRARY = "Main Campus"
FORM_DATA = {
    "form_build_id": "GET FROM WEBSITE BY INSPECTING A POST REQUEST",
    "form_id": "registration_form",
    "honeypot_time": "GET FROM WEBSITE BY INSPECTING A POST REQUEST",
    "field_tn_name[und][0][value]": "YOUR NAME",
    "anon_mail": "YOUR MAIL",
    "field_stud_ma[und]": "stud",
    "field_tum_kennung[und][0][value]": "YOUR ID",
    "field_benutzungsrichtlinien[und]": 1,
    "field_datenschutzerklaerung[und]": 1,
    "field_url_token[und][0][value]": None,
    "op": "Anmelden",
    "homepage": None
}
HEADERS = {'Cookie': 'YOUR VALUE'}
BASE_URL = "https://www.ub.tum.de/en/reserve-study-desks"

page = requests.get(BASE_URL)
soup = BeautifulSoup(page.content, "html.parser")

results = soup.find_all("td", class_="views-field views-field-field-teilbibliothek")
links = soup.find_all("td", class_="views-field views-field-views-conditional internlink")

positions = [i for i, x in enumerate(results) if x.text.strip() == LIBRARY]

for index in positions:
    if links[index].text.strip() != "ausgebucht":
        reservation_id = links[index].find("a")['href'].split("/")[-1]
        url = "https://www.ub.tum.de/reserve/" + reservation_id
        print(f"Requesting: {url}")
        response = requests.request("POST", url, headers=HEADERS, data=FORM_DATA)
        print(response.headers)
    else:
        print(f"There are no more seats for: {results[index].text.strip()}")
