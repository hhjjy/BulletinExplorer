import requests
import time
from datetime import datetime
import os
from urllib.parse import urlparse
import json
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Updater, Application, ContextTypes, filters, ChatMemberHandler
from telegram import  Chat, ChatMember, ChatMemberUpdated, ForceReply, Update, Bot
import telegram
import copy
from decimal import Decimal
from dotenv import load_dotenv


load_dotenv()
mode = os.getenv("DEV_OR_MAIN")  # 默認為開發環境
if mode == "main" or mode == "MAIN":# dev
    print("MAIN MODE")
    API_server =  "http://"+os.getenv("API_MAIN_HOST")+":"+os.getenv("API_MAIN_PORT")
    print(f"LLM API SERVER :{API_server}")
else:
    print(f"Defaulting to DEVELOPMENT MODE.")
    print("DEV MODE ")
    print(os.getenv("API_DEV_HOST"))
    API_server =  "http://"+os.getenv("API_DEV_HOST")+":"+os.getenv("API_DEV_PORT")
    print(f"LLM API SERVER :{API_server}")



TOKEN = os.getenv("TELEGRAM_TOKEN")
register_user = API_server + "/bot/register_user"
delete_subscription = API_server + "/bot/delete_subscription"
add_subscription = API_server + "/bot/add_subscription"
get_labelid = API_server + "/bot/get_labelid"
list_subscription = API_server + "/bot/list_subscription"
get_user = API_server + "/bot/get_user"
get_event_status = API_server + "/bot/get_event_status"
start_event = API_server + "/bot/start_event"
start_scraper = API_server + "/api/start_scraper"
start_llm = API_server + "/api/start_llm"
delete_event = API_server + "/scraper/delete_event"
get_newdata = API_server + "/bot/get_newdata"

user = []

async def update_user(context: ContextTypes.DEFAULT_TYPE) -> None:
    global user  
    url = get_user
    user_json = json.loads(requests.post(url).text)
    user = [int(x[0]) for x in user_json]

async def scraper(context: ContextTypes.DEFAULT_TYPE) -> None:
    url = get_event_status
    data = {
        "function": "scraper"
    }
    response = requests.post(url, json=data)
    
    if response.text[1:-1] == '0':#count of running
        url = start_event
        data = {
            "function": "scraper",
            "status": "1"
        }
        response = requests.post(url, json=data)

        url = start_scraper
        response = requests.post(url)

async def llm(context: ContextTypes.DEFAULT_TYPE) -> None:
    url = get_event_status
    data = {
        "function": "llm"
    }
    response = requests.post(url, json=data)
    
    if response.text[1:-1] == '0':
        url = start_event
        data = {
            "function": "llm",
            "status": "1"
        }
        response = requests.post(url, json=data)

        url = start_llm
        response = requests.post(url)
async def send_new_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    url = get_newdata
    newdata_json = json.loads(requests.post(url).text)
    for i in newdata_json:
        await context.bot.send_message(chat_id=i["chatid"], text = i["url"] + "\n" + i["title"])
        #'<a href="'+ i["url"]  +'">'+i["title"], parse_mode="HTML"



#Welcome
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    chat_id = update.effective_message.chat_id
    user_name = update.effective_user.full_name
    chat = update.effective_chat
    if (chat_id not in user): #why it is not str?
        await update.message.reply_text("Hi! 歡迎使用本機器人")
        url = register_user
        data = {
            "name": str(user_name),
            "chatid": str(chat_id)
        }
        response = requests.post(url, json=data)
        await update.message.reply_text("指令如下：\n/search [標籤名稱] - 搜尋標籤\n/subscribe [標籤名稱] - 訂閱標籤\n/unsubscribe [標籤名稱] - 取消訂閱標籤\n/list - 顯示正在追蹤的標籤")
    await update.message.reply_text("你已經註冊過了")

#check where do bot run(for debug)
async def whereami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    my_ip = requests.get("https://ifconfig.me/").text
    await update.effective_message.reply_text(my_ip)

#search command
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    await update.effective_message.reply_text("search")

#subscribe command
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        label_name = update.message.text.split(' ')[1:][0]#chinese not work
    except:
        await update.effective_message.reply_text("Please enter the topic name")
        return
    
    url = get_labelid
    data = {
        "labelname": label_name
    }
    response = requests.post(url, json=data)
    labelid = response.text[1:-1]

    if (labelid == "ul"):#bcs null[1] -> [u]
        await update.effective_message.reply_text("topic not exist")
    else:
        url = add_subscription
        data = {
            "chatid": str(chat_id),
            "labelid": str(labelid)
        }
        response = requests.post(url, json=data)
        await update.effective_message.reply_text("Subscribe topic successfully")


#unsubscribe command
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        label_name = update.message.text.split(' ')[1:][0]
    except:
        await update.effective_message.reply_text("Please enter the topic name")
        return
    url = get_labelid
    data = {
        "labelname": label_name
    }
    response = requests.post(url, json=data)
    labelid = response.text[1:-1]

    if (labelid == "ul"):#bcs null[1] -> [u]
        await update.effective_message.reply_text("topic not exist")
    else:
        url = delete_subscription
        data = {
            "chatid": str(chat_id),
            "labelid": str(labelid)
        }
        response = requests.post(url, json=data)
        await update.effective_message.reply_text(response.text)

   

#List all subscribe command
async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id

    url = list_subscription
    data = {
        "chatid": str(chat_id),
    }
    response = requests.post(url, json=data)
    await update.effective_message.reply_text(response.text)

#boot message & set instruction
async def post_init(application: Application) -> None:
    # for start-up
    url = delete_event
    data = {
        "function": "scraper",
        "status": "2"
    }
    response = requests.post(url, json=data)
    url = delete_event
    data = {
        "function": "llm",
        "status": "2"
    }
    response = requests.post(url, json=data)
    await application.bot.set_my_commands([('start', '開始使用'),('list', '顯示正在追蹤的標籤')])
    #await application.bot.send_message(str(user[0][0]), "系統啟動")

#Shutdown message
async def post_stop(application: Application) -> None:
    print("Shutting down...")
    #await application.bot.send_message(str(user[0][0]), "系統關閉...")

def main() -> None:
    application = Application.builder().token(TOKEN).post_init(post_init).post_stop(post_stop).build()
    job_queue = application.job_queue
    job_minute = job_queue.run_repeating(update_user, interval=30, first=3)
    job_minute = job_queue.run_repeating(scraper, interval=15, first=3)
    job_minute = job_queue.run_repeating(llm, interval=15, first=3)
    job_minute = job_queue.run_repeating(send_new_data, interval=20, first=10)


    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("whereami", whereami))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("list", list))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__ == "__main__":
    main()

