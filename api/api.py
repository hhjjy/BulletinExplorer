"""
Author: Leo lion24161582@gmail.com
Date: 2024-01-25 10:12:50
LastEditors: Leo lion24161582@gmail.com
LastEditTime: 2024-01-25 16:19:58
FilePath: \BulletinExplorer\api.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""

import psycopg2
from psycopg2 import sql
import os
from pprint import pprint
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse,RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()


# make sure you have run the following command before testing!
# ssh -L 65432:localhost:65432 mitlab@140.118.2.52 -p 33700
# uvicorn api:app --reload
from log_config import setup_logger
import logging,traceback
logger = setup_logger("api_service", log_level=logging.DEBUG)

db_config = {
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": "MyPostgres",
    "port": "5432"
}

app = FastAPI()

# 加入 CORSMiddleware 以處理跨來源請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允許所有來源，你也可以指定特定的來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 HTTP 標頭
)
@app.get("/")
async def root():
    return RedirectResponse(url='/docs')

# get data 
class Post(BaseModel):
    rawid: int
    publisher: str
    title: str
    url: str
    content: str
    addtime: datetime
# save data 
class PostIn(BaseModel):
    publisher: str
    title: str
    url: str
    content: str

class NewUser(BaseModel):
    name: str
    chatid: str
class Subribe(BaseModel):
    chatid: str
    labelid: str
class GetLabelid(BaseModel):
    labelname: str
class UserId(BaseModel):
    chatid: str
class ListSubTable(BaseModel):
    labelname: str
class NewDataReturn(BaseModel):
    chatid: int
    publisher: str
    title: str
    url: str
    labelname: str

# SELECT *,
#      (CASE WHEN publisher LIKE '%台%' THEN 1 ELSE 0 END +
#       CASE WHEN publisher LIKE '%網%' THEN 1 ELSE 0 END) AS Score
# FROM public.bulletinraw
# WHERE (addtime >= '2023-01-01' AND addtime <= '2024-01-21')
# and (publisher LIKE '%台%' OR publisher LIKE '%網%')
# ORDER BY Score DESC, addtime DESC, id ASC;
# 輸入台網

def adjust_date_range(start_date_str,end_date_str):
    logger.info(f"input {start_date_str}~{end_date_str}")
    # 將字符串轉換為 datetime 對象
    start_date_o = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date_o = datetime.strptime(end_date_str, "%Y-%m-%d")
    # 將結束日期增加一天
    end_date_o += timedelta(days=1)
    # 如果需要，將 datetime 對象轉換回字符串
    end_date_str = end_date_o.strftime("%Y-%m-%d")
    logger.info(f"return {start_date_str}~{end_date_str}")
    return start_date_str,end_date_str
def create_sql_query(keywords,number_data,start_date,end_date):
    case_statements = []
    where_conditions = []
    params = []
    if start_date is not None and end_date is not None :#調整時間！
        start_date,end_date = adjust_date_range(start_date,end_date)
    if keywords:#有關鍵字
        for  keyword in keywords:
            param = f"%{keyword}%"
            case_statements.append(f"(CASE WHEN publisher LIKE %s THEN 1 ELSE 0 END)")
            where_conditions.append(f"publisher LIKE %s")
            params.append(param)
        params.extend(params)# 參數再重複一次,原本是[台,網],重複一次就變成 [台,網,台,網] 為了後面SQL搜索時運用到避免遇到SQL注入攻擊
        params.extend([number_data] if start_date is None or end_date is None  else  [start_date,end_date,number_data])
        case_sql = " + ".join(case_statements)
        where_sql = " OR ".join(where_conditions)
        where_date_sql = "" if start_date is None and end_date is None else f"AND ( addtime >= %s AND addtime < %s)"

        sql_query = f"""
        SELECT *,
            ({case_sql}) AS Score
        FROM public.bulletinraw
        WHERE ({where_sql}) {where_date_sql}
        ORDER BY Score DESC, addtime DESC
        LIMIT %s;
        """ 
    else :#沒有關鍵字
        where_date_sql = "" if start_date is None or end_date is None else f"WHERE ( addtime >= %s AND addtime < %s)"
        sql_query = f"""
                SELECT * FROM bulletinraw
                {where_date_sql}
                ORDER BY addtime DESC
                LIMIT %s;
            """
        params.extend([number_data] if start_date is None or end_date is None  else  [start_date,end_date,number_data] )
    logger.debug(f"sql_query:{sql_query},params:{params}")
    return sql_query, params
# 取得最新的幾筆資料
## 取得的格式如下 ((ID,發布者,url,content,上傳時間),()...,)
def fetch_data(category: str,numbers:int, start_date: str, end_date: str):
    logger.debug(f"category:{category},numbers:{numbers},start_date:{start_date},end_date:{end_date}")
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    SQL_query ,params= create_sql_query(category,numbers,start_date,end_date)
    query = sql.SQL(
        SQL_query
    )
    cursor.execute(query, params)
    records = cursor.fetchall()
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
    return records
# 測試過中文的參數進入fastapi會自動處理不須轉換
@app.get("/api/getdata", response_model=List[Post])
async def get_data(category: Optional[str] = None, start_date:Optional[str]= None,end_date:Optional[str]= None,numbers: int = Query(default=20, le=200)):
    try:
        logger.info(f"Fetching {numbers} latest posts from {category} ,Date:{start_date}~{end_date}")
        raw_data = fetch_data(category, numbers,start_date,end_date)  # ((id, publisher,),....)
        data = [
            Post(
                rawid=row[0],
                publisher=row[1],
                title=row[2],
                url=row[3],
                content=row[4],
                addtime=row[5],
            )
            for row in raw_data
        ]
        return data
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )

@app.post("/scraper/save_bulletin")
async def save_data(post: PostIn):
    logger.info(f"Saving post {post} to database")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            SELECT * FROM bulletinraw
            WHERE publisher = %s AND title = %s
        """, (post.publisher, post.title))
        if cursor.fetchone() is None:
            # 如果數據不存在，則插入新數據
            cursor.execute("""
                INSERT INTO bulletinraw (publisher, title, url, content)
                VALUES (%s, %s, %s, %s)
            """, (post.publisher, post.title, post.url, post.content))
            connection.commit()
            logger.info(f"Saving Done")
            return {"message": "Data inserted successfully"}
        else:
            logger.info(f"Data already exists. No action taken.")
            return {"message": "Data already exists. No action taken."}

    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )
    finally:
        if connection:
            cursor.close()
            connection.close()



@app.post("/bot/register_user")
async def register_user(post: NewUser):
    logger.info(f"Add user {post.name} {post.chatid} to database")
    try:

        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            SELECT * FROM account
            WHERE name = %s AND chatid = %s
        """, (post.name, post.chatid))

        if cursor.fetchone() is None:
            # 如果數據不存在，則插入新數據
            cursor.execute("""
                INSERT INTO account (name, chatid)
                VALUES (%s, %s)
            """, (post.name, post.chatid))
            connection.commit()
            logger.info(f"Add user Done")
            return {f"Welcome New User"}
        else:
            logger.info(f"User already exists. No action taken.")
            return {f"User already exists. No action taken."}

    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.post("/bot/delete_subscription")
async def delete_subscription(post: Subribe):
    logger.info(f"{post.chatid} is Unsubscribe {post.labelid}")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            UPDATE public.subscription
            SET status = 'Unsubscribed'
            WHERE chatid = %s AND labelid = %s;
        """, (post.chatid, post.labelid))
        connection.commit()
        logger.info(f"{post.chatid} Unsubscribe {post.labelid} Done")
        return {f"Unsubscribe successfully"}

    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.post("/bot/add_subscription")
async def add_subscription(post: Subribe):
    logger.info(f"{post.chatid} is Subscribe {post.labelid}")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            INSERT INTO public.subscription (chatid, labelid, status, notificationpreference)
            VALUES (%s, %s, 'Subscribed', 'telegram')
            ON CONFLICT (chatid, labelid) DO UPDATE 
            SET status = 'Subscribed'
            WHERE public.subscription.status = 'Unsubscribed'
            RETURNING *;
        """, (post.chatid, post.labelid))
        connection.commit()
        logger.info(f"{post.chatid} Subscribe {post.labelid} Done")
        return {f"Subscribe successfully"}
    

    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"發生錯誤"},
        )
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.post("/bot/get_labelid")
async def get_labelid(post: GetLabelid):
    try:
        logger.info(f"{post} is queriying label name")
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            SELECT labelid
            FROM label
            WHERE labelname = %s;
        """, (post.labelname, ))#so weird
        connection.commit()
        label_name = cursor.fetchone()
        logger.info(f"get labelid Done {label_name}")
        return label_name
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )

@app.post("/bot/list_subscription")#, response_model=List[ListSubTable])
async def list_subscription(post:UserId):
    try:
        logger.info(f"{post.chatid} is listing subscription")

        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            SELECT labelname FROM subscription s
            INNER JOIN label ON label.labelid = s.labelid 
            WHERE s.chatid = %s AND s.status = 'Subscribed';
            
        """, (post.chatid, ))#so weird

        records = cursor.fetchall()
        return records
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )
@app.post("/bot/get_user")#, response_model=List[ListSubTable])
async def get_user():
    try:
        logger.info(f"getting user chatid")

        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            SELECT chatid FROM account
        """,)#so weird

        records = cursor.fetchall()
        return records
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )


@app.post("/bot/get_newdata", response_model=List[NewDataReturn])
async def get_newdata():
    try:
        logger.info(f"Fetching Unsent Data")
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            SELECT DISTINCT ON (s.chatid, br.rawid) s.chatid, br.publisher, br.title, br.url, l.labelname, br.rawid
            FROM subscription s
            JOIN bulletinprocessed bp ON s.labelid = bp.labelid
            JOIN bulletinraw br ON bp.rawid = br.rawid
            JOIN label l ON s.labelid = l.labelid
            WHERE bp.sentstatus = 'f' AND s.status = 'Subscribed';

        """, )
        records = cursor.fetchall()
        data = [
            NewDataReturn(
                chatid=row[0],
                publisher=row[1],
                title=row[2],
                url=row[3],
                labelname=row[4],
            )
            for row in records
        ]

        cursor.execute("""
            UPDATE bulletinprocessed
            SET sentstatus = 't'
            WHERE sentstatus = 'f';
        """, )
        connection.commit()
        logger.info(f"Set all `sentstatus` to True")
        return data
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.post("/api/start_scraper")
async def start_scraper():
    try:
        logger.info(f"Start Scraper")
        os.system("python3 ../scraper.py")  # call scraper


        return "Done"
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )


if __name__ == "__main__":
 
    data = fetch_data(None, 5,'2024-01-01',None)
    pprint(data)