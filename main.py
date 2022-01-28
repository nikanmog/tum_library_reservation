import datetime
import time
import requests
from bs4 import BeautifulSoup

LIBRARY = "Main Campus"
HEADER = {"Cookie": "GET FROM WEBSITE BY INSPECTING A POST REQUEST"}
captcha_1 = {
    "captcha_sid": 1234,
    "captcha_token": "1234",
    "captcha_response": "1234"
}
captcha_2 = {
    "captcha_sid": 1234,
    "captcha_token": "1234",
    "captcha_response": "1234"
}
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
BASE_URL = "https://www.ub.tum.de"


def book_seat() -> bool:
    is_seat_booked = False
    raw_page = requests.get(BASE_URL + "/en/reserve-study-desks")
    bs_page = BeautifulSoup(raw_page.content, "html.parser")

    libraries = bs_page.find_all("td", class_="views-field views-field-field-teilbibliothek")
    reservation_links = bs_page.find_all("td", class_="views-field views-field-views-conditional internlink")
    lib_indexes = [index for index, library in enumerate(libraries) if library.text.strip() == LIBRARY]
    captcha_switch = 0
    for index in lib_indexes:
        if reservation_links[index].text.strip() != "ausgebucht":
            reservation_id = reservation_links[index].find("a")['href'].split("/")[-1]
            url = BASE_URL + "/reserve/" + reservation_id
            print(f"Requesting: {url} at: {datetime.datetime.now()}")
            FORM_DATA.update(captcha_1 if captcha_switch % 2 == 0 else captcha_2)
            captcha_switch += 1
            response = requests.request("POST", url=url, headers=HEADER, data=FORM_DATA)
            print(response.headers)
            is_seat_booked = True
        else:
            print(f"There are no more seats for: {libraries[index].text.strip()} at: {datetime.datetime.now()}")
    return is_seat_booked


def time_until_execution():
    dt = datetime.datetime.now()
    delta = ((9 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)
    return delta if delta >= 0 else 86400 - delta


print(f"Will run in {time_until_execution()}")
time.sleep(time_until_execution() - 1)
for i in range(10):
    time.sleep(2)
    print("Sending Request")
    if book_seat():
        break
