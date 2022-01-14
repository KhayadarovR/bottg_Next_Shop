from asyncio import sleep

from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base import sqlite_db
from import_help import dp, bot


class FSMadd(StatesGroup):
    product = State()
    photo = State()
    name = State()
    descriptions = State()
    serv = State()
    price = State()
    from_user = State()


class FSMread(StatesGroup):
    prod_type = State()
    p_max = State()
    p_min = State()
    serv = State()


class FSMget(StatesGroup):
    username = State()
    contact = State()


"""****************************** АНТИФЛУД ***************************"""


async def anti_flood(*args, **kwargs):
    m = args[0]
    try:
        await m.answer("Пообещай не флудить и нажми /menu", reply_markup=types.ReplyKeyboardRemove())
    except:
        await m.answer("Будешь флудить - я начну игнорировать:)")
    await sleep(2)


"""*****************Обновить базу если чел изминил юзернейм************* ОТВЕТЫ НА СТАРТ И МЕНЮ***************************"""



# @dp.message_handler()
@dp.throttled(anti_flood, rate=3)
async def start_menu(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer(f'👋 Я бот который поможет тебе продать или купить вещи из игры NextRP!\nНажми *меню*,'
                     f' что бы ознакомиться с моими командами, используй кнопки снизу👇',
                     reply_markup=main_menu, parse_mode=types.ParseMode.MARKDOWN)
    u_name = msg.from_user.username
    user = (str(msg.from_user.id), str(u_name))
    await sqlite_db.add_idname(user)


@dp.throttled(anti_flood, rate=2)
async def exit(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer('Ok, забыли всё! Вы в меню 🏠\n\n'
                     '*/купить* -  найти товары которые выставили на продажу\n'
                     '*/продать* - выставить свой товар для продажи\n'
                     '*/контакты* - установить свои контакты для покупателей\n'
                     '*/объявления* - посмотреть свои объявления на продажу\n'
                     '*/меню* - отмена последних действий и выход в меню',
                     reply_markup=main_menu, parse_mode=types.ParseMode.MARKDOWN)


"""****************************** МАШИНА СОСТОЯНИЙ ДЛЯ ВЫСТАВКИ СВОЕГО ТОВАРА***************************"""


@dp.throttled(anti_flood, rate=3)
async def start_sell(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    user_contact = await sqlite_db.read_contact(str(user_id))
    if (user_contact[0])[1] is None or (user_contact[0])[0] is None or msg.from_user.username is None:
        await msg.answer('❗Вы не можете выставить товар, пока не заполнили свои контакты\n'
                         'Нажмите */контакты* и заполните его, что бы покупатели смогли связаться с вами',
                         parse_mode=types.ParseMode.MARKDOWN)
    else:
        await msg.answer('Выберите категорию товара\n'
                         '\n1 - 🚗 Транспорт\n'
                         '\n2 - 🏘 Недвижемость\n'
                         '\n3 - 💰 Бизнес', reply_markup=products)
        await FSMadd.product.set()


async def chose_product(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['product'] = msg.text
    await msg.answer('Отправте фото вашего товара', reply_markup=kb_exit)
    await FSMadd.next()


async def set_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = msg.photo[0].file_id
    await msg.answer('Напишите название вашего товара')
    await FSMadd.next()


async def set_name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text
    await msg.answer('Отправте описание вашего товара')
    await FSMadd.next()


async def set_descriptions(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['descriptions'] = msg.text
    await msg.answer('Выберите сервер на котором хотите ПРОДАТЬ этот товар:'
                     '\n1 - Cоветский⚒'
                     '\n2 - Балтийский⛵'
                     '\n3 - Кавказский🗻'
                     '\n4 - Центральный👑'
                     '\n5 - Сибрский❄'
                     '\n6 - Приморский🌊'
                     '\n7 - Краснодарский🏦'
                     '\n8 - Южный🏝'
                     '\n9 - Уральский🧢'
                     '\n10 - Алтайский🏞', reply_markup=kb_serv)
    await FSMadd.next()


async def set_serv(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            data['serv'] = int(msg.text)
            await msg.answer('Напишите или выберите цену товара\n(например: 1 285 000 или 125000)',
                             reply_markup=kb_price)
            await FSMadd.next()
        except:
            await msg.answer('Выберите или напишите число от 1 до 10, в соответсвии с вашим сервером!')
            await FSMadd.serv.set()


async def set_price_finish(msg: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['price'] = int(msg.text.replace(' ', ''))
            data['from_user'] = str(msg.from_user.id)
            answer = (tuple(data.values()))
        await bot.send_photo(msg.from_user.id, answer[1], f'*Тип*: {answer[0]}\n'
                                                          f'*Название:* {answer[2]}\n'
                                                          f'*Описание:* {answer[3]}\n'
                                                          f'*Цена:* {answer[-2]:,}',
                             parse_mode=types.ParseMode.MARKDOWN)
        await sqlite_db.add_product(state)
        await msg.answer('✔ Сохранил ваш товар в базу...\n⏰Ждите покупателей которые заинтересуются вашим товаром',
                         reply_markup=main_menu)
        await state.finish()
    except:
        await msg.answer('❌Не смог сохранить ваш товар! Вы как то умудрились ошибиться даже тут🤦‍♂️'
                         '\n\nНажмите продать и заполните заного😊', reply_markup=main_menu)
        await state.finish()


"""****************************** МАШИНА СОСТОЯНИЙ ДЛЯ СБОРА УСЛОВИЙ ПОИСКА***************************"""


@dp.throttled(anti_flood, rate=3)
async def start_buy(msg: types.Message):
    await msg.answer('Выберите категорию товара\n'
                     '\n1 - 🚗 Транспорт\n'
                     '\n2 - 🏘 Недвижемость\n'
                     '\n3 - 💰 Бизнес', reply_markup=products)
    await FSMread.prod_type.set()


async def set_prodtype(msg: types.Message, state: FSMContext):
    async with state.proxy() as search_data:
        search_data['prod_type'] = msg.text
    await msg.answer('Напиши или выбири МАКСИМАЛЬНУЮ цену:', reply_markup=kb_price)
    await FSMread.next()


async def set_pmax(msg: types.Message, state: FSMContext):
    try:
        async with state.proxy() as search_data:
            search_data['p_max'] = int(msg.text.replace(' ', ''))
        await msg.answer('Выбери МИНИМАЛЬНУЮ цену:', reply_markup=kb_minprice)
        await FSMread.next()
    except:
        await msg.answer(
            'Напишите\выбери корректное значение!\nНапример 50 000 или 200000\nНЕ используйте буквы/запятые/точки')
        await FSMread.p_max.set()


async def set_pmin(msg: types.Message, state: FSMContext):
    try:
        async with state.proxy() as search_data:
            search_data['p_min'] = int(msg.text.replace(' ', ''))
        await msg.answer('Выберите сервер на котором хотите КУПИТЬ этот товар:'
                         '\n1 - Cоветский⚒'
                         '\n2 - Балтийский⛵'
                         '\n3 - Кавказский🗻'
                         '\n4 - Центральный👑'
                         '\n5 - Сибрский❄'
                         '\n6 - Приморский🌊'
                         '\n7 - Краснодарский🏦'
                         '\n8 - Южный🏝'
                         '\n9 - Уральский🧢'
                         '\n10 - Алтайский🏞', reply_markup=kb_serv)
        await FSMread.next()
    except:
        await msg.answer(
            'Напишите\выбери корректное значение!\nНапример 50 000 или 200000\nНЕ используйте буквы/запятые/точки')
        await FSMread.p_min.set()


async def set_readserv(msg: types.Message, state: FSMContext):
    try:
        async with state.proxy() as search_data:
            search_data['serv'] = int(msg.text.replace(' ', ''))
            conditions = tuple(search_data.values())
        await msg.answer(f'*Условия поиска*\n\nТип: {conditions[0]}\nЦена с {conditions[2]:,} до {conditions[1]:,}'
                         f'\nСервер: {conditions[-1]}', reply_markup=main_menu, parse_mode=types.ParseMode.MARKDOWN)
        await sqlite_db.read_products(msg, conditions[0], int(conditions[2]), int(conditions[1]), int(conditions[-1]))
        await state.finish()
    except:
        await msg.answer('Выберите или напишите число от 1 до 10, в соответсвие с вашим сервером!')
        await FSMread.serv.set()


"""****************************** МАШИНА СОСТОЯНИЙ ДЛЯ СБОРА КОНТАКТОВ ПОЛЬЗОВАТЕЛЯ ***************************"""


@dp.throttled(anti_flood, rate=5)
async def start_getcontact(msg: types.Message):
    user_id = msg.from_user.id
    user_contact = await sqlite_db.read_contact(str(user_id))
    if not user_contact:
        await msg.answer('Контакты не найдены', reply_markup=main_menu)
    await bot.send_message(msg.from_user.id, f'Ваши контакты на данный момент\n\n'
                                             f'*Telegram:* @{(user_contact[0])[1]}\n*Контакты:*\n'
                                             f'{(user_contact[0])[0]}', parse_mode=types.ParseMode.MARKDOWN)

    if msg.from_user.username is None:
        await msg.answer(
            "1️⃣‼Установите свой @username в настроках профиля в телеграмме, после заполнения отправте /start\n\n"
            "Нажмите */меню* что бы выйти", parse_mode=types.ParseMode.MARKDOWN, reply_markup=kb_exit)
    else:
        await msg.answer(
            '*Отправте ваши контакты для потенциального покупателя, что бы они смогли свзяаться с вами*\n\n'
            'Например игровой телефонный номер, ваш ник, свой discord, ссылка на страницу вк, когда '
            'выходите в онлайн и т.д\n\nНажмите *меню* что бы выйти (текущие контакты сохраняться)',
            parse_mode=types.ParseMode.MARKDOWN, reply_markup=kb_exit)
        await FSMget.contact.set()


async def set_contact(msg: types.Message, state: FSMContext):
    async with state.proxy() as contact_data:
        contact_data['contact'] = msg.text
        contact_data['u_name'] = msg.from_user.username
        contact_data['u_id'] = str(msg.from_user.id)
        user_tg = contact_data['u_name']
    await sqlite_db.add_contact(state)
    await msg.answer(f'Ваши контакты:\n\n*Telegram:* @{user_tg}\n*Связь с вами:*\n{msg.text}',
                     parse_mode=types.ParseMode.MARKDOWN)
    await msg.answer('✅Сохранил...', reply_markup=main_menu)
    await state.finish()


"""****************************** ОБРОБОТКА CALLBACK ПОЛУЧЕНИЕ КОНТАКТА ПРОДАВЦА ***************************"""


@dp.throttled(anti_flood, rate=3)
async def give_contact(call_query: types.CallbackQuery):
    user_id = call_query.data.split('_')
    user_contact = await sqlite_db.read_contact(str(user_id[1]))
    if not user_contact:
        bot.send_message(call_query.from_user.id, 'Контакты НЕ найдены', reply_markup=main_menu)
    else:
        await bot.send_message(call_query.from_user.id, f'*Telegram продовца:* @{(user_contact[0])[1]}\n*Контакты:*\n'
                                                        f'{(user_contact[0])[0]}', parse_mode=types.ParseMode.MARKDOWN)
        await call_query.answer(f'Отправил контакты продавца!')


"""****************************** ОТПРАВКА CALLBACK НА УДАЛЕНИЕ ОБЪЯВЛЕНИЯ ***************************"""


@dp.throttled(anti_flood, rate=5)
async def see_board(msg: types.Message):
    await msg.answer('⏳Ищу ваши объявления о продаже... _среди кучи хлама_', parse_mode=types.ParseMode.MARKDOWN)
    user_id = msg.from_user.id
    rows = await sqlite_db.read_board(str(user_id))
    if not rows:
        await msg.answer('Ваших объявлений о продаже в базе не найдено, '
                         'но вы можете прямо сейчас добавить его, нажав */продать*',
                         reply_markup=main_menu, parse_mode=types.ParseMode.MARKDOWN)
    else:
        for ret in rows:
            il_contact = InlineKeyboardButton(text='👆❌Удалить объявление❌👆', callback_data=f'boarddelete_{ret[0]}')
            print(f'send rowid for delete: {il_contact.callback_data}')
            delete_user_board = InlineKeyboardMarkup().add(il_contact)
            await bot.send_photo(msg.from_user.id, ret[2], f"*Категория:* {ret[1]}\n"
                                                           f"*Название:* {ret[3]}\n"
                                                           f"*Описание:* {ret[4]}\n"
                                                           f"*Сервер:* {ret[5]}\n"
                                                           f"*Цена:* {ret[6]:,}\n",
                                 parse_mode=types.ParseMode.MARKDOWN, reply_markup=delete_user_board)
            await sleep(3)


"""****************************** ОБРОБОТКА CALLBACK НА УДАЛЕНИЕ ОБЪЯВЛЕНИЯ ***************************"""


@dp.throttled(anti_flood, rate=3)
async def delete_board(call_query: types.CallbackQuery):
    boards_rowid = call_query.data.split('_')
    delete_name = await sqlite_db.del_board(int(boards_rowid[1]))
    await call_query.answer(f'{delete_name[0]} удалён!')


"""****************************** РЕГИСТРАЦИЯ ФУНКЦИЙ *************************************"""


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_menu, commands=['start', 'help'], state='*')
    dp.register_message_handler(exit, state='*', commands=['exit', 'menu'])
    dp.register_message_handler(exit, Text(startswith=['выход', 'меню']), state='*')
    dp.register_message_handler(start_sell, state=None, commands=['продать'])
    dp.register_message_handler(start_buy, state=None, commands=['купить'])
    dp.register_message_handler(see_board, state=None, commands=['объявления'])
    dp.register_message_handler(start_getcontact, state=None, commands=['контакты'])
    dp.register_message_handler(chose_product, state=FSMadd.product)
    dp.register_message_handler(set_photo, content_types='photo', state=FSMadd.photo)
    dp.register_message_handler(set_name, state=FSMadd.name)
    dp.register_message_handler(set_descriptions, state=FSMadd.descriptions)
    dp.register_message_handler(set_serv, state=FSMadd.serv)
    dp.register_message_handler(set_price_finish, state=FSMadd.price)
    dp.register_message_handler(set_prodtype, state=FSMread.prod_type)
    dp.register_message_handler(set_pmax, state=FSMread.p_max)
    dp.register_message_handler(set_pmin, state=FSMread.p_min)
    dp.register_message_handler(set_readserv, state=FSMread.serv)
    dp.register_message_handler(set_contact, state=FSMget.contact)
    dp.register_callback_query_handler(give_contact, Text(startswith='con_'))
    dp.register_callback_query_handler(delete_board, Text(startswith='boarddelete_'))
