import telebot
from telebot import types
import time

# === КОНФИГУРАЦИЯ ===
# ЗАМЕНИТЕ ЭТИ ЗНАЧЕНИЯ НА СВОИ!
BOT_TOKEN = "8228595010:AAFJHE3PBlAdFy7NV_ZmoQbhBwby2zXOUCo"  # Получить у @BotFather
ADMIN_ID = [8132287874, 8458889045]          # Ваш ID (узнать у @userinfobot)

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# === ХРАНЕНИЕ ДАННЫХ ===
active_dialogs = {}  # {admin_chat_id: user_chat_id}

# === ФУНКЦИЯ ДЛЯ ПЕЧАТИ ИНФОРМАЦИИ В КОНСОЛЬ ===
def print_info(message):
    """Выводит информацию в консоль"""
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")

# === ОБРАБОТКА КОМАНД ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработка команды /start"""
    user = message.from_user
    welcome_text = f"""👋 <b>Привет, {user.first_name}!</b>

🤖 Я бот для связи с администратором.
📝 Просто напишите мне сообщение, и я передам его админу.

⚡ Админ ответит вам как можно скорее!
❓ Используйте /help для справки"""
    
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')
    print_info(f"Пользователь {user.id} ({user.first_name}) запустил бота")

@bot.message_handler(commands=['help'])
def send_help(message):
    """Обработка команды /help"""
    help_text = """ℹ️ <b>Помощь</b>

📤 <b>Как отправить сообщение админу:</b>
1. Просто напишите любое сообщение в этот чат
2. Я автоматически передам его администратору
3. Админ получит уведомление и ответит вам

📨 <b>Поддерживаются:</b>
• Текст • Фото • Видео • Документы
• Аудио • Голосовые сообщения • Стикеры

⏳ Обычно ответ приходит в течение нескольких часов"""
    
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['cancel'])
def cancel_dialog(message):
    """Обработка команды /cancel"""
    bot.reply_to(message, "✅ Диалог отменен. Вы можете отправить новое сообщение в любое время!")

# === КОМАНДЫ ДЛЯ АДМИНА ===
@bot.message_handler(commands=['admin', 'status'], chat_id=ADMIN_ID)
def admin_commands(message):
    """Команды только для админа"""
    if message.text == '/admin':
        text = """👨‍💼 <b>ПАНЕЛЬ АДМИНИСТРАТОРА</b>

<b>Доступные команды:</b>
/admin - Эта панель
/status - Статус бота

<b>Как отвечать пользователям:</b>
1. Получите сообщение от пользователя
2. Нажмите кнопку "💬 Ответить" под сообщением
3. Все ваши сообщения пойдут этому пользователю
4. Для ответа другому - нажмите его кнопку "Ответить" """
        
        bot.reply_to(message, text, parse_mode='HTML')
    
    elif message.text == '/status':
        active_count = len(active_dialogs)
        status_text = f"""📊 <b>СТАТУС БОТА</b>

✅ <b>Бот работает</b>
🔄 <b>Активных диалогов:</b> {active_count}
👤 <b>Ваш ID:</b> <code>{ADMIN_ID}</code>

🕒 <b>Время:</b> {time.strftime('%H:%M:%S')}"""
        
        bot.reply_to(message, status_text, parse_mode='HTML')

# === ОБРАБОТКА СООБЩЕНИЙ ОТ ПОЛЬЗОВАТЕЛЕЙ ===
@bot.message_handler(
    content_types=['text', 'photo', 'document', 'video', 'audio', 'voice', 'sticker'],
    func=lambda message: message.chat.type == 'private' and not message.text.startswith('/')
)
def forward_to_admin(message):
    """Пересылаем сообщения от пользователей админу"""
    user = message.from_user
    user_chat_id = message.chat.id
    
    print_info(f"Сообщение от {user.id} ({user.first_name}): {message.content_type}")
    
    # Подтверждение пользователю
    try:
        bot.reply_to(message, "✅ Сообщение отправлено администратору!")
    except:
        pass
    
    # Формируем информацию о пользователе
    user_info = f"""📨 <b>НОВОЕ СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ:</b>

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
    
    # Создаем клавиатуру для ответа
    keyboard = types.InlineKeyboardMarkup()
    reply_btn = types.InlineKeyboardButton(
        text=f"💬 Ответить {user.first_name}",
        callback_data=f"reply_{user_chat_id}"
    )
    keyboard.add(reply_btn)
    
    # Отправляем админу в зависимости от типа контента
    try:
        if message.content_type == 'text':
            bot.send_message(
                ADMIN_ID,
                user_info + message_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        
        elif message.content_type == 'photo':
            bot.send_photo(
                ADMIN_ID,
                message.photo[-1].file_id,
                caption=user_info + message_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        
        elif message.content_type == 'document':
            bot.send_document(
                ADMIN_ID,
                message.document.file_id,
                caption=user_info + message_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        
        elif message.content_type == 'video':
            bot.send_video(
                ADMIN_ID,
                message.video.file_id,
                caption=user_info + message_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        
        elif message.content_type == 'audio':
            bot.send_audio(
                ADMIN_ID,
                message.audio.file_id,
                caption=user_info + message_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        
        elif message.content_type == 'voice':
            bot.send_voice(
                ADMIN_ID,
                message.voice.file_id,
                caption=user_info + " (Голосовое сообщение)",
                parse_mode='HTML',
                reply_markup=keyboard
            )
        
        elif message.content_type == 'sticker':
            bot.send_message(
                ADMIN_ID,
                user_info + "\n\n🎭 <b>Стикер:</b>",
                parse_mode='HTML',
                reply_markup=keyboard
            )
            bot.send_sticker(ADMIN_ID, message.sticker.file_id)
        
        print_info(f"Сообщение от {user.id} переслано админу")
    
    except Exception as e:
        print_info(f"Ошибка пересылки от {user.id}: {str(e)}")
        try:
            bot.reply_to(message, "❌ Произошла ошибка при отправке. Пожалуйста, попробуйте позже.")
        except:
            pass

# === ОБРАБОТКА КНОПОК ===
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработка нажатий кнопок"""
    try:
        if call.data.startswith('reply_'):
            user_chat_id = int(call.data.split('_')[1])
            admin_chat_id = call.message.chat.id
            
            # Сохраняем активный диалог
            active_dialogs[admin_chat_id] = user_chat_id
            
            # Редактируем сообщение
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"""✅ <b>ДИАЛОГ АКТИВИРОВАН</b>

Теперь все ваши сообщения будут отправляться пользователю с Chat ID:
<code>{user_chat_id}</code>

✏️ <b>Просто напишите ответ...</b>""",
                    parse_mode='HTML'
                )
            except:
                pass
            
            # Отправляем подтверждение
            bot.send_message(
                admin_chat_id,
                f"""💬 <b>Вы начали диалог с пользователем</b>

Chat ID: <code>{user_chat_id}</code>

Теперь все ваши сообщения будут отправляться этому пользователю.
Для ответа другому - нажмите "Ответить" под его сообщением.""",
                parse_mode='HTML'
            )
            
            bot.answer_callback_query(call.id, "✅ Диалог начат!")
            print_info(f"Админ {admin_chat_id} начал диалог с {user_chat_id}")
    
    except Exception as e:
        print_info(f"Ошибка в callback: {str(e)}")
        bot.answer_callback_query(call.id, "❌ Ошибка")

# === ОТВЕТЫ АДМИНА ПОЛЬЗОВАТЕЛЯМ ===
@bot.message_handler(
    content_types=['text', 'photo', 'document', 'video', 'audio', 'voice', 'sticker'],
    func=lambda message: message.chat.id == ADMIN_ID and not message.text.startswith('/')
)
def admin_reply(message):
    """Обработка ответов админа"""
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

Используйте /status для проверки""",
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
            bot.send_photo(
                user_chat_id,
                message.photo[-1].file_id,
                caption=f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{message.caption or ''}""",
                parse_mode='HTML'
            )
            bot.reply_to(message, "✅ Фото отправлено пользователю")
        
        elif message.content_type == 'document':
            bot.send_document(
                user_chat_id,
                message.document.file_id,
                caption=f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{message.caption or ''}""",
                parse_mode='HTML'
            )
            bot.reply_to(message, "✅ Документ отправлен")
        
        elif message.content_type == 'video':
            bot.send_video(
                user_chat_id,
                message.video.file_id,
                caption=f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{message.caption or ''}""",
                parse_mode='HTML'
            )
            bot.reply_to(message, "✅ Видео отправлено")
        
        elif message.content_type == 'audio':
            bot.send_audio(
                user_chat_id,
                message.audio.file_id,
                caption=f"""👨‍💼 <b>ОТВЕТ ОТ АДМИНИСТРАТОРА</b>

{message.caption or ''}""",
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
        
        print_info(f"Админ отправил {message.content_type} пользователю {user_chat_id}")
    
    except Exception as e:
        error_msg = str(e)
        print_info(f"Ошибка отправки пользователю {user_chat_id}: {error_msg}")
        
        # Проверяем конкретные ошибки
        if "chat not found" in error_msg.lower() or "blocked" in error_msg.lower():
            bot.reply_to(message, "❌ Не удалось отправить. Пользователь заблокировал бота или чат не найден.")
        else:
            bot.reply_to(message, f"❌ Не удалось отправить сообщение. Ошибка: {error_msg[:100]}")
        
        # Удаляем нерабочий диалог
        if admin_chat_id in active_dialogs:
            del active_dialogs[admin_chat_id]

# === ЗАПУСК БОТА ===
def main():
    """Запуск бота"""
    print("=" * 50)
    print("🤖 ТЕЛЕГРАМ БОТ ДЛЯ СВЯЗИ С АДМИНОМ")
    print("=" * 50)
    print(f"👨‍💼 Админ ID: {ADMIN_ID}")
    print(f"🔑 Токен: {BOT_TOKEN[:10]}...")
    print()
    print("📱 Бот работает в личных сообщениях")
    print()
    print("🎯 КАК ЭТО РАБОТАЕТ:")
    print("1. ПОЛЬЗОВАТЕЛЬ пишет боту → сообщение идет АДМИНУ")
    print("2. АДМИН жмет '💬 Ответить' под сообщением")
    print("3. АДМИН пишет ответ → ответ идет ПОЛЬЗОВАТЕЛЮ")
    print("=" * 50)
    print()
    print("✅ Бот запущен!")
    print("📝 Все события будут отображаться здесь")
    print("⏳ Ожидание сообщений...")
    print()
    
    # Бесконечный перезапуск при ошибках
    while True:
        try:
            print_info("Запуск бота...")
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            error_msg = str(e)
            print_info(f"Бот упал с ошибкой: {error_msg}")
            print_info("Перезапуск через 5 секунд...")
            time.sleep(5)

# === ТОЧКА ВХОДА ===
if __name__ == "__main__":
    main()