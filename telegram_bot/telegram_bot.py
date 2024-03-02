import requests
import time
from datetime import datetime
import os
from urllib.parse import urlparse
import psycopg2
import json
import concurrent.futures
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Updater, Application, ContextTypes, filters, ChatMemberHandler
from telegram import  Chat, ChatMember, ChatMemberUpdated, ForceReply, Update, Bot
import telegram
from psycopg2 import sql, extras
import copy
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_server = "http://API:8000"
register_user = API_server + "/bot/register_user"
delete_subscription = API_server + "/bot/delete_subscription"
add_subscription = API_server + "/bot/add_subscription"
get_labelid = API_server + "/bot/get_labelid"
list_subscription = API_server + "/bot/list_subscription"
get_user = API_server + "/bot/get_user"

# Check if the data already exists

insert_query = {}  # Define the insert_query variable
try:
    url = get_user
    user_json = json.loads(requests.post(url).text)
    user = [int(x[0]) for x in user_json]
except:
    user = []

async def UpdateUser(context: ContextTypes.DEFAULT_TYPE) -> None:
    url = get_user
    user_json = json.loads(requests.post(url).text)
    user = [int(x[0]) for x in user_json]


async def AddUser(user_name, user_ids) -> None:
    # Create the INSERT query
    url = register_user
    data = {
        "name": str(user_name),
        "chatid": (user_ids)
    }
    response = requests.post(url, json=data)
    return response.text


        
#Welcome
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    chat_id = update.effective_message.chat_id
    user_name = update.effective_user.full_name
    chat = update.effective_chat
    #context.bot_data.setdefault("user_ids", set()).add(chat.id)
    #user_ids = ", ".join(str(uid) for uid in context.bot_data.setdefault("user_ids", set()))
    if (chat_id not in user): #why it is not str?
        await update.message.reply_text(AddUser(user_name, chat_id))
    await update.message.reply_text("Hi! 歡迎使用")

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

   

#List command
async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id

    url = list_subscription
    data = {
        "chatid": str(chat_id),
    }
    response = requests.post(url, json=data)
    await update.effective_message.reply_text(response.text)

#Init message
async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([('start', '開始使用'),('list', '顯示正在追蹤的標籤')])
    #await application.bot.send_message(str(user[0][0]), "系統啟動")

#Shutdown message
async def post_stop(application: Application) -> None:
    print("Shutting down...")
    #await application.bot.send_message(str(user[0][0]), "系統關閉...")

def main() -> None:
    application = Application.builder().token(TOKEN).post_init(post_init).post_stop(post_stop).build()
    job_queue = application.job_queue
    job_minute = job_queue.run_repeating(UpdateUser, interval=120, first=0)


    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("list", list))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    connection.close()
if __name__ == "__main__":
    main()

