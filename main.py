import datetime
import time

import grequests
import requests
from bs4 import BeautifulSoup

LIBRARY = "Main Campus"
HEADER = {"Cookie": "GET FROM WEBSITE BY INSPECTING A POST REQUEST"}
captcha = [
    {
        "captcha_sid": 1,
        "captcha_token": "1",
        "captcha_response": "1"
    },
    {
        "captcha_sid": 1,
        "captcha_token": "1",
        "captcha_response": "1"
    }
]

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
    "op": "Save Registration",
    "homepage": None
}
BASE_URL = "https://www.ub.tum.de"


def book_seat() -> bool:
    raw_page = requests.get(BASE_URL + "/en/reserve-study-desks")
    bs_page = BeautifulSoup(raw_page.content, "html.parser")

    libraries = bs_page.find_all("td", class_="views-field views-field-field-teilbibliothek")
    reservation_links = bs_page.find_all("td", class_="views-field views-field-views-conditional internlink")
    lib_indexes = [index for index, library in enumerate(libraries) if library.text.strip() == LIBRARY]
    async_list = []
    for index in lib_indexes:
        if reservation_links[index].text.strip() != "ausgebucht":
            reservation_id = reservation_links[index].find("a")['href'].split("/")[-1]
            url = BASE_URL + "/en/reserve/" + reservation_id
            FORM_DATA.update(captcha[len(async_list)])
            async_list.append(grequests.post(url=url, headers=HEADER, data=FORM_DATA))
        else:
            print(f"There are no more seats for: {libraries[index].text.strip()} at: {datetime.datetime.now()}")

    successful_bookings = 0
    while successful_bookings < len(async_list):
        for resp in grequests.imap(async_list, len(async_list)):
            link = resp.headers.get("Link")
            print(f"Requesting {link}")
            if "confirmation" in link:
                print(f"Success {successful_bookings}")
                successful_bookings += 1

    return successful_bookings == len(async_list)


def time_until_execution():
    dt = datetime.datetime.now()
    delta = ((9 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)
    return delta if delta >= 0 else 86400 - delta


print(f"Will run in {time_until_execution()}")
time.sleep(time_until_execution())
for i in range(3600):
    print("Sending Request")
    try:
        if book_seat():
            break
    except Exception as e:
        print(e)
    time.sleep(1)
