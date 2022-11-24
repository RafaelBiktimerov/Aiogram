import datetime

import telebot
import sqlite3
# import datetime
from config import API
from config import db
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

bot = telebot.TeleBot(API, parse_mode='MarkDown')
conn = sqlite3.connect(db, check_same_thread=False)
cursor = conn.cursor()
conn.row_factory = sqlite3.Row
admin = '1145160788'
admin2 = ['Avazvildan', 'rzoek']
sell_list = []


'''Запуск бота'''


@bot.message_handler(commands=['start'], func=lambda message: str(message.from_user.username) in admin2)
def start_manager(message):
    cursor.execute('SELECT * FROM base WHERE id IS 1')
    text = cursor.fetchone()
    print(text)
    merged_buttons = text[4].split(',')
    sql_buttons = 'SELECT * FROM base WHERE is_button IS 1 AND id IN ({seq})'.format(seq=','.join(['?'] * len(merged_buttons)))
    cursor.execute(sql_buttons, merged_buttons)
    buttons = cursor.fetchall()
    keyboard = types.InlineKeyboardMarkup()
    for but in buttons:
        button = types.InlineKeyboardButton(text=but[2], callback_data=but[1])
        keyboard.add(button)
    bot.send_message(message.chat.id, ''+str(text[2])+'', reply_markup=keyboard)


'''Проверка остатков'''


@bot.message_handler(commands=['ost'], func=lambda message: str(message.from_user.username) in admin2)
def send_ost(message):
    cursor.execute('SELECT * FROM assortment')
    text = cursor.fetchall()
    mess = ''
    for item in text:
        mess = mess + '\n' + str(item[2]) + ' ' + str(item[3]) + ' ' + str(item[4]) + ' кг' + ': ' + str(item[6]) + ''
    bot.send_message(chat_id=message.chat.id, text=str(mess))


'''Скоро будет. Добавление новых товаров'''


@bot.callback_query_handler(func=lambda call: call.data.startswith('add'))
def add(call):
    print(call.data)
    my_name = call.data[4:]
    print(my_name)
    cursor.execute('SELECT my_name, count, pet, property, weight FROM assortment WHERE my_name = ?', (my_name,))
    text = cursor.fetchone()
    buttons = cursor.fetchall()
    print(text)
    new_count = text[1]+1
    print(text[1])
    print(new_count)
    sucsess_text = 'Добавлено: '
    error_text = 'Добавить не смог'
    try:
        sqlite_insert_query_addings = """INSERT INTO table_of_addings
                              (date, my_name, count)
                              VALUES
                              (?, ?, ?);"""
        count = cursor.execute(sqlite_insert_query_addings, (datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'), my_name, 1))
        sqlite_insert_query_assortment = 'UPDATE assortment SET count = ? WHERE my_name = ?'
        update_assortment = cursor.execute(sqlite_insert_query_assortment, (new_count, text[0]))
        conn.commit()
        keyboard = types.InlineKeyboardMarkup()
        for but in buttons:
            button = types.InlineKeyboardButton(text=str(but[2]) + ' ' + str(but[3]) + ' ' + str(but[4])+'кг'+': '+str(but[6])+'шт.', callback_data='add_' + str(but[0]))
            keyboard.add(button)
        bot.answer_callback_query(call.id, text=sucsess_text+str(text[2])+' '+str(text[3])+' '+str(text[4])+'кг'+'\n'+'Итого '+str(new_count)+' штук')
    except sqlite3.Error as error:
        # print("Ошибка при работе с SQLite", error)
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Главное меню', callback_data='top_menu')
        keyboard.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=error_text)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)


# @bot.callback_query_handler(func=lambda call:call.data('day'))
# def day(call):
#     time = datetime.datetime.now()
#     time1 = '16.08.2022 00:15:38'
#     if time >time1:
#         bot.reply_to(call, 'больше')
#     else:
#         bot.reply_to(call, 'меньше')
#     # cursor.execute('SELECT * FROM table_of_sales WHERE date > ?', time-)

'''Скоро будет. Отчет о продажах'''


@bot.message_handler(commands=['report'], func=lambda message: str(message.from_user.username) in admin2)
def report(message):
    buttons = [('День', 'day'), ('Неделя', 'week'), ('Месяц', 'month')]
    keyboard = types.InlineKeyboardMarkup()
    for but in buttons:
        button = types.InlineKeyboardButton(text=but[0], callback_data=but[1])
        keyboard.add(button)
    bot.send_message(message.chat.id, 'Выбери продолжительность отчета', reply_markup=keyboard)


'''Пополнение запасов магазина'''


@bot.message_handler(commands=['tovar'], func=lambda message: str(message.from_user.username) in admin2)
def add(message):
    cursor.execute('SELECT * FROM assortment')
    buttons = cursor.fetchall()
    print(buttons)
    keyboard = types.InlineKeyboardMarkup()
    for but in buttons:
        button = types.InlineKeyboardButton(text=str(but[2]) + ' ' + str(but[3]) + ' ' + str(but[4])+'кг'+': '+str(but[6])+'шт.', callback_data= 'add_' + str(but[1]))
        keyboard.add(button)
    bot.send_message(message.chat.id, 'Выбери', reply_markup=keyboard)


'''Процесс продажи'''

'''Продажа'''
@bot.callback_query_handler(func=lambda call: call.data.startswith('cash'))
def manager(call):
    call_data = call.data
    print('call data: '+call_data)
    text_without_cash = call_data.partition('_')
    print('partition 1: '+str(text_without_cash))
    payment = text_without_cash[0]
    if payment == 'cashpay':
        payment = 1
    else:
        payment = 0
    print('payment: '+str(payment))
    text_with_manager = text_without_cash[2].replace('manager','')
    print('text_with_manager '+text_with_manager)
    sell_partition = text_with_manager.partition('_')
    print('sell_partition: '+str(sell_partition))
    sell_text = sell_partition[2]
    print('sell_text: '+sell_text)
    seller = sell_partition[0]
    print('seller: '+seller)
    my_name = sell_text[5:]
    print('my_name: '+my_name)
    cursor.execute('SELECT pet, property, weight, price, count, id FROM assortment WHERE my_name = ?', (my_name,))
    text = cursor.fetchone()
    print('text: '+str(text))
    new_count = text[4] - 1
    print(new_count)
    print(text[0])
    print(text[1])
    print(text[2])
    print(text[3])
    print(seller)
    print(payment)
    print(my_name)
    sucsess_text = 'Продано: '+str(text[0])+' '+str(text[1])+' '+str(text[2])+'кг'
    error_text = 'Продажа не прошла. Повтори операцию'
    try:
        sqlite_insert_query = """INSERT INTO table_of_sales
                              (date, pet, property, weight, price, manager, cash, my_name)
                              VALUES
                              (?, ?, ?, ?, ?, ?, ?, ?);"""
        count = cursor.execute(sqlite_insert_query, (datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'), text[0], text[1], text[2], text[3], seller, payment, my_name))
        sqlite_update = 'UPDATE assortment SET count = ? where id = ?'
        update_assortment = cursor.execute(sqlite_update, (new_count, text[5]))
        conn.commit()
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Главное меню', callback_data='top_menu')
        keyboard.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=sucsess_text)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)
    except sqlite3.Error as error:
        print(error)
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Главное меню', callback_data='top_menu')
        keyboard.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=error_text)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)


'''Выбор способа оплаты'''
@bot.callback_query_handler(func=lambda call: call.data.startswith('manager'))
def cash(call):
    types_of_payment = [('cashpay', 'Наличные'), ('cashless', 'Безналом')]
    keyboard = types.InlineKeyboardMarkup()
    chat_info = 'Как оплачивает клиент?'
    for payment in types_of_payment:
        button = types.InlineKeyboardButton(text=payment[1], callback_data=payment[0]+'_'+call.data)
        keyboard.add(button)
    button = types.InlineKeyboardButton(text='Главное меню', callback_data='top_menu')
    keyboard.add(button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=chat_info)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)


# '''Набор товаров в список'''
# @bot.callback_query_handler(func=lambda call: call.data.startswith('sell'))
# def collect(call):
#     call_data = call.data
#     keyboard = types.InlineKeyboardMarkup()
#     product_name = call_data.partition('_')
#     sell_list.append(product_name[2])
#     print(sell_list[0])
#     button = types.InlineKeyboardButton(text='Главное меню', callback_data='top_menu')
#     keyboard.add(button)
#     mess = ''
#     for item in sell_list:
#         mess = mess + '\n' + item + ''
#     bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess)
#     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)


'''Выбор продавца'''
@bot.callback_query_handler(func=lambda call: call.data.startswith('sell'))
def sell(call):
    text = call.data[5:]
    cursor.execute('SELECT * FROM managers')
    managers = cursor.fetchall()
    keyboard = types.InlineKeyboardMarkup()
    chat_info = 'Выбери продавца'
    for seller in managers:
        button = types.InlineKeyboardButton(text=seller[2], callback_data='manager'+seller[1]+'_'+call.data)
        keyboard.add(button)
    button = types.InlineKeyboardButton(text='Главное меню', callback_data='top_menu')
    keyboard.add(button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=chat_info)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)




'''Здесь будет отрисовка календаря'''
@bot.message_handler(commands=['cal'])
def start(m):
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(m.chat.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar(locale='ru').process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              c.message.chat.id,
                              c.message.message_id)


# '''Здесь будет запрос в SQL для создания отчета'''
# @bot.callback_query_handler(func=lambda call: call.data.startswith('2'))
# def report(call):




@bot.callback_query_handler(func=lambda call: True)
def bot_body(call):
    button = (call.data,)
    sql_search_buttons = 'SELECT * FROM base WHERE name=?'
    cursor.execute(sql_search_buttons, button)
    text = cursor.fetchone()
    '''Выделяем следующий шаг'''
    next_step_id = text[4]
    '''Определяем следующее сообщение'''
    cursor.execute('SELECT * FROM base WHERE id=?', (next_step_id,))
    next_step = cursor.fetchone()
    '''Определяем кнопки'''
    # print(next_step)
    merged_buttons = str(next_step[4]).split(',')
    chat_info = next_step[2]
    cursor.execute('SELECT * FROM base WHERE id IN ({seq})'.format(seq=','.join(['?'] * len(merged_buttons))), (merged_buttons))
    buttons = cursor.fetchall()
    keyboard = types.InlineKeyboardMarkup()
    for but in buttons:
        button = types.InlineKeyboardButton(text=but[2], callback_data=but[1])
        keyboard.add(button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=chat_info)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)


bot.infinity_polling()
