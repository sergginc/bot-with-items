import telebot
import sqlite3
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
TOKEN = ''
bot = telebot.TeleBot(TOKEN)
# ABOVE - BOT LIFE / DO NOT EDIT 

def init_db(): # create database
    conn = sqlite3.connect("menubase.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            type INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name INTEGER NOT NULL,
            describe TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

##### ---Functions for DB--- #####
def add_menu(name, describe): # add new item at menu
    conn = sqlite3.connect("menubase.db",detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO menu (name, describe) VALUES (?, ?)""", (name, describe))
    conn.commit()
    conn.close()

def get_menu_by_id(id): # get item by ID
    conn = sqlite3.connect("menubase.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""SELECT name, describe FROM menu WHERE id = ?""", (id,))
    info = cursor.fetchone()
    conn.close()
    return info

def get_menu_by_name(name): # get item(-s) by name
    conn = sqlite3.connect("menubase.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""SELECT id, name FROM menu WHERE LOWER(name) LIKE LOWER(?)""", (f'%{name}%',))
    info = cursor.fetchall()
    conn.close()
    return info

def get_all_menu(): # get all items
    conn = sqlite3.connect("menubase.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""SELECT id, name FROM menu""")
    all_menu = cursor.fetchall()
    conn.close()
    return all_menu

def delete_menu(id): # delete item by ID
    conn = sqlite3.connect("menubase.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def edit_menu(id,name,describe): # update item
    conn = sqlite3.connect("menubase.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("UPDATE menu SET name=?, describe=? WHERE id = ?", (name, describe, id,))
    conn.commit()
    conn.close()

def add_user(user_id): # add new user to DB
    conn = sqlite3.connect("menubase.db",timeout=10, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""INSERT OR IGNORE INTO users (user_id) VALUES (?)""", (user_id,))
    conn.commit()
    conn.close()

def is_admin(user_id): # check admin
    conn = sqlite3.connect("menubase.db",timeout=10,detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""SELECT user_id, type FROM users WHERE user_id = ?""", (user_id,))
    info = cursor.fetchone()
    conn.close()
    try:
      if info[1] != 1:
        bot.send_message(user_id, "❗ Нет админ прав!")
        bot.send_message(user_id,f"🍉 Добро пожаловать в меню!\n🔎 Выберите или введите название изделия.", reply_markup=menu_board(0))
        return False
    except:
        bot.send_message(user_id, "❗ Нет админ прав!")
        bot.send_message(user_id,f"🍉 Добро пожаловать в меню!\n🔎 Выберите или введите название изделия.", reply_markup=menu_board(0))
        return False
    return True


def set_admin(user_id): # set admin
    conn = sqlite3.connect("menubase.db",detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""UPDATE users SET type = ? WHERE user_id = ?""", (1,user_id))
    conn.commit()
    conn.close()
    print("админ добавлен")

def remove_admin(user_id): # remove admin
    conn = sqlite3.connect("menubase.db",detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = conn.cursor()
    cursor.execute("""UPDATE users SET type = ? WHERE user_id = ?""", (0,user_id))
    conn.commit()
    conn.close()
    print("админ удален")

###### ---BUTTONS--- ######

items = 5 # items on one page (for list of items)

def menu_board(page=0): # button to choose item in list
    menu = get_all_menu()
    keyboard = InlineKeyboardMarkup()
    start = page * items
    end = start + items

    for item_id, name in menu[start:end]: keyboard.add(InlineKeyboardButton(text=name,callback_data=f"item_{item_id}"))

    nav = []
    if page > 0: nav.append(InlineKeyboardButton("◀️ Назад",callback_data=f"page_{page-1}"))
    if end < len(menu): nav.append(InlineKeyboardButton("▶️ Вперед",callback_data=f"page_{page+1}"))
    if nav: keyboard.row(*nav)

    return keyboard

###### ---FUNCTIONS BUTTONS--- ######

### next - for users

@bot.callback_query_handler(func=lambda c: c.data.startswith("page_"))
def page(call): # logic of pages with items
    page = int(call.data.split("_")[1])
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=menu_board(page))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("item_"))
def item(call): # logic of choosen item   ("!1")
    item_id = int(call.data.split("_")[1])
    name, describe = get_menu_by_id(item_id)
    if is_admin(call.message.chat.id): # if admin - add buttons of admin events
      keyboard = InlineKeyboardMarkup()
      keyboard.row(InlineKeyboardButton(text="📝 Изменить изделие",callback_data=f"admin_edit_{item_id}"), InlineKeyboardButton(text="🗑️ Удалить изделие",callback_data=f"admin_delete_{item_id}")) 
      keyboard.add(InlineKeyboardButton(text="↩️ Выйти",callback_data="back"))
      bot.edit_message_text(text=f"<b>{name}</b>\n<blockquote>{describe}</blockquote>", parse_mode="HTML",chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
    else: # if not admin
      keyboard = InlineKeyboardMarkup()
      keyboard.add(InlineKeyboardButton(text="↩️ Выйти",callback_data="back"))
      bot.edit_message_text(text=f"<b>{name}</b>\n<blockquote>{describe}</blockquote>", parse_mode="HTML",chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call): # logic of back button on choosen item
    bot.edit_message_text(text=f"🍉 Добро пожаловать в меню!\n🔎 Выберите или введите название изделия.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=menu_board(0))
    bot.answer_callback_query(call.id)



###### --MAIN FUNC-- ######

@bot.message_handler(commands=['start'])
def start(message): # main menu
    bot.send_message(message.chat.id,f"🍉 Добро пожаловать в меню!\n🔎 Выберите или введите название изделия.\n> ver: 1.1", reply_markup=menu_board(0))
    add_user(message.chat.id)
    # set_admin(-1)
    # remove_admin(-1)

@bot.message_handler(func=lambda message: not message.text.startswith("/"))
def search(message): # search item by name (may be a piece of the name)
    items = get_menu_by_name(message.text)
    if not items:
      bot.send_message(message.chat.id, f"⚠️ По запросу <b>{message.text}</b> совпадений не найдено! Попробуйте ещё раз", parse_mode="HTML")
      bot.send_message(message.chat.id,f"🍉 Добро пожаловать в меню!\n🔎 Выберите или введите название изделия.", reply_markup=menu_board(0))
      return
    keyboard = InlineKeyboardMarkup()
    for item_id, name in items: keyboard.add(InlineKeyboardButton(text=name,callback_data=f"item_{item_id}"))
    bot.send_message(message.chat.id, f"Найдено {len(items)} совпадений:", reply_markup=keyboard)

@bot.message_handler(commands=['add'])
def add(message): # admins: add new item (step 1 - read /add command)
    if is_admin(message.chat.id):
      bot.send_message(message.chat.id,f"📝 Введите название:")
      bot.register_next_step_handler(message, get_name)

def get_name(message): # admins: add new item (step 2 - get name for item by message)
    bot.send_message(message.chat.id,f"📝 Введите описание:")
    bot.register_next_step_handler(message, get_describe, message.text) # message.text - name

def get_describe(message,name): # admins: add new item (step 3 - get describe for item by message and add item to DB)
    if is_admin(message.chat.id):
      describe = message.text
      add_menu(name,describe)
      bot.send_message(message.chat.id,f"🎉 Изделие успешно добавлено!\n\n<b>{name}</b>\n<blockquote>{describe}</blockquote>", parse_mode="HTML")
      bot.send_message(message.chat.id,f"🍉 Добро пожаловать в меню!\n🔎 Выберите или введите название изделия.", reply_markup=menu_board(0))


### admin functional

@bot.callback_query_handler(func=lambda c: c.data == "admin_add")
def admin_add(call): # logic of adding new item - get name
    if is_admin(call.message.chat.id):
      bot.answer_callback_query(call.id, "❗ Нет админ прав!")
      return
    bot.send_message(call.message.chat.id, "📝 Введите название:")
    bot.register_next_step_handler(call.message, get_name)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_delete_"))
def delete_item(call): # logic of delete choosen item after choose DELETE button
    if is_admin(call.message.chat.id):
      item_id = int(call.data.split("_")[2])
      keyboard = InlineKeyboardMarkup()
      keyboard.add(InlineKeyboardButton("🗑️ Удалить", callback_data=f"confirm_delete_{item_id}"))
      keyboard.add(InlineKeyboardButton("↩️ Назад", callback_data=f"item_{item_id}"))

      name, describe = get_menu_by_id(item_id)
      bot.edit_message_text(f"<b>{name}</b>\n<blockquote>{describe}</blockquote>\n\nУдалить?", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode="HTML")
      bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_delete_"))
def confirm_delete(call): # logic of delete choosen item after confirm deleting
    if is_admin(call.message.chat.id):
      item_id = int(call.data.split("_")[2])
      delete_menu(item_id)
      bot.edit_message_text(f"⚠️ Успешно удалено", chat_id=call.message.chat.id, message_id=call.message.message_id)
      bot.send_message(text=f"🍉 Добро пожаловать в меню!\n🔎 Выберите или введите название изделия.", chat_id=call.message.chat.id, reply_markup=menu_board(0))
      bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_edit_"))
def edit_item(call): # logic of edit choosen item after choose EDIT
    if is_admin(call.message.chat.id):
      item_id = int(call.data.split("_")[2])
      keyboard = InlineKeyboardMarkup()
      keyboard.add(InlineKeyboardButton("📒 Изменить название", callback_data=f"edit_nameitem_{item_id}"))
      keyboard.add(InlineKeyboardButton("📓 Изменить описание", callback_data=f"edit_describeitem_{item_id}"))
      keyboard.add(InlineKeyboardButton("↩️ Назад", callback_data=f"item_{item_id}"))

      name, describe = get_menu_by_id(item_id)
      bot.edit_message_text(f"<b>{name}</b>\n<blockquote>{describe}</blockquote>\n\nВыберите тип редактирования:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode="HTML")
      bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("edit_nameitem_"))
def edit_nameitem_(call): # logic of edit choosen item after choose EDIT NAME
    if is_admin(call.message.chat.id):
      item_id = int(call.data.split("_")[2])
      name, describe = get_menu_by_id(item_id)
      bot.edit_message_text(f"⚠️ Введите новое название (старое: {name}):", chat_id=call.message.chat.id, message_id=call.message.message_id)
      bot.register_next_step_handler(call.message, get_edit_name, item_id, describe)

def get_edit_name(message, id, describe): # logic of send changes after edited name
    if is_admin(message.chat.id):
      name = message.text
      edit_menu(id, name, describe)
      bot.send_message(message.chat.id,"Название успешно обновлено!")
      if is_admin(message.chat.id):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text="📝 Изменить изделие",callback_data=f"admin_edit_{id}"), InlineKeyboardButton(text="🗑️ Удалить изделие",callback_data=f"admin_delete_{id}"))
        keyboard.add(InlineKeyboardButton(text="↩️ Выйти",callback_data="back"))
        bot.send_message(text=f"<b>{name}</b>\n<blockquote>{describe}</blockquote>", parse_mode="HTML",chat_id=message.chat.id, reply_markup=keyboard)
      else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="↩️ Выйти",callback_data="back"))
        bot.send_message(text=f"<b>{name}</b>\n<blockquote>{describe}</blockquote>", parse_mode="HTML",chat_id=message.chat.id, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda c: c.data.startswith("edit_describeitem_"))
def edit_describeitem_(call): # logic of edit choosen item after choose EDIT DESCRIBE
    if is_admin(call.message.chat.id):
      item_id = int(call.data.split("_")[2])
      name, describe = get_menu_by_id(item_id)
      bot.edit_message_text(f"⚠️ Введите новое описание (старое: {describe}):", chat_id=call.message.chat.id, message_id=call.message.message_id)
      bot.register_next_step_handler(call.message, get_edit_describe, item_id, name)

def get_edit_describe(message, id, name): # logic of send changes after edited name
    if is_admin(message.chat.id):
      describe = message.text
      edit_menu(id, name, describe)
      bot.send_message(message.chat.id,"Описание успешно обновлено!")
      if is_admin(message.chat.id) == 1:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text="📝 Изменить изделие",callback_data=f"admin_edit_{id}"), InlineKeyboardButton(text="🗑️ Удалить изделие",callback_data=f"admin_delete_{id}"))
        keyboard.add(InlineKeyboardButton(text="↩️ Выйти",callback_data="back"))
        bot.send_message(text=f"<b>{name}</b>\n<blockquote>{describe}</blockquote>", parse_mode="HTML",chat_id=message.chat.id, reply_markup=keyboard)
      else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="↩️ Выйти",callback_data="back"))
        bot.send_message(text=f"<b>{name}</b>\n<blockquote>{describe}</blockquote>", parse_mode="HTML",chat_id=message.chat.id, reply_markup=keyboard)


# Technical fragment
@bot.message_handler(commands=['my_console_id'])
def my_console_id(message): # print to console id of user
    print("Пользователь запросил свой ID в консоль:", message.chat.id)
    bot.delete_message(message.chat.id, message.id)
    

# BOT LIFE / DO NOT EDIT 
init_db()
bot.polling(none_stop=True, skip_pending=True)