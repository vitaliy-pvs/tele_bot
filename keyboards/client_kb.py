from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('/сегодня')
b2 = KeyboardButton('/список')
b3 = KeyboardButton('/добавить')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.row(b1, b2, b3)
