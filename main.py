import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from config import config
import sqlite3
import aiosqlite


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(bot)


conn = sqlite3.connect('menu.db', check_same_thread=False)
cursor = conn.cursor()


@dp.message_handler(commands=['start'])
async def start_manager(message):
    cursor.execute('SELECT * FROM base WHERE id IS 1')
    text = cursor.fetchone()
    merged_buttons = text[4].split(',')
    sql_buttons = 'SELECT * FROM base WHERE is_button IS 1 AND id IN ({seq})'.format(seq=','.join(['?'] * len(merged_buttons)))
    cursor.execute(sql_buttons, merged_buttons)
    buttons = cursor.fetchall()
    keyboard = types.InlineKeyboardMarkup()
    for but in buttons:
        button = types.InlineKeyboardButton(text=but[2], callback_data=but[1])
        keyboard.add(button)
    await bot.send_message(message.chat.id, ''+str(text[2])+'', reply_markup=keyboard)


@dp.callback_query_handler()
async def bot_body(call):
    button = (call.data,)
    sql_search_buttons = 'SELECT * FROM base WHERE name=?'
    cursor.execute(sql_search_buttons, button)
    text = cursor.fetchone()
    # text = str(text).split(',')
    '''Выделяем следующий шаг'''
    next_step_id = text[4]
    '''Определяем следующее сообщение'''
    cursor.execute('SELECT * FROM base WHERE id=?', (next_step_id,))
    next_step = cursor.fetchone()
    '''Определяем кнопки'''
    merged_buttons = str(next_step[4]).split(',')
    chat_info = next_step[2]
    cursor.execute('SELECT * FROM base WHERE id IN ({seq})'.format(seq=','.join(['?'] * len(merged_buttons))), (merged_buttons))
    buttons = cursor.fetchall()
    keyboard = types.InlineKeyboardMarkup()
    for but in buttons:
        button = types.InlineKeyboardButton(text=but[2], callback_data=but[1])
        keyboard.add(button)
    await bot.edit_message_text(chat_id=call['from'].id, message_id=call.message.message_id, text=chat_info)
    await bot.edit_message_reply_markup(chat_id=call['from'].id, message_id=call.message.message_id, reply_markup=keyboard)


@dp.message_handler(commands=['test'])
async def cmd_test(message: types.Message):
    db = await aiosqlite.connect('menu.db')
    cursor = await db.execute('SELECT * FROM base')
    rows = await cursor.fetchall()
    await bot.send_message(chat_id=message.chat.id, text=rows)


@dp.message_handler()
async def text(message: types.Message):
    await message.answer(message.text)


async def main():
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
