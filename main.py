import telebot
import os
from telebot import types
from bot_interface import BotInterface


if __name__ == "__main__":
    token = os.environ['KEY_TELEBOT']
    bot = telebot.TeleBot(token)
    interface: BotInterface = BotInterface()

    @bot.message_handler(commands=["start"])
    def start_bot(message: types.Message):
        text_button = ["Главное меню"]
        bot.send_message(
            message.chat.id, "Вы запустили бота. Который поможет вам определять погоду в вашем регионе", reply_markup=interface.create_keyboard_button(text_button, 2))

    @bot.message_handler(content_types=["text"])
    def start_menu(message: types.Message):

        text = message.text
        if(text == "Главное меню"):
            interface.button_main_menu(bot, message)
            pass
        elif(text == "Показать погоду"):
            interface.button_show_weather(bot, message)
            pass
        elif(text == "Выбрать геолокацию"):
            interface.button_select_geoposition(bot, message)
            pass
        elif(text == "Определить геолокацию"):
            interface.button_determine_geoposition(bot, message)
            pass
        elif(text == "Сегодня"):
            interface.button_today(bot, message)
            pass
        elif(text == "Завтра"):
            interface.button_tomorrow(bot, message)
            pass
        elif(text == "Неделя"):
            interface.button_week(bot, message)
            pass
        else:
            pass

    @bot.message_handler(content_types=['location'])
    def location (message):
        if message.location is not None:
            interface.location(bot, message)

    @bot.callback_query_handler(func=lambda call: True)
    def call_today(call: types.CallbackQuery):
        info = call.data.split("#")

        if info[0] == "call_today":
            interface.call_today(bot, call)
        elif info[0] == "call_tomorrow":
            interface.call_tomorrow(bot, call)
        elif info[0] == "call_week":
            interface.call_week(bot, call)
        pass

    bot.polling()
