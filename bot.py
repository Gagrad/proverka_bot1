import os
import requests
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import time
import schedule
import threading
from datetime import datetime

# 🔑 Токены из переменных окружения
TOKEN = os.environ.get("TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

# ⚙️ Настройки GitHub
REPO = "Gagrad/tg-samoletvpn1"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# 📁 Шаблон ключей
TEMPLATE = """vless://824fc5dd-4bc9-4db3-901e-686b4d14bc3b@sk-01.probizvpn.com:443?encryption=none&security=reality&sni=sk-01.probizvpn.com&fp=random&pbk=9ITdhrriqT8BTjnyg9L38fFFvV3L0oin3D5D9Aqrd1o&sid=c6ce41466f8c4043&spiderX=%2F&type=tcp&flow=xtls-rprx-vision#🇸🇰 Словакия | За продлением 👇
vless://824fc5dd-4bc9-4db3-901e-686b4d14bc3b@de-01.probizvpn.com:443?encryption=none&security=reality&sni=de-01.probizvpn.com&fp=chrome&pbk=ZMgjoe4oMyF_tcxTvdDwGlOvGkPIij2pQ1d0A3Qajl8&sid=59a7d7265aef033a&spiderX=%2F&type=tcp&flow=xtls-rprx-vision#🇩🇪 Германия | Подписки 👇
vless://824fc5dd-4bc9-4db3-901e-686b4d14bc3b@us-01.probizvpn.com:443?encryption=none&security=reality&sni=us-01.probizvpn.com&fp=random&pbk=3g7PSrdPfyqYHstydDAp027kSV8_BcLSPoGJGI6yxRo&sid=639a8f9635bf5c3f&spiderX=%2F&type=tcp&flow=xtls-rprx-vision#🇺🇸 США | Заходи в бота 👇
vless://824fc5dd-4bc9-4db3-901e-686b4d14bc3b@93.183.82.51:443?encryption=none&security=reality&sni=ru-02.probizvpn.com&fp=random&pbk=Iv6UW1-d_hYK-HEwEQS9uu_IMOiscXEm1F5BHc1WkmU&sid=43344b38424c382b&spiderX=%2F&type=tcp&flow=xtls-rprx-vision#🇷🇺 YouTube | @samoletvpn_bot
vless://824fc5dd-4bc9-4db3-901e-686b4d14bc3b@kz.pbvnet.com:443?encryption=none&security=reality&sni=kz.pbvnet.com&fp=firefox&pbk=5t9e5mgu-vCqGgqpkjLQ7gBGhwoUvNvPGjUFZm90Axo&sid=926179454800a5d9&spiderX=%2F&type=tcp&flow=xtls-rprx-vision#🇰🇿 Казахстан | Канал 👇
vless://8d0b2dc1-42f9-44d8-aec4-ca4ca05f0336@103.27.157.200:8080?type=ws&path=%2Fupload&encryption=none&security=none#🇩🇪 Германия ⚡️ | Бот 👇
vless://88a66608-d1b9-4939-a812-461ac0eb7dde@95sub.ghost-lan.com:443?encryption=none&security=reality&sni=ads.x5.ru&fp=chrome&pbk=13QRazrM7OwuIk4TuCPzasQMP_fHTVM4xikaVP4-KWQ&sid=f23728e727c01887&spiderX=&type=tcp&flow=xtls-rprx-vision#🇷🇺 Обход глушилок и Россия
vless://88a66608-d1b9-4939-a812-461ac0eb7dde@95sub.ghost-lan.com:8444?encryption=none&security=reality&sni=max.ru&fp=chrome&pbk=rgQXJB3AvfhFn2pwyxM9fn0VWuDw95bbNUM-YmuPrHw&sid=ba1f85c54470e904&spiderX=&type=tcp&flow=xtls-rprx-vision#🇪🇪 Обход глушилок и Эстония
vless://88a66608-d1b9-4939-a812-461ac0eb7dde@95sub.ghost-lan.com:8443?encryption=none&security=reality&sni=ads.x5.ru&fp=chrome&pbk=Z-wM5gqK6_RXwYzklavgQlX02-8B2C86_nHVvTktKU4&sid=0d5f755988ec4f39&spiderX=&type=tcp&flow=xtls-rprx-vision#🇳🇱 Обход глушилок и Нидерланды"""

# Хранилище клиентов
clients = {}

# 🚀 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для управления ключами VPN.\n\n"
        "📌 Доступные команды:\n"
        "/newclient Имя - создать нового клиента\n"
        "/delete Имя - удалить клиента\n"
        "/list - список всех клиентов"
    )# 👤 Команда /newclient
async def newclient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Напиши имя клиента: /newclient Имя")
        return
    
    name = context.args[0]
    filename = f"{name}.txt"
    
    # Создаём файл на GitHub
    url = f"https://api.github.com/repos/{REPO}/contents/{filename}"
    content_bytes = TEMPLATE.encode("utf-8")
    data = {
        "message": f"Add {filename}",
        "content": content_bytes.hex()
    }
    
    r = requests.put(url, headers=HEADERS, json=data)
    
    if r.status_code == 201:
        raw_url = f"https://raw.githubusercontent.com/{REPO}/main/{filename}"
        
        # Получаем короткую ссылку через clck.ru
        short = requests.get(f"https://clck.ru/--?url={raw_url}").text
        
        # Сохраняем информацию
        clients[name] = {
            "file": filename,
            "short": short,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "active"
        }
        
        await update.message.reply_text(
            f"✅ Клиент {name} создан!\n\n"
            f"🔗 Короткая ссылка: {short}\n"
            f"📁 Файл: {filename}"
        )
        
        # Уведомление админу
        bot = Bot(token=TOKEN)
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🆕 Новый клиент: {name}\n🔗 {short}"
        )
    else:
        await update.message.reply_text(f"❌ Ошибка: {r.status_code}")

# 🗑️ Команда /delete
async def delete_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Напиши имя клиента: /delete Имя")
        return
    
    name = context.args[0]
    filename = f"{name}.txt"
    
    # Получаем SHA файла
    url = f"https://api.github.com/repos/{REPO}/contents/{filename}"
    r = requests.get(url, headers=HEADERS)
    
    if r.status_code == 200:
        sha = r.json()["sha"]
        
        # Удаляем файл
        data = {
            "message": f"Delete {filename}",
            "sha": sha
        }
        r2 = requests.delete(url, headers=HEADERS, json=data)
        
        if r2.status_code == 200:
            if name in clients:
                clients[name]["status"] = "deleted"
            await update.message.reply_text(f"✅ Клиент {name} удалён")
            
            # Уведомление админу
            bot = Bot(token=TOKEN)
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🗑️ Клиент {name} удалён"
            )
        else:
            await update.message.reply_text("❌ Ошибка при удалении")
    else:
        await update.message.reply_text(f"❌ Клиент {name} не найден")

# 📋 Команда /list
async def list_clients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not clients:
        await update.message.reply_text("📭 Нет активных клиентов")
        return
    
    text = "📋 Список клиентов:\n\n"
    for name, data in clients.items():
        text += f"• {name}\n  🔗 {data['short']}\n  📅 {data['created']}\n  📊 {data['status']}\n\n"
    
    await update.message.reply_text(text)

# 🔍 Фоновая проверка (заглушка)
def check_ips():
    print(f"🔍 Проверка IP... {datetime.now()}")
    # Здесь будет код для проверки TinyURL

def run_schedule():
    schedule.every(6).hours.do(check_ips)
    while True:
        schedule.run_pending()
        time.sleep(60)

# 🧠 Запуск бота
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newclient", newclient))
    app.add_handler(CommandHandler("delete", delete_client))
    app.add_handler(CommandHandler("list", list_clients))
    
    # Запускаем фоновую проверку
    threading.Thread(target=run_schedule, daemon=True).start()
    
    print("✅ Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
[Ссылка]
Яндекс Кликер — Сокращение ссылок
http://clck.ru