'''
Author: Leo lion24161582@gmail.com
Date: 2024-01-25 10:12:50
LastEditors: Leo lion24161582@gmail.com
LastEditTime: 2024-01-25 16:19:58
FilePath: \BulletinExplorer\api.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

import psycopg2
from psycopg2 import sql
from pprint import pprint
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
# uvicorn api:app --reload 
db_config = {
    "database": "mydb",
    "user": "admin",
    "password": "12345",
    "host": "localhost",
    "port": "65432"
}
## 取得最新的幾筆資料 
## 取得的格式如下 ((ID,發布者,url,content,上傳時間),()...,)
def fetch_data(category: Optional[str], numbers: int):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    if category in (None, "", "all"):  # 检查category是否为空或为'all'
        query = sql.SQL("""
                        SELECT * FROM bulletinraw
                        ORDER BY addtime DESC
                        LIMIT %s;
                        """)
        cursor.execute(query, (numbers,))
    else:
        query = sql.SQL("""
                        SELECT * FROM bulletinraw
                        WHERE publisher = %s
                        ORDER BY addtime DESC
                        LIMIT %s;
                        """)
        cursor.execute(query, (category, numbers))

    records = cursor.fetchall()
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

    return records


app = FastAPI()

class Post(BaseModel):
    id: int
    publisher: str
    title: str
    url: str
    content: str
    addtime: datetime

#測試過中文的參數進入fastapi會自動處理不須轉換
@app.get("/api/getdata", response_model=List[Post])
async def get_data(category: Optional[str], numbers: int = Query(default=20, le=100)):
    try:
        raw_data = fetch_data(category, numbers)  # ((id, publisher,),....)
        if not raw_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        data = [Post(id=row[0], publisher=row[1], title=row[2], url=row[3], content=row[4], addtime=row[5]) 
                for row in raw_data]
        return data
    except Exception as Error:
        error_message = '{"error": "%s"}' % Error
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(Error)}
        )
if __name__ == '__main__':
    # 获取数据库中的所有数据
    all_data = fetch_data("",10)

