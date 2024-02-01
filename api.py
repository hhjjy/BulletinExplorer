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
from pprint import pprint
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# make sure you have run the following command before testing!
# ssh -L 65432:localhost:65432 mitlab@140.118.2.52 -p 33700
# uvicorn api:app --reload

db_config = {
    "database": "mydb",
    "user": "admin",
    "password": "12345",
    "host": "localhost",
    "port": "65432",
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
# get data 
class Post(BaseModel):
    id: int
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

# SELECT *,
#     (CASE WHEN publisher LIKE '%台%' THEN 1 ELSE 0 END +
#      CASE WHEN publisher LIKE '%網%' THEN 1 ELSE 0 END) AS Score
# FROM public.bulletinraw
# WHERE publisher LIKE '%台%' OR publisher LIKE '%網%'
# ORDER BY Score DESC, publish_date DESC, id ASC;
# SQL語法生成
# 輸入台網
def create_sql_query(keywords,number_data):
    case_statements = []
    where_conditions = []
    params = []

    for  keyword in keywords:
        param = f"%{keyword}%"
        case_statements.append(f"(CASE WHEN publisher LIKE %s THEN 1 ELSE 0 END)")
        where_conditions.append(f"publisher LIKE %s")
        params.append(param)
    
    params.extend(params)# 參數再重複一次,原本是[台,網],重複一次就變成 [台,網,台,網] 為了後面SQL搜索時運用到避免遇到SQL注入攻擊
    params.append(number_data) #補上數據資料限制筆數
    case_sql = " + ".join(case_statements)
    where_sql = " OR ".join(where_conditions)

    sql_query = f"""
    SELECT *,
        ({case_sql}) AS Score
    FROM public.bulletinraw
    WHERE {where_sql}
    ORDER BY Score DESC, addtime DESC
    LIMIT %s;
    """
    return sql_query, params
# 取得最新的幾筆資料
## 取得的格式如下 ((ID,發布者,url,content,上傳時間),()...,)
def fetch_data(category: Optional[str], numbers: int):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    if category in (None, "", "all"):  # 检查category是否为空或为'all'
        query = sql.SQL(
            """
                        SELECT * FROM bulletinraw
                        ORDER BY addtime DESC
                        LIMIT %s;
                        """
        )
        cursor.execute(query, (numbers,))
    else:
        SQL_query ,params= create_sql_query(category,numbers)
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
async def get_data(category: Optional[str], numbers: int = Query(default=20, le=200)):
    try:
        raw_data = fetch_data(category, numbers)  # ((id, publisher,),....)
        if not raw_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        data = [
            Post(
                id=row[0],
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
        error_message = '{"error": "%s"}' % Error
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error)},
        )

@app.post("/api/savedata")
async def save_data(post: PostIn):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    try:
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
            return {"message": "Data inserted successfully"}
        else:
            return {"message": "Data already exists. No action taken."}

    except Exception as Error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error)}
        )
    finally:
        if connection:
            cursor.close()
            connection.close()



if __name__ == "__main__":
    # 获取数据库中的所有数据
    all_data = fetch_data("台科大", 100)
    # 使用示例

    # connection = psycopg2.connect(**db_config)
    # cursor = connection.cursor()

    # SQL_query ,params = create_sql_query("台科大主網",10)
    # query = sql.SQL(
    #     SQL_query
    # )
    # cursor.execute(query, params)

    # records = cursor.fetchall()
    # if connection:
    #     cursor.close()
    #     connection.close()
    #     print("PostgreSQL connection is closed")
    # print(records)

    # # 如果关键词改变
    # keywords = ['台', '科', '大']
    # print(create_sql_query(keywords))
