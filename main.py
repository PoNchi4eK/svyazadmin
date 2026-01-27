import telebot
from telebot import types
import time
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# === КОНФИГУРАЦИЯ ===
# Лучше хранить в переменных окружения или защищенном хранилище
BOT_TOKEN = os.getenv('BOT_TOKEN', "8228595010:AAFJHE3PBlAdFy7NV_ZmoQbhBwby2zXOUCo")

# Список ID администраторов (можно добавить несколько)
ADMIN_IDS = [
    8132287874,  # Ваш ID
    8458889045 # второй админ
]

# Проверка наличия токена
if not BOT_TOKEN:
    print("ОШИБКА: Не указан BOT_TOKEN!")
    print("Создайте файл .env и добавьте: BOT_TOKEN=ваш_токен")
    exit(1)

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# === ХРАНЕНИЕ ДАННЫХ ===
# active_dialogs: {admin_chat_id: user_chat_id}
# user_data: {user_chat_id: {"name": str, "username": str}}
active_dialogs = {}
user_data = {}

# === ФУНКЦИИ ВСПОМОГАТЕЛЬНЫЕ ===
def print_info(message):
    """Выводит информацию в консоль"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def is_admin(chat_id):
    """Проверяет, является ли пользователь администратором"""
    return chat_id in ADMIN_IDS

def get_user_info(user_chat_id):
    """Получает информацию о пользователе"""
    if user_chat_id in user_data:
        return user_data[user_chat_id]
    return {"name": "Неизвестный", "username": "нет"}

# === ОБРАБОТКА КОМАНД ДЛЯ ВСЕХ ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработка команды /start"""
    user = message.from_user
    welcome_text = f"""👋 <b>Привет, {user.first_name}!</b>

🤖 Я бот для связи с администратором.
📝 Просто напишите мне сообщение, и я передам его админам.

⚡ Админы ответят вам как можно скорее!
❓ Используйте /help для справки"""
    
    # Сохраняем данные пользователя
    user_data[message.chat.id] = {
        "name": user.first_name,
        "username": user.username if user.username else "нет",
        "user_id": user.id
    }
    
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')
    print_info(f"Пользователь {user.id} ({user.first_name}) запустил бота")

@bot.message_handler(commands=['help'])
def send_help(message):
    """Обработка команды /help"""
    help_text = """ℹ️ <b>Помощь</b>

📤 <b>Как отправить сообщение админу:</b>
1. Просто напишите любое сообщение в этот чат
2. Я автоматически передам его администраторам
3. Админ получит уведомление и ответит вам

📨 <b>Поддерживаются:</b>
• Текст • Фото • Видео • Документы
• Аудио • Голосовые сообщения • Стикеры

⏳ Обычно ответ приходит в течение нескольких часов

🆘 <b>Команды:</b>
/start - Начало работы
/help - Эта справка
/cancel - Отмена текущего диалога"""
    
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['cancel'])
def cancel_dialog(message):
    """Обработка команды /cancel"""
    user_id = message.chat.id
    
    # Отменяем диалог если пользователь - админ
    if is_admin(user_id) and user_id in active_dialogs:
        target_user = active_dialogs[user_id]
        del active_dialogs[user_id]
        bot.send_message(user_id, f"✅ Диалог с пользователем {target_user} завершен.")
        print_info(f"Админ {user_id} завершил диалог с {target_user}")
    else:
        bot.reply_to(message, "✅ Вы можете начать новый диалог в любое время!")

# === КОМАНДЫ ДЛЯ АДМИНОВ ===
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    """Панель администратора"""
    if not is_admin(message.chat.id):
        bot.reply_to(message, "⛔ У вас нет прав доступа к этой команде.")
        return
    
    admin_panel_text = """👨‍💼 <b>ПАНЕЛЬ АДМИНИСТРАТОРА</b>

<b>Доступные команды:</b>
/admin - Эта панель
/status - Статус бота
/users - Список пользователей
/broadcast - Рассылка (в разработке)

<b>Как отвечать пользователям:</b>
1. Получите сообщение от пользователя
2. Нажмите кнопку "💬 Ответить" под сообщением
3. Все ваши сообщения пойдут этому пользователю
4. Для ответа другому - нажмите его кнопку "Ответить"

<b>Текущие администраторы:</b>"""
    
    # Добавляем список админов
    for i, admin_id in enumerate(ADMIN_IDS, 1):
        admin_panel_text += f"\n{i}. ID: <code>{admin_id}</code>"
    
    bot.reply_to(message, admin_panel_text, parse_mode='HTML')

@bot.message_handler(commands=['status'])
def bot_status(message):
    """Статус бота"""
    if not is_admin(message.chat.id):
        bot.reply_to(message, "⛔ У вас нет прав доступа к этой команде.")
        return
    
    active_count = len(active_dialogs)
    users_count = len(user_data)
    
    status_text = f"""📊 <b>СТАТУС БОТА</b>

✅ <b>Бот работает</b>
🔄 <b>Активных диалогов:</b> {active_count}
👥 <b>Всего пользователей:</b> {users_count}
👑 <b>Администраторов:</b> {len(ADMIN_IDS)}

<b>Активные диалоги:</b>"""
    
    if active_dialogs:
        for admin_id, user_id in active_dialogs.items():
            user_info = get_user_info(user_id)
            status_text += f"\nАдмин {admin_id} → {user_info['name']} (ID: {user_id})"
    else:
        status_text += "\nНет активных диалогов"
    
    status_text += f"\n\n🕒 <b>Время:</b> {time.strftime('%H:%M:%S %d.%m.%Y')}"
    
    bot.reply_to(message, status_text, parse_mode='HTML')

@bot.message_handler(commands=['users'])
def list_users(message):
    """Список пользователей"""
    if not is_admin(message.chat.id):
        bot.reply_to(message, "⛔ У вас нет прав доступа к этой команде.")
        return
    
    if not user_data:
        bot.reply_to(message, "📭 Пользователей еще нет.")
        return
    
    users_text = f"👥 <b>Список пользователей:</b> ({len(user_data)} чел.)\n\n"
    
    for i, (user_id, data) in enumerate(list(user_data.items())[:50], 1):  # Ограничим вывод
        users_text += f"{i}. <b>{data['name']}</b>\n"
        users_text += f"   👤 @{data['username']}\n"
        users_text += f"   🆔 <code>{user_id}</code>\n\n"
    
    if len(user_data) > 50:
        users_text += f"\n... и еще {len(user_data) - 50} пользователей"
    
    bot.reply_to(message, users_text, parse_mode='HTML')

# === ОБРАБОТКА СООБЩЕНИЙ ОТ ПОЛЬЗОВАТЕЛЕЙ ===
@bot.message_handler(
    content_types=['text', 'photo', 'document', 'video', 'audio', 'voice', 'sticker'],
    func=lambda message: message.chat.type == 'private' and 
                         not message.text.startswith('/') and
                         not is_admin(message.chat.id)
)
def forward_to_admin(message):
    """Пересылаем сообщения от пользователей админам"""
    user = message.from_user
    user_chat_id = message.chat.id
    
    # Сохраняем/обновляем данные пользователя
    user_data[user_chat_id] = {
        "name": user.first_name,
        "username": user.username if user.username else "нет",
        "user_id": user.id
    }
    
    print_info(f"Сообщение от {user.id} ({user.first_name}): {message.content_type}")
    
    # Подтверждение пользователю
    try:
        bot.reply_to(message, "✅ Сообщение отправлено администраторам!")
    except Exception as e:
        print_info(f"Ошибка отправки подтверждения: {e}")
    
    # Формируем информацию о пользователе
    user_info = f"""📨 <b>НОВОЕ СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ</b>

👤 <b>Имя:</b> {user.first_name}
📱 <b>Username:</b> @{user.username if user.username else 'нет'}
🆔 <b>User ID:</b> <code>{user.id}</code>
💬 <b>Chat ID:</b> <code>{user_chat_id}</code>
🕒 <b>Время:</b> {time.strftime('%H:%M:%S')}"""
    
    # Добавляем текст сообщения
    message_text = ""
    if message.content_type == 'text':
        message_text = f"\n\n💬 <b>Сообщение:</b>\n{message.text}"
    elif message.caption:
        message_text = f"\n\n💬 <b>Подпись:</b>\n{message.caption}"
    
    # Отправляем всем админам
    for admin_id in ADMIN_IDS:
        try:
            # Создаем клавиатуру для ответа
            keyboard = types.InlineKeyboardMarkup()
            reply_btn = types.InlineKeyboardButton(
                text=f"💬 Ответить {user.first_name}",
                callback_data=f"reply_{user_chat_id}"
            )
            keyboard.add(reply_btn)
            
            # Отправляем в зависимости от типа контента
            if message.content_type == 'text':
                bot.send_message(
                    admin_id,
                    user_info + message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            
            elif message.content_type == 'photo':
                bot.send_photo(
                    admin_id,
                    message.photo[-1].file_id,
                    caption=user_info + message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            
            elif message.content_type == 'document':
                bot.send_document(
                    admin_id,
                    message.document.file_id,
                    caption=user_info + message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            
            elif message.content_type == 'video':
                bot.send_video(
                    admin_id,
                    message.video.file_id,
                    caption=user_info + message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            
            elif message.content_type == 'audio':
                bot.send_audio(
                    admin_id,
                    message.audio.file_id,
                    caption=user_info + message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            
            elif message.content_type == 'voice':
                bot.send_voice(
                    admin_id,
                    message.voice.file_id,
                    caption=user_info + " (Голосовое сообщение)",
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            
            elif message.content_type == 'sticker':
                bot.send_message(
                    admin_id,
                    user_info + "\n\n🎭 <b>Стикер:</b>",
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
                bot.send_sticker(admin_id, message.sticker.file_id)
            
            print_info(f"Сообщение от {user.id} переслано админу {admin_id}")
        
        except Exception as e:
            print_info(f"Ошибка пересылки админу {admin_id}: {str(e)}")

# === ОБРАБОТКА КНОПОК ===
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработка нажатий кнопок"""
    try:
        if call.data.startswith('reply_'):
            user_chat_id = int(call.data.split('_')[1])
            admin_chat_id = call.message.chat.id
            
            # Проверяем, является ли отправитель админом
            if not is_admin(admin_chat_id):
                bot.answer_callback_query(call.id, "⛔ Вы не администратор!")
                return
            
            # Получаем информацию о пользователе
            user_info = get_user_info(user_chat_id)
            
            # Сохраняем активный диалог
            active_dialogs[admin_chat_id] = user_chat_id
            
            # Редактируем сообщение
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"""✅ <b>ДИАЛОГ АКТИВИРОВАН</b>

Теперь все ваши сообщения будут отправляться:
👤 <b>{user_info['name']}</b>
📱 @{user_info['username']}
🆔 Chat ID: <code>{user_chat_id}</code>

✏️ <b>Просто напишите ответ...</b>
ℹ️ Используйте /cancel для завершения диалога""",
                    parse_mode='HTML'
                )
            except Exception as e:
                print_info(f"Ошибка редактирования сообщения: {e}")
            
            # Отправляем подтверждение
            bot.send_message(
                admin_chat_id,
                f"""💬 <b>Вы начали диалог с пользователем</b>

👤 <b>{user_info['name']}</b>
📱 @{user_info['username']}
🆔 Chat ID: <code>{user_chat_id}</code>

Теперь все ваши сообщения будут отправляться этому пользователю.
Для ответа другому - нажмите "Ответить" под его сообщением.

ℹ️ Используйте /cancel для завершения диалога.""",
                parse_mode='HTML'
            )
            
            bot.answer_callback_query(call.id, "✅ Диалог начат!")
            print_info(f"Админ {admin_chat_id} начал диалог с {user_chat_id} ({user_info['name']})")
    
    except Exception as e:
        print_info(f"Ошибка в callback: {str(e)}")
        bot.answer_callback_query(call.id, "❌ Ошибка обработки запроса")

# === ОТВЕТЫ АДМИНОВ ПОЛЬЗОВАТЕЛЯМ ===
@bot.message_handler(
    content_types=['text', 'photo', 'document', 'video', 'audio', 'voice', 'sticker'],
    func=lambda message: is_admin(message.chat.id) and not message.text.startswith('/')
)
def admin_reply(message):
    """Обработка ответов админов"""
    admin_chat_id = message.chat.id
    
    # Проверяем активный диалог
    if admin_chat_id not in active_dialogs:
        bot.reply_to(
            message,
            """⚠️ <b>ВЫ НЕ В ДИАЛОГЕ</b>

Чтобы ответить пользователю:
1. Дождитесь сообщения от пользователя
2. Нажмите кнопку "💬 Ответить" под сообщением
3. После этого пишите ответ

Используйте /status для проверки активных диалогов""",
            parse_mode='HTML'
        )
        return
    
    user_chat_id = active_dialogs[admin_chat_id]
    
    try:
        # Отправляем ответ пользователю
        if message.content_type == 'text':
            bot.send_message(
                user_chat_id,
                f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{message.text}

💬 <i>Вы можете продолжить диалог, просто ответив на это сообщение</i>""",
                parse_mode='HTML'
            )
            bot.reply_to(message, f"✅ Ответ отправлен пользователю (Chat ID: {user_chat_id})")
        
        elif message.content_type == 'photo':
            caption = message.caption or ""
            bot.send_photo(
                user_chat_id,
                message.photo[-1].file_id,
                caption=f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{caption}""",
                parse_mode='HTML'
            )
            bot.reply_to(message, "✅ Фото отправлено пользователю")
        
        elif message.content_type == 'document':
            caption = message.caption or ""
            bot.send_document(
                user_chat_id,
                message.document.file_id,
                caption=f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{caption}""",
                parse_mode='HTML'
            )
            bot.reply_to(message, "✅ Документ отправлен")
        
        elif message.content_type == 'video':
            caption = message.caption or ""
            bot.send_video(
                user_chat_id,
                message.video.file_id,
                caption=f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{caption}""",
                parse_mode='HTML'
            )
            bot.reply_to(message, "✅ Видео отправлено")
        
        elif message.content_type == 'audio':
            caption = message.caption or ""
            bot.send_audio(
                user_chat_id,
                message.audio.file_id,
                caption=f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{caption}""",
                parse_mode='HTML'
            )
            bot.reply_to(message, "✅ Аудио отправлено")
        
        elif message.content_type == 'voice':
            bot.send_voice(
                user_chat_id,
                message.voice.file_id,
                caption="👨‍💼 ОТВЕТ ОТ АДМИНИСТРАТОРА",
                parse_mode='HTML'
            )
            bot.reply_to(message, "✅ Голосовое сообщение отправлено")
        
        elif message.content_type == 'sticker':
            bot.send_message(
                user_chat_id,
                "👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>",
                parse_mode='HTML'
            )
            bot.send_sticker(user_chat_id, message.sticker.file_id)
            bot.reply_to(message, "✅ Стикер отправлен")
        
        print_info(f"Админ {admin_chat_id} отправил {message.content_type} пользователю {user_chat_id}")
    
    except Exception as e:
        error_msg = str(e)
        print_info(f"Ошибка отправки пользователю {user_chat_id}: {error_msg}")
        
        # Проверяем конкретные ошибки
        if "chat not found" in error_msg.lower() or "blocked" in error_msg.lower():
            bot.reply_to(message, "❌ Не удалось отправить. Пользователь заблокировал бота или чат не найден.")
            # Удаляем нерабочий диалог
            if admin_chat_id in active_dialogs:
                del active_dialogs[admin_chat_id]
                bot.send_message(admin_chat_id, "🗑️ Диалог удален из активных.")
        else:
            bot.reply_to(message, f"❌ Не удалось отправить сообщение. Ошибка: {error_msg[:100]}")

# === ЗАПУСК БОТА ===
def main():
    """Запуск бота"""
    print("=" * 60)
    print("🤖 ТЕЛЕГРАМ БОТ ДЛЯ СВЯЗИ С АДМИНАМИ")
    print("=" * 60)
    print(f"👑 Админы: {len(ADMIN_IDS)} пользователей")
    for i, admin_id in enumerate(ADMIN_IDS, 1):
        print(f"   {i}. ID: {admin_id}")
    print(f"🔑 Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-10:]}")
    print()
    print("📱 Бот работает в личных сообщениях")
    print()
    print("🎯 КАК ЭТО РАБОТАЕТ:")
    print("1. ПОЛЬЗОВАТЕЛЬ пишет боту → сообщение идет ВСЕМ АДМИНАМ")
    print("2. ЛЮБОЙ АДМИН жмет '💬 Ответить' под сообщением")
    print("3. АДМИН пишет ответ → ответ идет ПОЛЬЗОВАТЕЛЮ")
    print("=" * 60)
    print()
    print("✅ Бот запущен!")
    print("📝 Все события будут отображаться здесь")
    print("⏳ Ожидание сообщений...")
    print()
    
    # Проверяем, что бот может получить информацию о себе
    try:
        bot_info = bot.get_me()
        print_info(f"Бот @{bot_info.username} успешно запущен!")
    except Exception as e:
        print_info(f"Ошибка подключения к Telegram API: {e}")
        print_info("Проверьте токен бота и интернет-соединение")
        return
    
    # Бесконечный перезапуск при ошибках
    while True:
        try:
            print_info("Запуск polling...")
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            error_msg = str(e)
            print_info(f"Бот упал с ошибкой: {error_msg}")
            print_info("Перезапуск через 5 секунд...")
            time.sleep(5)

# === ТОЧКА ВХОДА ===
if __name__ == "__main__":
    main()