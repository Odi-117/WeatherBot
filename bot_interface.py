import json
from json.decoder import JSONDecodeError
import telebot
import weather
import datetime
import os
import pickle
from telebot import types

class BotInterface:
    def __init__(self) -> None:
        self._weather = weather.Weather(
            os.environ['KEY_WEATHER_API'],
            None,
            ["temperature", "windSpeed", "weatherCode"],
            "metric"
        )
        self.users = {}
        pass

    def create_keyboard_button(self, text_list: list, row_width_button: int):
        markup = types.ReplyKeyboardMarkup(row_width=row_width_button, resize_keyboard=True)
        buttons = list()
        for i in text_list:
            buttons.append(types.KeyboardButton(i))
        markup.add(*buttons)
        return markup

    def create_inline_button(self, text_callback: list, row_width_button: int):
        click_kb = types.InlineKeyboardMarkup()
        buttons: list = list()
        for i in text_callback:
            buttons.append(types.InlineKeyboardButton(
                i[0], callback_data=i[1]))
        click_kb.add(*buttons, row_width=row_width_button)
        return click_kb

    def update_wheather(self):
        d = datetime.datetime.today()
        today_weather = self._weather.get_weather("1h", d.strftime(
            "%Y-%m-%dT%H:00:00Z"), d.strftime("%Y-%m-%dT23:00:00Z"))
        d = datetime.datetime.today() + datetime.timedelta(days=1)
        tomorrow_weather = self._weather.get_weather("1h", d.strftime(
            "%Y-%m-%dT00:00:00Z"), d.strftime("%Y-%m-%dT23:00:00Z"))
        d = datetime.datetime.today() + datetime.timedelta(days=7)
        week_weater = self._weather.get_weather("1d", d.today().strftime(
            "%Y-%m-%dT%H:00:00Z"), d.strftime("%Y-%m-%dT23:00:00Z"))

        today_weather = self._weather.intervals(json.loads(today_weather))
        tomorrow_weather = self._weather.intervals(
            json.loads(tomorrow_weather))
        week_weater = self._weather.intervals(json.loads(week_weater))

        if self._weather.data_weather == None:
            self._weather.data_weather = weather.DateWeather(
                datetime.datetime.today(), {})

        self._weather.data_weather.time_update = datetime.datetime.today()
        self._weather.save_weather("today", today_weather)
        self._weather.save_weather("tomorrow", tomorrow_weather)
        self._weather.save_weather("week", week_weater)

        pickle.dump(self._weather.data_weather,
                    open(f'dump_location/{self._weather.location}.bin', 'wb'))

    def get_weather(self, key: str, datetime_: str):
        try:
            self._weather.data_weather = pickle.load(
                open(f'dump_location/{self._weather.location}.bin', 'rb'))
        except:
            self.update_wheather()

        seconds = self._weather.data_weather.get_timedelta_update(
            datetime.datetime.today()).total_seconds()
        hours = seconds // 3600

        if hours >= 6:
            self.update_wheather()
        return self._weather.data_weather.get_record_on_datatime(key, datetime_)

        pass

    def get_location(self, user_id: int):
        location = self.users[user_id]["location"]
        result = str(location.get("latitude")) + \
            ", " + str(location.get("longitude"))
        return result

    def button_main_menu(self, bot: telebot.TeleBot, message: types.Message):
        text = "Главное меню"
        text_button = ["Показать погоду", "Выбрать геолокацию"]
        text_inline_button = []

        bot.send_message(message.chat.id, text, reply_markup=self.create_keyboard_button(
            text_button, row_width_button=2))
        pass

    def button_show_weather(self, bot: telebot.TeleBot, message: types.Message):

        text = "Выберите периуд за который хотите увидеть погоду в вашем регионе"
        text_button = ["Сегодня", "Завтра", "Неделя", "Главное меню"]
        text_inline_button = []

        if self.users.get(message.from_user.id) == None:
            bot.send_message(
                message.chat.id, "для начала укажите свою геопозицию")
        else:
            self._weather.location = self.get_location(message.from_user.id)
            print(self._weather.location)
            bot.send_message(message.chat.id, text, reply_markup=self.create_keyboard_button(
                text_button, row_width_button=4))
        pass

    def button_select_geoposition(self, bot: telebot.TeleBot, message: types.Message):
        text = "Для определения погоды в вашем регионе, вам необходимо указать свою геолокацию"
        text_button = ["Главное меню"]

        keyboard = self.create_keyboard_button(text_button, row_width_button=2)
        button_geo = types.KeyboardButton(
            text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(
            message.chat.id, "Поделись местоположением", reply_markup=keyboard)

        pass

    def button_determine_geoposition(self, bot: telebot.TeleBot, message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(
            text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(
            message.chat.id, "Поделись местоположением", reply_markup=keyboard)
        pass

    def button_today(self, bot: telebot.TeleBot, message: types.Message):
        text = "Выберите время за который хотите увидеть погоду в вашем регионе"
        text_button = ["Завтра", "Неделя", "Главное меню"]
        text_inline_button = []
        hour_now = datetime.datetime.today()
        for i in range(hour_now.hour, 24):
            text_time = ""
            if i < 10:
                text_time = f"0{i}:00"

            else:
                text_time = f"{i}:00"

            text_inline_button.append([text_time, "call_today#" + text_time])

        bot.send_message(message.chat.id, "1", reply_markup=self.create_keyboard_button(
            text_button, row_width_button=2))
        bot.send_message(message.chat.id, text, reply_markup=self.create_inline_button(
            text_inline_button, row_width_button=4))
        pass

    def button_tomorrow(self, bot: telebot.TeleBot, message: types.Message):
        text = "Выберите день за который хотите увидеть погоду в вашем регионе"
        text_button = ["Сегодня", "Неделя", "Главное меню"]
        text_inline_button = []

        for i in range(1, 25):
            text_time = ""
            if i < 10:
                text_time = f"0{i}:00"

            else:
                text_time = f"{i}:00"

            text_inline_button.append(
                [text_time, "call_tomorrow#" + text_time])

        bot.send_message(message.chat.id, "1", reply_markup=self.create_keyboard_button(
            text_button, row_width_button=1))
        bot.send_message(message.chat.id, text, reply_markup=self.create_inline_button(
            text_inline_button, row_width_button=7))
        pass

    def button_week(self, bot: telebot.TeleBot, message: types.Message):
        text = "Выберите день за который хотите увидеть погоду в вашем регионе"
        text_button = ["Сегодня", "Завтра", "Главное меню"]
        text_inline_button = []
        for i in range(2, 7):
            text_inline_button.append(["", "call_week#"])

            day: datetime.date = datetime.date.today(
            ) + datetime.timedelta(days=i)

            text_inline_button[len(
                text_inline_button)-1][0] = self.weekday_on_id(int(day.weekday())) + "🟢"+day.strftime("%Y-%m-%d")+"🟢"
            text_inline_button[len(text_inline_button) -
                               1][1] += day.strftime("%Y-%m-%d")

        bot.send_message(message.chat.id, "1", reply_markup=self.create_keyboard_button(
            text_button, row_width_button=1))
        bot.send_message(message.chat.id, text, reply_markup=self.create_inline_button(
            text_inline_button, row_width_button=1))
        pass

    def location(self, bot: telebot.TeleBot, message: types.Message):
        try:
            f = open("users_save.json", "r")
            self.users = json.loads(f.read())
            f.close()
        except FileNotFoundError:
            pass
        except JSONDecodeError:
            pass

        self.users[message.from_user.id] = message.json
        print("Users = ", self.users)

        f = open("users_save.json", "w")
        f.write(json.dumps(self.users))
        f.close()
        pass

    def call_today(self, bot: telebot.TeleBot, call: types.CallbackQuery):

        today = datetime.datetime.today()
        hour = call.data.split("#")[1].split(":")
        result = self.get_weather(
            "today", today.strftime(f"%Y-%m-%dT{hour[0]}:00:00Z"))
        print(result)
        bot.send_message(
            call.message.chat.id, "Погода на сегодня\n" + self.format_text_weather(result))
        pass

    def call_tomorrow(self, bot: telebot.TeleBot, call: types.CallbackQuery):
        tomorrow = datetime.datetime.today() + datetime.timedelta(1)
        hour = call.data.split("#")[1].split(":")
        result = self.get_weather(
            "tomorrow", tomorrow.strftime(f"%Y-%m-%dT{hour[0]}:00:00Z"))
        bot.send_message(call.message.chat.id, "Погода на завтра\n" + self.format_text_weather(
            result))
        pass

    def call_week(self, bot: telebot.TeleBot, call: types.CallbackQuery):

        day_date = call.data.split("#")[1].split("-")
        day_date = datetime.date(
            int(day_date[0]), int(day_date[1]), int(day_date[2]))

        result = self.get_weather(
            "week", day_date.strftime(f"%Y-%m-%dT03:00:00Z"))
        bot.send_message(call.message.chat.id, self.format_text_weather(
            result))

        pass

    def format_text_weather(self, values: dict):
        try:
            date_text = values["startTime"].split("T")
            date_list = date_text[0].split("-")

            weekday = datetime.date(int(date_list[0]), int(
                date_list[1]), int(date_list[2])).weekday()
            weekday = self.weekday_on_id(int(weekday))

            weather_data = values["values"]
            temperature = weather_data["temperature"]
            wind_speed = weather_data["windSpeed"]
            weather_code = self.text_weather_on_id(weather_data["weatherCode"])

            result = "🟠" * 5 + "\n" + \
                date_text[0] + " 🕘 " + date_text[1] + "\n"
            result += f"{weekday}\n 🌡 {temperature}\n 🌬 {wind_speed}\n {weather_code}"
            return result
        except:
            return "ещё раз нажми"

    def weekday_on_id(self, id: int):
        weekdays = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресение"
        ]
        return weekdays[id]

    def text_weather_on_id(self, id):
        weather_index = {
            "0": "Неизвестно",
            "1000": "Ясно ☀",
            "1001": "Облачно ☁",
            "1100": "В основном ясно 🌤",
            "1101": "Небольшая облачность 🌤",
            "1102": "Переменная облачность 🌤☀",
            "2000": "Туман 🌫",
            "2100": "Легкий туман 🌫☀",
            "3000": "Легкий ветер💨",
            "3001": "Ветер💨💨",
            "3002": "Сильный ветер💨💨💨",
            "4000": "Морось 🧊",
            "4001": "Дождь🌧🌧",
            "4200": "Легкий дождь☁🌧",
            "4201": "Сильный дождь🌧🌧🌧",
            "5000": "Снег🌨🌨",
            "5001": "Шквал🌨💨",
            "5100": "Легкий снег🌨",
            "5101": "Сильный снегопад🌨🌨🌨",
            "6000": "Ледяная морось🌨🧊",
            "6001": "Ледяной дождь🌧🌧🧊",
            "6200": "Легкий ледяной дождь🌧🧊",
            "6201": "Сильный переохлажденный дождь🌧🌧🌧🧊",
            "7000": "Гранулы льда🌧🧊🧊",
            "7101": "Тяжелые гранулы льда🌧🧊🧊🧊",
            "7102": "Легкие ледяные гранулы🌧🧊",
            "8000": "Гроза⛈"
        }
        return weather_index[str(id)]
