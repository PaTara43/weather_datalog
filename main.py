import datetime
import json
import logging
import random
import sys

import requests
import threading
import time

import robonomicsinterface as RI
from typing import List

# set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

API_KEY = 'f601b0c9e92272482e5403fb30a9be7a'
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"


def get_weather() -> List[str] or None:
    city_num = random.randrange(len_city_list)
    city_id = city_list[city_num]["id"]
    city_name = city_list[city_num]["name"] + ', ' + city_list[city_num]["country"]

    url = BASE_URL + "id=" + str(city_id) + "&appid=" + API_KEY

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        main_inf = data['main']
        temperature = str(round((main_inf['temp'] - 273), 2))
        humidity = main_inf['humidity']
        pressure = main_inf['pressure']
        report = data['weather'][0]['description']
        response.close()
        return {"city": city_name, "temperature": temperature, "humidity": humidity,
                "pressure": pressure, "report": report}
    else:
        logging.error("Error in the weather HTTP request")
        response.close()
        return None


def send_datalog() -> bool:
    try:
        logging.info("Sending weather request")
        weather_data = get_weather()
        if weather_data:
            logging.info(f"Got weather in {str(weather_data['city'])}")
            weather_report = f'Weather in {str(weather_data["city"])} at {str(datetime.datetime.now())} is: ' \
                             f'temperature: {str(weather_data["temperature"])} ' \
                             f'humidity: {str(weather_data["humidity"])} ' \
                             f'pressure: {str(weather_data["pressure"])} ' \
                             f'report: {str(weather_data["report"])}'
            logging.info("Sending datalog")
            interface.record_datalog(weather_report)
            return True
        else:
            interface.record_datalog(f'Failed to get current weather in {weather_data["city"]} '
                                     f'at {datetime.datetime.now()}')
            return False
    except Exception as e:
        logging.error(f"Failed to send datalog: {e}")
        return False


if __name__ == '__main__':

    seed = sys.argv[1]
    interface = RI.RobonomicsInterface(seed=seed)
    logging.info(f"Reading Cities list")
    with open('city.list.json') as json_file:
        city_list = json.load(json_file)
        len_city_list = len(city_list)

    while True:
        threads_num = threading.activeCount()
        if threads_num > 12:
            logging.warning(f"Too many active threads: {threads_num}. Idling")
            time.sleep(12)
            continue
        send_datalog_thread = threading.Thread(target=send_datalog)
        send_datalog_thread.start()
        time.sleep(2)
        logging.info(f"Active threads count: {threads_num}")
