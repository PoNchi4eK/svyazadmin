import logging
import telebot
from telebot import types

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
ADMIN_ID = 8132287874  # Замените на ваш ID в Telegram
BOT_TOKEN = "8228595010:AAFJHE3PBlAdFy7NV_ZmoQbhBwby2zXOUCo"  # Получите у @BotFather

# Создаем экземпляр бота 
bot = telebot.TeleBot(BOT_TOKEN)

# Хранение данных
# Ключевое исправление: user_id -> chat_id пользователя
active_dialogs = {}  # {admin_chat_id: user_chat_id}
user_info = {}       # {user_chat_id: {"name": ..., "user_id": ...}}

# ========== ОБРАБОТКА СООБЩЕНИЙ ОТ ПОЛЬЗОВАТЕЛЕЙ ==========

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработка команды /start"""
    user = message.from_user
    bot.reply_to(message, 
        f"👋 Привет, {user.full_name}!\n\n"
        "Я бот для связи с администратором.\n"
        "Просто отправь мне сообщение, и я перешлю его админу.\n\n"
        "Админ ответит вам как можно скорее!\n\n"
        "Используйте /help для справки."
    )

@bot.message_handler(commands=['help', 'cancel'])
def handle_help_cancel(message):
    """Обработка команд /help и /cancel"""
    if message.text == '/help':
        bot.reply_to(message,
            "ℹ️ *Помощь*\n\n"
            "• Просто напишите мне сообщение, и оно будет отправлено администратору\n"
            "• Администратор получит ваше сообщение и ответит вам\n\n"
            "Если у вас есть вопросы, пишите!",
            parse_mode='Markdown'
        )
    else:
        bot.reply_to(message,
            "Диалог отменен. Вы можете начать новый в любое время, просто написав сообщение!"
        )

@bot.message_handler(
    content_types=['text', 'photo', 'document', 'video', 'audio', 'voice', 'sticker'],
    func=lambda message: message.chat.type == 'private'
)
def handle_user_message(message):
    """Обработка всех сообщений от пользователей"""
    user = message.from_user
    user_chat_id = message.chat.id  # Это chat_id пользователя
    
    # Сохраняем информацию о пользователе
    user_info[user_chat_id] = {
        'name': user.full_name,
        'username': user.username or "Без username",
        'user_id': user.id  # Telegram ID пользователя
    }
    
    # Уведомляем пользователя
    if message.content_type == 'text':
        bot.reply_to(message, "✅ Сообщение отправлено администратору!\nОжидайте ответа.")
    else:
        bot.reply_to(message, "✅ Файл отправлен администратору!\nОжидайте ответа.")
    
    # Отправляем сообщение админу
    send_to_admin(user, message, user_chat_id)

def send_to_admin(user, message, user_chat_id):
    """Отправка сообщения от пользователя админу"""
    # Создаем inline-клавиатуру с кнопкой "Ответить" 
    keyboard = types.InlineKeyboardMarkup()
    # Ключевое изменение: передаем user_chat_id в callback_data
    reply_button = types.InlineKeyboardButton(
        text=f"💬 Ответить {user.full_name}",
        callback_data=f"reply_{user_chat_id}"  # Теперь передаем chat_id пользователя
    )
    keyboard.add(reply_button)
    
    # Формируем текст сообщения для админа
    text = f"📨 *Новое сообщение от пользователя:*\n\n"
    text += f"👤 *Имя:* {user.full_name}\n"
    text += f"📱 *Username:* @{user.username or 'Без username'}\n"
    text += f"🆔 *User ID:* `{user.id}`\n"
    text += f"💬 *Chat ID:* `{user_chat_id}`\n"
    
    try:
        # Отправляем текстовое сообщение
        if message.content_type == 'text':
            text += f"\n💬 *Сообщение:*\n{message.text}"
            bot.send_message(ADMIN_ID, text, parse_mode='Markdown', reply_markup=keyboard)
        
        # Отправляем фото
        elif message.content_type == 'photo':
            text += f"\n💬 *Сообщение:*\n{message.caption or 'Фото'}"
            bot.send_photo(
                ADMIN_ID, 
                message.photo[-1].file_id, 
                caption=text, 
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        
        # Отправляем документ
        elif message.content_type == 'document':
            text += f"\n💬 *Сообщение:*\n{message.caption or 'Документ'}"
            bot.send_document(
                ADMIN_ID,
                message.document.file_id,
                caption=text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        
        # Отправляем видео
        elif message.content_type == 'video':
            text += f"\n💬 *Сообщение:*\n{message.caption or 'Видео'}"
            bot.send_video(
                ADMIN_ID,
                message.video.file_id,
                caption=text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        
        # Отправляем аудио
        elif message.content_type == 'audio':
            text += f"\n💬 *Сообщение:*\n{message.caption or 'Аудио'}"
            bot.send_audio(
                ADMIN_ID,
                message.audio.file_id,
                caption=text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        # Отправляем голосовое сообщение
        elif message.content_type == 'voice':
            text += f"\n💬 *Сообщение:*\nГолосовое сообщение"
            bot.send_voice(
                ADMIN_ID,
                message.voice.file_id,
                caption=text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        # Отправляем стикер
        elif message.content_type == 'sticker':
            text += f"\n💬 *Сообщение:*\nСтикер"
            bot.send_message(ADMIN_ID, text, parse_mode='Markdown', reply_markup=keyboard)
            bot.send_sticker(ADMIN_ID, message.sticker.file_id)
    
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения админу: {e}")

# ========== КОМАНДЫ ДЛЯ АДМИНА ==========

@bot.message_handler(commands=['admin'], chat_id=ADMIN_ID)
def handle_admin_panel(message):
    """Обработка команды /admin"""
    active_dialogs_count = len(active_dialogs)
    
    bot.reply_to(message,
        f"👨‍💼 *Панель администратора*\n\n"
        f"• Активных диалогов: {active_dialogs_count}\n"
        f"• Всего пользователей: {len(user_info)}\n\n"
        "Как отвечать пользователям:\n"
        "1. Вы получаете сообщение с кнопкой 'Ответить'\n"
        "2. Нажимаете кнопку '💬 Ответить'\n"
        "3. Пишете ответ - он отправится пользователю\n\n"
        "Для проверки диалога: /status",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['status'], chat_id=ADMIN_ID)
def handle_status(message):
    """Обработка команды /status"""
    admin_chat_id = message.chat.id
    
    if admin_chat_id in active_dialogs:
        user_chat_id = active_dialogs[admin_chat_id]
        if user_chat_id in user_info:
            user_data = user_info[user_chat_id]
            bot.reply_to(message,
                f"✅ *Активный диалог*\n\n"
                f"👤 С: {user_data['name']}\n"
                f"📱 @{user_data['username']}\n"
                f"💬 Chat ID: `{user_chat_id}`\n\n"
                f"Все ваши сообщения отправляются этому пользователю.",
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(message, "❌ Ошибка: информация о пользователе не найдена")
    else:
        bot.reply_to(message, 
            "⚠️ *Нет активного диалога*\n\n"
            "Чтобы начать диалог:\n"
            "1. Дождитесь сообщения от пользователя\n"
            "2. Нажмите кнопку '💬 Ответить'\n"
            "3. После этого пишите ответы",
            parse_mode='Markdown'
        )

# ========== ОБРАБОТКА INLINE КНОПОК ==========

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Обработка нажатий на inline кнопки"""
    try:
        if call.data.startswith("reply_"):
            # Начало диалога с пользователем
            user_chat_id = int(call.data.split("_")[1])
            admin_chat_id = call.message.chat.id
            
            # Проверяем, есть ли информация о пользователе
            if user_chat_id not in user_info:
                bot.answer_callback_query(call.id, "❌ Пользователь не найден!")
                return
            
            user_data = user_info[user_chat_id]
            
            # Сохраняем активный диалог: admin_chat_id -> user_chat_id
            active_dialogs[admin_chat_id] = user_chat_id
            
            # Редактируем сообщение с уведомлением
            new_text = f"💬 *Диалог с {user_data['name']}*\n\n"
            new_text += f"✅ Теперь все ваши сообщения будут отправляться:\n"
            new_text += f"👤 {user_data['name']} (@{user_data['username']})\n"
            new_text += f"💬 Chat ID: `{user_chat_id}`\n\n"
            new_text += f"✏️ *Напишите ответ:*"
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=new_text,
                parse_mode='Markdown'
            )
            
            bot.answer_callback_query(call.id, f"Диалог с {user_data['name']} начат!")
            
            # Отправляем дополнительное уведомление
            bot.send_message(
                admin_chat_id,
                f"✅ *Диалог начат!*\n\n"
                f"Теперь все ваши сообщения будут отправляться:\n"
                f"👤 {user_data['name']} (@{user_data['username']})\n\n"
                f"Просто напишите ответ...",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Ошибка обработки callback: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")

# ========== ОБРАБОТКА СООБЩЕНИЙ ОТ АДМИНА ==========

@bot.message_handler(
    content_types=['text', 'photo', 'document', 'video', 'audio', 'voice', 'sticker'],
    func=lambda message: message.chat.id == ADMIN_ID and not message.text.startswith('/')
)
def handle_admin_message(message):
    """Обработка сообщений от админа (ответы пользователям)"""
    admin_chat_id = message.chat.id
    
    # Проверяем, находится ли админ в активном диалоге
    if admin_chat_id in active_dialogs:
        user_chat_id = active_dialogs[admin_chat_id]
        
        # Проверяем, есть ли информация о пользователе
        if user_chat_id not in user_info:
            bot.reply_to(message, "❌ Ошибка: пользователь не найден!")
            if admin_chat_id in active_dialogs:
                del active_dialogs[admin_chat_id]
            return
        
        user_data = user_info[user_chat_id]
        
        try:
            # Отправляем текстовое сообщение
            if message.content_type == 'text':
                bot.send_message(
                    user_chat_id,
                    f"👨‍💼 *Ответ от администратора:*\n\n{message.text}",
                    parse_mode='Markdown'
                )
                bot.reply_to(message, f"✅ Ответ отправлен {user_data['name']}!")
            
            # Отправляем фото
            elif message.content_type == 'photo':
                bot.send_photo(
                    user_chat_id,
                    message.photo[-1].file_id,
                    caption=f"👨‍💼 *Ответ от администратора:*\n\n{message.caption or ''}",
                    parse_mode='Markdown'
                )
                bot.reply_to(message, f"✅ Фото отправлено {user_data['name']}!")
            
            # Отправляем документ
            elif message.content_type == 'document':
                bot.send_document(
                    user_chat_id,
                    message.document.file_id,
                    caption=f"👨‍💼 *Ответ от администратора:*\n\n{message.caption or ''}",
                    parse_mode='Markdown'
                )
                bot.reply_to(message, f"✅ Документ отправлен {user_data['name']}!")
            
            # Отправляем видео
            elif message.content_type == 'video':
                bot.send_video(
                    user_chat_id,
                    message.video.file_id,
                    caption=f"👨‍💼 *Ответ от администратора:*\n\n{message.caption or ''}",
                    parse_mode='Markdown'
                )
                bot.reply_to(message, f"✅ Видео отправлено {user_data['name']}!")
            
            # Отправляем аудио
            elif message.content_type == 'audio':
                bot.send_audio(
                    user_chat_id,
                    message.audio.file_id,
                    caption=f"👨‍💼 *Ответ от администратора:*\n\n{message.caption or ''}",
                    parse_mode='Markdown'
                )
                bot.reply_to(message, f"✅ Аудио отправлено {user_data['name']}!")
                
            # Отправляем голосовое сообщение
            elif message.content_type == 'voice':
                bot.send_voice(
                    user_chat_id,
                    message.voice.file_id,
                    caption="👨‍💼 *Ответ от администратора*",
                    parse_mode='Markdown'
                )
                bot.reply_to(message, f"✅ Голосовое сообщение отправлено {user_data['name']}!")
                
            # Отправляем стикер
            elif message.content_type == 'sticker':
                bot.send_message(
                    user_chat_id,
                    "👨‍💼 *Ответ от администратора:*\n\nСтикер",
                    parse_mode='Markdown'
                )
                bot.send_sticker(user_chat_id, message.sticker.file_id)
                bot.reply_to(message, f"✅ Стикер отправлен {user_data['name']}!")
        
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            bot.reply_to(message, 
                f"❌ Не удалось отправить сообщение {user_data['name']}!\n"
                f"Возможно, пользователь заблокировал бота."
            )
            # Удаляем нерабочий диалог
            if admin_chat_id in active_dialogs:
                del active_dialogs[admin_chat_id]
    
    else:
        # Если админ не в диалоге
        bot.reply_to(message,
            "⚠️ *Вы не в активном диалоге*\n\n"
            "Чтобы ответить пользователю:\n"
            "1. Дождитесь сообщения от пользователя\n"
            "2. Нажмите кнопку '💬 Ответить' под сообщением\n"
            "3. После этого все ваши сообщения будут отправляться этому пользователю\n\n"
            "Используйте /status для проверки статуса\n"
            "Используйте /admin для справки",
            parse_mode='Markdown'
        )

# ========== ЗАПУСК БОТА ==========

def main():
    """Запуск бота"""
    print("=" * 50)
    print("🤖 БОТ ДЛЯ СВЯЗИ С АДМИНИСТРАТОРОМ")
    print("=" * 50)
    print(f"👨‍💼 ID администратора: {ADMIN_ID}")
    print("📱 Режим: Личные сообщения")
    print("\n" + "=" * 50)
    print("🎯 ИНСТРУКЦИЯ:")
    print("=" * 50)
    print("1. ПОЛЬЗОВАТЕЛЬ пишет боту → сообщение приходит АДМИНУ")
    print("2. АДМИН нажимает '💬 Ответить' под сообщением")
    print("3. АДМИН пишет ответ → ответ идет ПОЛЬЗОВАТЕЛЮ")
    print("=" * 50)
    print("\n🚀 Бот запущен. Ожидание сообщений...")
    
    # Запускаем бота
    bot.infinity_polling()

if __name__ == "__main__":
    main()