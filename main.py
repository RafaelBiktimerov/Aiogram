import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from config import config


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer_dice(emoji='🎲')


async def main():
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
