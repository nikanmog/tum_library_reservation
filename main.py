import datetime
import time

import grequests
import requests
from bs4 import BeautifulSoup

LIBRARY = "Main Campus"
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


def get_reservation_urls() -> list[str]:
    raw_page = requests.get(BASE_URL + "/en/reserve-study-desks")
    bs_page = BeautifulSoup(raw_page.content, "html.parser")

    libraries = bs_page.find_all("td", class_="views-field views-field-field-teilbibliothek")
    reservation_links = bs_page.find_all("td", class_="views-field views-field-views-conditional internlink")
    lib_indexes = [index for index, library in enumerate(libraries) if library.text.strip() == LIBRARY]

    reservation_urls = []
    for index in lib_indexes:
        if reservation_links[index].text.strip() != "ausgebucht":
            reservation_id = reservation_links[index].find("a")['href'].split("/")[-1]
            url = BASE_URL + "/en/reserve/" + reservation_id
            reservation_urls.append(url)
    print(f"Reservation URLs: {reservation_urls}")
    return reservation_urls


def create_requests(reservation_urls: list[str]) -> list[grequests.post]:
    request_list = []
    for url in reservation_urls:
        FORM_DATA.update(captcha[len(request_list)])
        request_list.append(grequests.post(url=url, data=FORM_DATA))
    return request_list


def send_requests(request_list: list[grequests.post]) -> int:
    successful_bookings = 0
    for resp in grequests.imap(request_list, len(request_list)):
        link = resp.headers.get("Link")
        print(f"Requesting {link}")
        if link and "confirmation" in link:
            print(f"Success {successful_bookings}")
            successful_bookings += 1
    return successful_bookings


def time_until_execution():
    dt = datetime.datetime.now()
    delta = ((9 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)
    return delta if delta >= 0 else 86400 - delta


def main():
    print(f"Will run in {time_until_execution()}")
    time.sleep(time_until_execution())
    reservation_urls = []

    for i in range(3600):
        try:
            reservation_urls = get_reservation_urls()
            if len(reservation_urls) > 0:
                break
        except Exception as e:
            print(e)
        time.sleep(1)
    request_list = create_requests(reservation_urls)
    successful_bookings = 0
    while successful_bookings < len(request_list):
        successful_bookings += send_requests(request_list)


if __name__ == "__main__":
    main()
