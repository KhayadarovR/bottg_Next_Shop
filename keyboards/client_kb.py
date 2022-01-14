from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# menu
buy = KeyboardButton('/купить 💰')
sell = KeyboardButton('/продать 💸')
contact = KeyboardButton('/контакты 📞')
board = KeyboardButton('/объявления 📝')

car = KeyboardButton('1')
house = KeyboardButton('2')
business = KeyboardButton('3')

b_exit = KeyboardButton('меню 🏠')

p00 = KeyboardButton('0')
p0 = KeyboardButton('50 000')
p1 = KeyboardButton('100 000')
p2 = KeyboardButton('200 000')
p5 = KeyboardButton('500 000')
p10 = KeyboardButton('1 000 000')
p102 = KeyboardButton('10 000 000')
p103 = KeyboardButton('20 000 000')
p104 = KeyboardButton('50 000 000')

s1 = KeyboardButton('1')
s2 = KeyboardButton('2')
s3 = KeyboardButton('3')
s4 = KeyboardButton('4')
s5 = KeyboardButton('5')
s6 = KeyboardButton('6')
s7 = KeyboardButton('7')
s8 = KeyboardButton('8')
s9 = KeyboardButton('9')
s10 = KeyboardButton('10')


main_menu = ReplyKeyboardMarkup(resize_keyboard=True).insert(buy).insert(sell).add(contact).add(board).add(b_exit)

products = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).insert(car).insert(house).insert(business)\
    .add(b_exit)

kb_exit = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(b_exit)

kb_price = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).insert(p1).insert(p2)\
    .insert(p5).insert(p10).insert(p102).insert(p103).insert(p104).add(b_exit)


kb_minprice = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).insert(p00).insert(p0).insert(p1).insert(p2)\
    .insert(p5).insert(p10).insert(p102).insert(p103).insert(p104).add(b_exit)


kb_serv = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard= True).insert(s1).insert(s2).insert(s3).insert(s4)\
    .insert(s5).insert(s6).insert(s7).insert(s8).insert(s9).insert(s10)
