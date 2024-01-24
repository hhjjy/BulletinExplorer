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
#####PostgreSQL setup
db_config = {
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": "localhost",
    "port": os.getenv("POSTGRES_PORT")
}
connection = psycopg2.connect(**db_config)
cursor = connection.cursor() #Init. connection

# Check if the data already exists

insert_query = {}  # Define the insert_query variable
insert_query["updateUser"] = sql.SQL("""
    SELECT chatid FROM account
""")
cursor.execute(insert_query["updateUser"])
user_json = cursor.fetchall()
user = [int(x[0]) for x in user_json]

async def UpdateUser(context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor.execute(insert_query["updateUser"])
    user_json = cursor.fetchall()
    user = [int(x[0]) for x in user_json]

insert_query["addUser"] = sql.SQL("""
    INSERT INTO account (name, chatid)
    VALUES (%s, %s)
""")
insert_query["getTopic"] = sql.SQL("""
    SELECT topicname FROM subscription s
    INNER JOIN topics ON topics.topicid = s.topicid 
    WHERE s.chatid = %s AND s.status = 'Subscribed';
""")
insert_query["checkTopicExist"] = sql.SQL("""
    SELECT topicid
    FROM topics
    WHERE topicname = %s;
""")
insert_query["checkSubscription"] = sql.SQL("""
    SELECT s.topicid FROM public.subscription s 
    JOIN public.account a ON s.userid = a.userid 
    WHERE a.chatid = %s AND s.topicid = %s;
""")
# insert_query["Subscription"] = sql.SQL("""
#     INSERT INTO public.subscription (chatid, topicid, status, notificationpreference)
#     SELECT %s, %s, 'Subscribed', 'telegram'
#     ON CONFLICT (chatid, topicid) DO NOTHING;
# """)
insert_query["Subscription"] = sql.SQL("""
    INSERT INTO public.subscription (chatid, topicid, status, notificationpreference)
    VALUES (%s, %s, 'Subscribed', 'telegram')
    ON CONFLICT (chatid, topicid) DO UPDATE 
    SET status = 'Subscribed'
    WHERE public.subscription.status = 'Unsubscribed'
    RETURNING *;
""")
insert_query["unSubscription"] = sql.SQL("""
    UPDATE public.subscription
    SET status = 'Unsubscribed'
    WHERE chatid = %s AND topicid = %s;
""")

async def AddUser(user_name, user_ids) -> None:
    # Create the INSERT query
    cursor.execute(insert_query["addUser"], (user_name, user_ids))
    connection.commit()

        
#Welcome
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    user_name = update.effective_user.full_name
    chat = update.effective_chat
    context.bot_data.setdefault("user_ids", set()).add(chat.id)
    user_ids = ", ".join(str(uid) for uid in context.bot_data.setdefault("user_ids", set()))
    if (str(user_ids) not in str(user)): #why it is not str?
        await AddUser(user_name, user_ids)
        await update.message.reply_text("New User")
    await update.message.reply_text("Hi! 歡迎使用")

#search command
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    await update.effective_message.reply_text("search")

#subscribe command
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    topicname = update.message.text.split(' ')[1:][0]
    cursor.execute(insert_query["checkTopicExist"], (topicname,))
    connection.commit()
    topicid = cursor.fetchone()
    if (topicid == None):
        await update.effective_message.reply_text("topic not exist")
    else:
        cursor.execute(insert_query["Subscription"], (chat_id, topicid))
        connection.commit()
        await update.effective_message.reply_text("Subscribe topic successfully")

    

#unsubscribe command
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    topicname = update.message.text.split(' ')[1:][0]
    cursor.execute(insert_query["checkTopicExist"], (topicname,))
    connection.commit()
    topicid = cursor.fetchall()[0][0]
    cursor.execute(insert_query["unSubscription"], (chat_id, topicid))
    connection.commit()
    await update.effective_message.reply_text("unsubscribe")

#List command
async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    cursor.execute(insert_query["getTopic"], (chat_id,))
    connection.commit()
    await update.effective_message.reply_text(cursor.fetchall())

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

