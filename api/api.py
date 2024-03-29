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
import subprocess
import asyncio
import scraper

load_dotenv()
# make sure you have run the following command before testing!
# ssh -L 65432:localhost:65432 mitlab@140.118.2.52 -p 33700
# uvicorn api:app --reload
from log_config import setup_logger
import logging,traceback
logger = setup_logger("api_service", log_level=logging.DEBUG)
mode = os.getenv("DEV_OR_MAIN")  # 默認為開發環境 
if mode == "main" or mode == "MAIN":# dev 
    print("MAIN MODE")
    db_config = {
            "database": os.getenv("POSTGRES_MAIN_DB"),
            "user": os.getenv("POSTGRES_MAIN_USER"),
            "password": os.getenv("POSTGRES_MAIN_PASSWORD"),
            "host": os.getenv("POSTGRES_MAIN_HOST"),
            "port": os.getenv("POSTGRES_MAIN_PORT")
        }
else:
    print(f"Unrecognized mode: {mode}. Defaulting to DEVELOPMENT MODE.")
    print("DEV MODE ")
    db_config = {
        "database": os.getenv("POSTGRES_DEV_DB"),
        "user": os.getenv("POSTGRES_DEV_USER"),
        "password": os.getenv("POSTGRES_DEV_PASSWORD"),
        "host": os.getenv("POSTGRES_DEV_HOST"),
        "port": os.getenv("POSTGRES_DEV_PORT")
    }
    

# print(db_config)
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
# LLM save llm labels 
class LabelSaveDB(BaseModel):
    rawid:str
    labelid:str 
# LLM get label define 
#SELECT * FROM label LIMIT 100
    
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
class DataForLLM(BaseModel):
    rawid: int
    publisher: str
    title: str
    url: str
    content: str
class Coordinate(BaseModel):
    function: str
    status: str
class CheckCoordinate(BaseModel):
    function: str
# 取得原始公告
class GetRawTable(BaseModel):
    publisher: Optional[str] = None
    keywords: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    numbers: int = 20
# 取得標籤後資訊
class GetProcessedTable(BaseModel):
    search_label: Optional[str] = None
    publisher: Optional[str] = None
    keywords: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    numbers: int = 20
# 新增標籤後資訊
class AddProcessedTable(BaseModel):
    rawid: int
    labelid: int
# 取得label table
class GetLabelTable(BaseModel):
    labelid: int
    labelname: str
    description: str

# 日期範圍調整
def adjust_date_range(start_date_str, end_date_str):
    try:
        if start_date_str and end_date_str:  # 確保日期不為空
            logger.info(f"input {start_date_str}~{end_date_str}")
            # 將字符串轉換為 datetime 對象
            start_date_o = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date_o = datetime.strptime(end_date_str, "%Y-%m-%d")
            # 將結束日期增加一天
            end_date_o += timedelta(days=1)
            # 如果需要，將 datetime 對象轉換回字符串
            end_date_str = end_date_o.strftime("%Y-%m-%d")
            logger.info(f"return {start_date_str}~{end_date_str}")
            return start_date_str, end_date_str
        else:
            logger.info("Empty date strings provided")
            return None, None
    except ValueError as e:
        logger.error(f"Error in adjusting date range: {e}")
        raise ValueError("Invalid date format provided")

def create_sql_query(publisher, keywords, number_data, start_date, end_date, table):
    case_statements = []
    where_conditions = []
    params = []

    if start_date is not None and end_date is not None: # 調整時間
        start_date, end_date = adjust_date_range(start_date, end_date)

    if publisher: # 搜尋發布者關鍵字
        for publish in publisher:
            param = f"%{publish}%"
            case_statements.append(f"(CASE WHEN publisher LIKE %s THEN 1 ELSE 0 END)")
            where_conditions.append(f"publisher LIKE %s")
            params.append(param)

        params.extend(params) # 參數再重複一次,原本是[台,網],重複一次就變成 [台,網,台,網] 為了後面SQL搜索時運用到避免遇到SQL注入攻擊
        params.extend([number_data] if start_date is None or end_date is None  else [start_date, end_date, number_data])
        case_sql = " + ".join(case_statements)
        where_sql = " OR ".join(where_conditions)
        where_date_sql = "" if start_date is None and end_date is None else f"AND ( addtime >= %s AND addtime < %s)"

        sql_query = f"""
            SELECT *,
            ({case_sql}) AS Score
            FROM {table}
            WHERE ({where_sql}) {where_date_sql}
            ORDER BY Score DESC, addtime DESC
            LIMIT %s;
        """ 
        
    elif keywords: # 搜尋內文關鍵字
        for keyword in keywords:
            param = f"%{keyword}%"
            where_conditions.append(f"content LIKE %s")
            params.append(param)

        params.extend([number_data] if start_date is None or end_date is None  else [start_date, end_date, number_data])
        where_sql = " OR ".join(where_conditions)
        where_date_sql = "" if start_date is None or end_date is None else f"AND ( addtime >= %s AND addtime < %s)"
        
        sql_query = f"""
            SELECT * FROM {table}
            WHERE ({where_sql}) {where_date_sql}
            ORDER BY addtime DESC
            LIMIT %s;
        """

    else: # 兩者都沒有
        where_date_sql = "" if start_date is None or end_date is None else f"WHERE ( addtime >= %s AND addtime < %s)"
        sql_query = f"""
            SELECT * FROM {table}
            {where_date_sql}
            ORDER BY addtime DESC
            LIMIT %s;
        """
        params.extend([number_data] if start_date is None or end_date is None  else  [start_date, end_date, number_data] )
    
    logger.debug(f"sql_query:{sql_query}, params:{params}")
    return sql_query, params

# 取得最新的幾筆資料
# 取得的格式如下 ((rawid, publisher, title, url, content, addtime),()...,)
def fetch_data(publisher: str, keywords: str, numbers: int, start_date: str, end_date: str, table: str):
    logger.debug(f"publisher:{publisher}, keywords:{keywords}, numbers:{numbers}, start_date:{start_date}, end_date:{end_date}")
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    SQL_query ,params = create_sql_query(publisher, keywords, numbers, start_date, end_date, table)
    query = sql.SQL(SQL_query)
    cursor.execute(query, params)
    records = cursor.fetchall()
    if connection:
        cursor.close()
        connection.close()
    return records

# 測試過中文的參數進入fastapi會自動處理不須轉換
# 取得原始公告資料  
@app.post("/frontend/get_bulletin", response_model=List[Post])
async def get_bulletin(post: GetRawTable):
    try:
        publisher = post.publisher
        keywords = post.keywords
        start_date = post.start_date
        end_date = post.end_date
        numbers = post.numbers
        search_type = "ALL" if not keywords and not publisher else ("keywords" if keywords else "publisher")
        logger.info(f"Fetching {numbers} latest posts with {search_type} from Date:{start_date}~{end_date}")

        raw_data = fetch_data(publisher, keywords, numbers, start_date, end_date, "bulletinraw")  # ((id, publisher,),....)
        data = [
            Post(
                rawid = row[0],
                publisher = row[1],
                title = row[2],
                url = row[3],
                content = row[4],
                addtime = row[5],
            )
            for row in raw_data
        ]
        return data
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )

# 刪除原始公告資料
@app.post("/frontend/delete_bulletin")
async def delete_bulletin(rawid: int):
    logger.info(f"Deleting data {rawid} from the database")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # 查詢公告是否存在
        cursor.execute("""
            DELETE FROM bulletinraw
            WHERE rawid = %s
            RETURNING rawid
        """, (rawid,))
        # 獲取刪除的行數
        deleted_rows = cursor.rowcount
        # 檢查是否刪除成功
        if deleted_rows > 0:
            connection.commit()
            logger.info(f"Deletion completed")
            return {"message": "Data successfully deleted"}
        else:
            # 如果公告不存在，則引發HTTP異常
            raise HTTPException(status_code=404, detail="Data not found")

    except Exception as Error:
        error_message = "An error occurred during deletion: {}".format(str(Error))
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

# 修改原始公告資料
@app.post("/frontend/modify_bulletin")
async def modify_bulletin(rawid: int, post: PostIn):
    logger.info(f"Modifying bulletin with rawid: {rawid}")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # 檢查要修改的公告是否存在
        cursor.execute("""
            SELECT * FROM bulletinraw
            WHERE rawid = %s
        """, (rawid,))
        connection.commit()
        existing_post = cursor.fetchone()

        if existing_post:
            # 修改公告資料
            cursor.execute("""
                UPDATE bulletinraw
                SET publisher = %s, title = %s, url = %s, content = %s
                WHERE rawid = %s
            """, (post.publisher, post.title, post.url, post.content, rawid,))
            connection.commit()
            logger.info(f"Modification in progress")
            return {"message": "Data is being modified"}
        else:
            # 如果公告不存在，則引發 HTTP 異常
            raise HTTPException(status_code=404, detail="Data not found")

    except Exception as Error:
        error_message = "Error occurring during modification: {}".format(str(Error))
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

# 查詢標籤對應的 rawid 函數
def get_rawid_by_label(search_label, cursor):
    sql_query = f"""
        SELECT DISTINCT rawid FROM bulletinprocessed WHERE labelid = (
            SELECT labelid FROM label WHERE labelname = %s
        )
    """
    logger.debug(f"sql_query:{sql_query}, params:{search_label}")
    cursor.execute(sql_query, [search_label])
    rawids = cursor.fetchall()
    return [rawid[0] for rawid in rawids] if rawids else []

# 取得 rawid 對應的資料函數
def get_data_by_rawid(rawids, cursor):
    if not rawids:
        return []  # 如果 rawids 為空，直接返回空列表
    sql_query = """
        SELECT rawid, publisher, title, url FROM bulletinraw WHERE rawid IN %s
    """
    logger.debug(f"sql_query:{sql_query}")
    cursor.execute(sql_query, [tuple(rawids)])
    data = cursor.fetchall()
    return data

# 取得標籤後資料
@app.post("/frontend/get_processed_table")
async def get_processed_table(post: GetProcessedTable):
    try:
        search_label = post.search_label
        publisher = post.publisher
        keywords = post.keywords
        start_date = post.start_date
        end_date = post.end_date
        numbers = post.numbers
        
        logger.debug(f"search_label:{search_label}, publisher:{publisher}, keywords:{keywords}, start_date:{start_date}, end_date:{end_date}, numbers:{numbers}")
        
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        rawids = get_rawid_by_label(search_label, cursor)
        raw_data = get_data_by_rawid(rawids, cursor)
        
        data = [
            {
                "rawid": row[0],
                "publisher": row[1],
                "title": row[2],
                "url": row[3]
            }
            for row in raw_data
        ]

        if connection:
            cursor.close()
            connection.close()

        return data
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )

# 新增標籤後資料
@app.post("/frontend/add_processed_table")
async def add_processed_table(post: AddProcessedTable):
    try:
        rawid = post.rawid
        labelid = post.labelid
        
        logger.debug(f"rawid:{rawid}, labelid:{labelid}")
        
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # 檢查要新增的的公告、標籤是否存在
        cursor.execute("""
            SELECT * FROM bulletinprocessed
            WHERE rawid = %s AND labelid = %s
        """, (rawid, labelid))
        connection.commit()
        existing_post = cursor.fetchone()
            
        if existing_post:
            # 標籤&公告已存在
            logger.info(f"Data already exist")
            return {"message": "Data already exist"}
        else:
            # 如果標籤&公告不存在，則新增標籤後資料
            cursor.execute("""
                INSERT INTO bulletinprocessed
                (rawid, labelid) VALUES (%s, %s)
            """, (rawid, labelid))
            logger.info(f"Add rawid: {rawid}, labelid: {labelid}")
            connection.commit()
            return {"message": f"Add rawid: {rawid}, labelid: {labelid}"}     

    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )

    finally:
        if connection:
            cursor.close()
            connection.close()

# 刪除標籤後資料
@app.post("/frontend/delete_processed_table")
async def delete_processed_table(id: int):
    logger.info(f"Deleting data {id} from the database")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # 查詢公告是否存在
        cursor.execute("""
            DELETE FROM bulletinprocessed
            WHERE id = %s
            RETURNING id
        """, (id,))
        # 獲取刪除的行數
        deleted_rows = cursor.rowcount
        # 檢查是否刪除成功
        if deleted_rows > 0:
            connection.commit()
            logger.info(f"Deletion completed")
            return {"message": "Data successfully deleted"}
        else:
            # 如果公告不存在，則引發HTTP異常
            raise HTTPException(status_code=404, detail="Data not found")

    except Exception as Error:
        error_message = "An error occurred during deletion: {}".format(str(Error))
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

# requests.post(f"{self.api_endpoint}/llm/save_label", json=response_dict)
class processtable(BaseModel):
    rawid:int 
    labelid:int

@app.post('/llm/save_label')
async def save_label(input:processtable):
    try:
        logger.info(f"input:{input}")
        rawid = input.rawid
        labelid = input.labelid
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO bulletinprocessed (rawid, labelid) VALUES (%s, %s)", (rawid, labelid))
        connection.commit() # commit 很重要！
        if connection:
            cursor.close()
            connection.close()
        logger.info(f"output:成功插入！")
        return {"message":"Label ID INSERT SUCESSFULLY!","detail":""}
    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(Error),"detail":error_traceback},
        )

# 取得label table整個資料表
@app.post('/llm/get_label_table')
async def get_label_table():
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # 執行 SQL 查詢
        cursor.execute("SELECT * FROM label")
        rows = cursor.fetchall()

        # 將查詢結果轉換為自定義的 GetLabelTable 物件列表
        data = [
            GetLabelTable(
                labelid=row[0],
                labelname=row[1],
                description=row[2]
            )
            for row in rows
        ]

        return data

    except Exception as Error:
        error_message = "Error occurring during modification: {}".format(str(Error))
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

@app.post("/scraper/save_bulletin")
async def save_bulletin(post: PostIn):
    logger.info(f"Saving post {post} to database")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在你好
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


@app.post("/llm/get_unprocessed_data", response_model=List[DataForLLM])
async def get_unprocessed_data():
    try:
        logger.info(f"Fetching Unprocess Data")
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            SELECT br.rawid, br.publisher, br.title, br.url, br.content
            FROM public.bulletinraw br
            LEFT JOIN public.bulletinprocessed bp ON br.rawid = bp.rawid
            WHERE bp.rawid IS NULL;
        """, )
        
        records = cursor.fetchall()
        data = [
            DataForLLM(
                rawid=row[0],
                publisher=row[1],
                title=row[2],
                url=row[3],
                content=row[4],
            )
            for row in records
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
    finally:
        if connection:
            cursor.close()
            connection.close()


@app.post("/bot/start_event")
async def start_event(post: Coordinate):
    logger.info(f"{post.function} is running {post.status}")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            INSERT INTO public.coordinates (function, start)
            VALUES (%s, %s);
        """, (post.function, post.status))
        connection.commit()
        logger.info(f"{post.function} records {post.status} Done")
        return {f"Start"}

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


@app.post("/scraper/delete_event")
async def delete_event(post: Coordinate):
    logger.info(f"{post.function} is deleting")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在

            # INSERT INTO public.coordinates (function, start)
            # VALUES (%s, %s);
        # cursor.execute("""
                       
        #     DO $$
        #     BEGIN
        #         -- Check if there is only one row meeting the conditions
        #         IF (SELECT COUNT(*) FROM public.coordinates WHERE function = %s AND start = 1 AND finish = false) = 1 THEN
        #             -- Update the 'finish' column to 1 for the specified conditions
        #             UPDATE public.coordinates
        #             SET finish = true
        #             WHERE function = %s AND start = 1 AND finish = false;
        #         ELSE
        #             -- Return an error message if there are not exactly one row matching the conditions
        #             RAISE EXCEPTION 'More than one row or no row found matching the specified conditions';
        #         END IF;
        #     END $$;
        # """, (post.function, post.status))
        cursor.execute("""
            UPDATE public.coordinates
            SET finish = true,
                start = 2
            WHERE function = %s AND start = 1 AND finish = false;
        """, (post.function, ))
        connection.commit()
        logger.info(f"{post.function} Delete Done")
        return {f"Delete {post.function}"}

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

@app.post("/bot/get_event_status")
async def get_event_status(post: CheckCoordinate):
    logger.info(f"Checking can {post.function} start")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            SELECT COUNT(*)
            FROM public.coordinates
            WHERE function = %s AND start = 1 AND finish = false;
        """, (post.function,))
        count = cursor.fetchone()
        connection.commit()
        logger.info(f"{count} of {post.function} can running")
        return count

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


@app.post("/bot/list_event")
async def list_event():
    logger.info(f"Listing all event not completed")
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        # 檢查數據是否已存在
        cursor.execute("""
            select * from coordinates
            where start = '1' and finish = false;
        """, )
        connection.commit()
        logger.info(f"Querry Done")
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
    finally:
        if connection:
            cursor.close()
            connection.close()


@app.post("/api/start_scraper")
async def start_scraper():
    try:
        logger.info(f"Start Scraper")
        process = await asyncio.create_subprocess_exec(
            "python3", "-c", "from scraper import scrape; scrape()",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if stdout:
            logger.info(f"Scraper output: {stdout.decode()}")
        if stderr:
            logger.error(f"Scraper error: {stderr.decode()}")
        return {"message": "Scraper run finish."}


    except Exception as Error:
        error_message = "Error occurred: {}".format(str(Error))
        error_traceback = traceback.format_exc()
        logger.error("%s\n%s", error_message, error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error),"detail":error_traceback},
        )

if __name__ == "__main__":
    # print("1234")
    # connection = psycopg2.connect(**db_config)
    print(db_config)
    # app_env = os.getenv("APP_ENV", "DEV_OR_MAIN")  # 默认为开发环境
    # print(app_env)
    # data = fetch_data(None, 5,'2024-01-01',None)
    # pprint(data)