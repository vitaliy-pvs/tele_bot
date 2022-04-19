import sqlite3 as sq

from handlers.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime

month_list = [
        ['январь', 'января', 'январе', '1', '01'],
        ['февраль', 'февраля', 'феврале', '2', '02'],
        ['март', 'марта', 'марте', '3', '03'],
        ['апрель', 'апреля', 'апреле', '4', '04'],
        ['май', 'мая', 'мае', '5', '05'],
        ['июнь', 'июня', 'июне', '6', '06'],
        ['июль', 'июля', 'июле', '7', '07'],
        ['август', 'августа', 'августе', '8', '08'],
        ['сентябрь', 'сентября', 'сентябре', '9', '09'],
        ['октябрь', 'октября', 'октябре', '10'],
        ['ноябрь', 'ноября', 'ноябре', '11'],
        ['декабрь', 'декабря', 'декабре', '12']
    ]


def month_names(month_number_string):
    for month in month_list:
        if month_number_string in month:
            return month
    return ''


def sql_start():
    global base, cur
    base = sq.connect('user_events.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS user_events(id INTEGER PRIMARY KEY, user_id TEXT, month_number TEXT, day_number TEXT, event_description TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO user_events (user_id, month_number, day_number, event_description) VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_delete_command(data):
    cur.execute('DELETE FROM user_events WHERE id == ?', (data,))
    base.commit()


async def sql_read(message):
    i = 1
    for ret in cur.execute('SELECT * FROM user_events WHERE user_id == ?', (message.from_user.id,)).fetchall():
        await bot.send_message(message.from_user.id, str(i) + ') ' + str(ret[3]) + ' ' + str(ret[2]) + ': ' + str(ret[4]), reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text='Удалить', callback_data='id_' + str(ret[0]) + '_' + str(message.from_user.id))))
        i += 1
    if i == 1:
        await bot.send_message(message.from_user.id, 'В Вашем списке нет ни одного события')


async def to_send_command():
    for ret in cur.execute('SELECT * FROM user_events WHERE month_number == ? AND day_number == ?', (month_names(str(datetime.date.today().month))[1], str(datetime.date.today().day))).fetchall():
        await bot.send_message(int(ret[1]), 'Сегодня ' + str(ret[3]) + ' ' + str(ret[2]) + ' ' + str(ret[4]))

    for ret in cur.execute('SELECT * FROM user_events WHERE month_number == ? AND day_number == ?', (month_names(str((datetime.date.today() + datetime.timedelta(days=2)).month))[1], str((datetime.date.today() + datetime.timedelta(days=2)).day))).fetchall():
        await bot.send_message(int(ret[1]), 'Послезавтра ' + str(ret[3]) + ' ' + str(ret[2]) + ' ' + str(ret[4]))


async def to_send_today(from_user_id):
    flag = True
    for ret in cur.execute('SELECT * FROM user_events WHERE user_id == ? AND month_number == ? AND day_number == ?', (from_user_id, month_names(str(datetime.date.today().month))[1], str(datetime.date.today().day))).fetchall():
        await bot.send_message(int(from_user_id), 'Сегодня ' + str(ret[3]) + ' ' + str(ret[2]) + ' ' + str(ret[4]))
        flag = False
    if flag:
        await bot.send_message(int(from_user_id), 'Сегодня нет событий')
