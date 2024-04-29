import telebot
from telebot import types
from currency_converter import CurrencyConverter
import requests
import json
from random import choice

comments = ['Вся красота мира в одной картинке', 'Моменты, которые запечатлены навсегда',
            'Счастье в каждом кадре', 'Когда слова не нужны, достаточно фотографии',
            'История, рассказанная через объектив', 'Остановить время в одном кадре',
            'Фотография — это способ улыбнуться в будущем', 'Сегодня — самый лучший день',
            'Я не доверяю словам. Я доверяю фотографиям']

bot = telebot.TeleBot('6940446227:AAGRHFNbGeU2E30Gu-1NvhrpzD1NQPvm-zs')
API = 'fc51aad507de82b168d5123cc28d4888'
currency = CurrencyConverter()
amount = 0


@bot.message_handler(commands=['start', 'main', 'hello'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Услышать новости', url='https://dzen.ru/news/')
    btn2 = types.InlineKeyboardButton('Посмотреть погоду', callback_data='whether')
    btn3 = types.InlineKeyboardButton('Перевести валюту', callback_data='money')
    btn4 = types.InlineKeyboardButton('Оценить фото', callback_data='koment')
    btn5 = types.InlineKeyboardButton('Сделать заказ на яндекс маркете', url='https://market.yandex.ru/?utm_source_service=suggest&src_pof=901&icookie=ZUC8Q9DKMCVZ5khFLpDeFpz9NCP3p2YnOvvhMjVEsf5GfktkCINJBmtshlOnIS8mQ+x6vC2UCK+x17LFvQN6OdG1LPA=&wprid=9173185276109650074100857403180')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Чем сегодня займёмся?',
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_whether(callback):
    if callback.data == 'whether':
        bot.send_message(callback.message.chat.id, f'Введите город, который вам интересен.')
        bot.register_next_step_handler(callback.message, get_weather)
    elif callback.data == 'money':
        bot.send_message(callback.message.chat.id, f'Введите сумму, которую хотите перевести')
        bot.register_next_step_handler(callback.message, perevod)
    elif callback.data == 'koment':
        bot.send_message(callback.message.chat.id, f'Пришлите фото, к кторому нужно придумать комментарий')
        bot.register_next_step_handler(callback.message, vauly)
    else:
        if callback.data == 'else':
            bot.send_message(callback.message.chat.id, 'Введите пару значений через слэш')
            bot.register_next_step_handler(callback.message, mycurrency)
        else:
            values = callback.data.upper().split('/')
            res = currency.convert(amount, values[0], values[1])
            bot.send_message(callback.message.chat.id, f'Получается: {round(res, 2)}')
            #bot.register_next_step_handler(callback.message, perevod)

def mycurrency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Получается: {round(res, 2)}')
        bot.register_next_step_handler(message, perevod)
    except Exception:
        bot.send_message(message.chat.id, f'Что-то не так, попробуйте ещё раз')
        bot.register_next_step_handler(message, mycurrency)

def perevod(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат, введите сумму.')
        bot.register_next_step_handler(message, perevod)
        return
    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn6 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn7 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn8 = types.InlineKeyboardButton('USD/CNY', callback_data='usd/cny')
        btn9 = types.InlineKeyboardButton('Другие валюты', callback_data='else')
        markup.add(btn6, btn7, btn8, btn9)
        bot.send_message(message.chat.id, 'Выберите пару валют', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Неверный формат, введите сумму.')
        bot.register_next_step_handler(message, perevod)



def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    data = json.loads(res.text)
    bot.reply_to(message, f'Сейчас погода: {data["main"]["temp"]}')


def vauly(message):
    bot.reply_to(message, f'{choice(comments)}')



@bot.message_handler()
def info(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Напиши /start, чтобы начать.')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')
    else:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Напиши /start, чтобы начать.')

bot.polling(non_stop=True)