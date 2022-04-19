from handlers.create_bot import bot
from keyboards import kb_client
from keyboards import kb_cancel
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base import sqlite_db
from handlers.create_bot import dp


class FSMAdmin(StatesGroup):
    user_id = State()
    month_number = State()
    day_number = State()
    event_description = State()


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


async def start_sending():
    await sqlite_db.to_send_command()


async def command_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, 'Привет! Я напоминатель событий.\nВыполняю такие команды:\n/Сегодня - посмотреть сегодняшние события\n/Список - посмотреть список всех событий\n/Добавить - добавить событие в список', reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС\nОбратитесь к боту здесь\nhttps://t.me/remind2022_bot')


async def now_date_command(message: types.Message):
    await sqlite_db.to_send_today(message.from_user.id)


async def date_list_command(message: types.Message):
    await sqlite_db.sql_read(message)


async def cm_start(message: types.Message, state: FSMContext):
    await FSMAdmin.user_id.set()
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
    await FSMAdmin.next()
    await message.answer('Введите месяц события', reply_markup=kb_cancel)


async def cansel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Добавление события отменено!', reply_markup=kb_client)


async def load_month_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if month_names(message.text.lower()) == '':
            await message.answer('Уточните номер или название месяца')
        else:
            data['month_number'] = month_names(message.text.lower())[1]
            await FSMAdmin.next()
            await message.answer('Какого числа в ' + month_names(message.text)[2] + ' событие?')


async def load_day_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        day_number = int(message.text)
        month = data['month_number']
        month_31 = ['января', 'марта', 'мая', 'июля', 'августа', 'октября', 'декабря']
        if month == 'февраля':
            if 0 < day_number < 30:
                data['day_number'] = day_number
                await FSMAdmin.next()
                await message.answer('Введите краткое описание события.')
            else:
                await message.answer(str(day_number) + ' ' + month + ' не существует!\nПожалуйста, уточните число.')
        if month in month_31:
            if 0 < day_number < 32:
                data['day_number'] = day_number
                await FSMAdmin.next()
                await message.answer('Введите краткое описание события.')
            else:
                await message.answer(str(day_number) + ' ' + month + ' не существует!\nПожалуйста, уточните число.')
        else:
            if 0 < day_number < 31:
                data['day_number'] = day_number
                await FSMAdmin.next()
                await message.answer('Введите краткое описание события.')
            else:
                await message.answer(str(day_number) + ' ' + month + ' не существует!\nПожалуйста, уточните число.')


async def load_event_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['event_description'] = message.text
    await sqlite_db.sql_add_command(state)
    await state.finish()
    await message.answer('Событие ' + data['event_description'] + ' добавлено!', reply_markup=kb_client)


@dp.callback_query_handler(Text(startswith='id_'))
async def del_callback_run(callback: types.CallbackQuery):
    await sqlite_db.sql_delete_command(int(callback.data.split('_')[1]))
    await bot.send_message(int(callback.data.split('_')[2]), 'Cобытие удалено')


async def echo_send(message: types.Message):
    await message.reply('Список доступных команд:\n/Сегодня - посмотреть сегодняшние события\n/Список - посмотреть список всех событий\n/Добавить - добавить событие в список')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    # dp.register_message_handler(cansel_handler, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(cansel_handler, commands=['отмена'], state="*")
    dp.register_message_handler(start_sending, commands=['sending'])
    dp.register_message_handler(now_date_command, commands=['сегодня'])
    dp.register_message_handler(date_list_command, commands=['список'])
    dp.register_message_handler(cm_start, commands=['добавить'], state=None)
    dp.register_message_handler(load_day_number, state=FSMAdmin.day_number)
    dp.register_message_handler(load_month_number, state=FSMAdmin.month_number)
    dp.register_message_handler(load_event_description, state=FSMAdmin.event_description)
    dp.register_message_handler(echo_send)
