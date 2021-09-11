import datetime
import time
import requests
import json
from requests.models import LocationParseError


class Weather:

    def __init__(self, apikey: str, location: str, fields: list, units: str) -> None:
        self._url = "https://api.tomorrow.io/v4/timelines"
        self._apikey = apikey
        self.location = location
        self.fields = fields
        self.units = units
        self.data_weather = None
        pass

    def get_weather(self, timesteps: str, start_time: str, end_time: str):
        querystring = {
            "location": self.location,
            "fields": self.fields,
            "units": self.units,
            "timesteps": timesteps,
            "startTime": start_time,
            "endTime": end_time,
            "apikey": self._apikey}
        response = requests.request("GET", self._url, params=querystring)
        return response.text

    def save_weather(self, key: str, data: list):
        self.data_weather.weather[key] = data
        pass

    def get_location_by_name_city(self, name: str):
        
        pass

    def get_wheater_datetime(self, key: str, datatime: str):

        return json.loads(self.data_weather.get_record_on_datatime(key, datatime))

    def intervals(self, weather: dict):
        try:
            return weather["data"]["timelines"][0]["intervals"]
        except KeyError:
            print(weather)


class DateWeather:
    def __init__(self, time_update: datetime.datetime, weather: dict) -> None:
        self.time_update = time_update
        self.weather = weather
        pass

    def get_timedelta_update(self, datetime_: datetime.datetime):
        return datetime_ - self.time_update

    def get_record_on_datatime(self, key_weather: str, datatime_text: str):
        list_info = self.weather[key_weather]
        for i in list_info:
            if i["startTime"] == datatime_text:
                return i
        return None


if __name__ == "__main__":
    w = Weather(
        "Nf2wnhFmbyN75vmXfcvrN7zaIjLam7zk",
        "50.04451329450664, 36.29288212944572",
        ["temperature", "cloudCover", "weatherCode"],
        "metric",
        "1h"
    )

#    ["data"]["timelines"][0]["interval"][0]["values"]

    result = json.loads(w.get_wheater_from_today(3))[
        "data"]["timelines"][0]["intervals"][0]["values"]

    print("from day", "!"*20, "\n", result)
    print("get data", "!"*20, "\n", w.get_wheater_datetime(8, 9, 2021, 14, 9))
