import sqlite3 as sq
from asyncio import sleep

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from import_help import dp, bot


def sql_start():
    global base, cursor
    base = sq.connect('warehouse.db')
    cursor = base.cursor()
    if base:
        print('Data base connected')
    base.execute('CREATE TABLE IF NOT EXISTS products('
                 'product INTEGER CHECK(product > 0 and product < 4)'
                 ', photo TEXT'
                 ', name TEXT'
                 ', descriptions TEXT'
                 ', serv INTEGER'
                 ', price INTEGER'
                 ', from_user TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS users ('
                 'user_id TEXT UNIQUE'
                 ', username TEXT'
                 ', contacts TEXT)')
    base.commit()


async def add_product(state):
    # cursor.execute(f'INSERT INTO products (from_user) VALUES({msg.from_user.id})')
    async with state.proxy() as data:
        print(f'add product:\n{tuple(data.values())}')
        cursor.execute('INSERT INTO products VALUES (?,?,?,?,?,?,?)', tuple(data.values()))
        base.commit()


async def add_contact(state):
    async with state.proxy() as data_contact:
        print(f'add contact:\n{tuple(data_contact.values())}')
        cursor.execute(f'UPDATE users SET contacts = ?, username = ? WHERE user_id = ?', tuple(data_contact.values()))
        base.commit()


async def add_idname(user):
    print(f'add userid username:\n{user}')
    cursor.execute(f'INSERT or IGNORE INTO users (user_id, username) VALUES (?,?)', user)
    print(f'add username: {user[1]}')
    cursor.execute(f'UPDATE users SET username = ? WHERE user_id = ?', (user[1], user[0],))
    base.commit()


async def read_products(msg, prod_type, p_min: int, p_max: int, serv: int):
    rows = (cursor.execute(f"SELECT * FROM products WHERE product=? and price>=? and price<=? and serv=?",
                           (prod_type, p_min, p_max, serv)).fetchall())
    print(f'find products:\n{rows}')
    if not rows:
        await bot.send_message(msg.from_user.id, 'По вашему запросу предложений не найдено🙁\n'
                                                 'Попробуйте изменить условия поиска')
    else:
        for ret in rows:
            il_contact = InlineKeyboardButton(text='👆Контакты продовца👆', callback_data=f'con_{ret[-1]}')
            ilkb_getcotact = InlineKeyboardMarkup().add(il_contact)
            await sleep(1)
            await bot.send_photo(msg.from_user.id, ret[1], f'{ret[2]}\n'
                                                           f'{ret[3]}\n'
                                                           f'💸 {ret[-2]:,} рублей', reply_markup=ilkb_getcotact)
            await sleep(1)


async def read_board(u_id: str):
    print(f'search board from user: {u_id}')
    rows_board = cursor.execute('SELECT rowid, * FROM products WHERE "from_user"=?', (u_id,)).fetchall()
    print(f'find board:\n{rows_board}')
    if not rows_board:
        print('Не найден продукт этого юзера')
    return rows_board


async def del_board(rowid: int):
    print(f'delete product: {rowid}')
    delete_product = cursor.execute('SELECT name FROM products WHERE rowid=?', (rowid,)).fetchone()
    cursor.execute('DELETE FROM products WHERE rowid=?', (rowid,))
    base.commit()
    if not delete_product:
        print('Не найден продукт под этим rowid')
    else:
        return delete_product


async def read_contact(user_id: str):
    print(f'search contact:\n{user_id}')
    rows_contact = cursor.execute('SELECT "contacts", "username" FROM users WHERE "user_id"=?', (user_id,)).fetchall()
    print(f'find contact:\n{rows_contact}')
    if not rows_contact:
        print('Не найден контакт')
    return rows_contact
