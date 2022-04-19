from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

button_cancel = KeyboardButton('/отмена')

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)
