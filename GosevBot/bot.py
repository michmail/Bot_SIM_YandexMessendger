import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# ========== ТВОЙ ТОКЕН ОТ BOTFATHER ==========
TOKEN = "1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"

# ========== MTProto ПРОКСИ ==========
PROXY = {
    'proxy_type': 'mtproto',  # тип прокси
    'addr': '127.0.0.1',      # адрес (обычно localhost для MTProto)
    'port': 443,              # порт
    'secret': b'7t3_BeZaaaan_RoooooSH_93ZWIuYmFsZS5haQ%3D%3D'  # секрет в байтах
}
# ====================================

CITIES = ['Гусев', 'Черняховск', 'Советск']

def parse_message(text: str):
    for city in CITIES:
        if city.lower() in text.lower():
            patterns = [
                rf'{city}\s*[-:]\s*(\d+)',
                rf'{city}\s+(\d+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return city, int(match.group(1))
    return None, None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    city, count = parse_message(message.text)
    if city and count is not None:
        print(f'Найдено: {city} = {count}')
        await message.reply_text(f'✅ Распознано: {city} = {count} 🛴')
    else:
        await message.reply_text('❌ Не понял. Напиши как "Гусев 5"')

def main():
    # Создаем клиента с MTProto прокси
    client = TelegramClient(
        StringSession(), 
        api_id=1,  # Временный ID
        api_hash='123',  # Временный хеш
        proxy=PROXY
    )
    client.start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print('🤖 Бот запущен через MTProto прокси')
    app.run_polling()

if __name__ == '__main__':
    main()