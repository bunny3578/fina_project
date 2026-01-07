from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(
    title="名言佳句API",
    description="這是一個名言佳句管理系統的API提供新增、查詢、更新及刪除名言的功能。",
)

# --- FastAPI 應用程式設定 ---
# 定義 FastAPI 應用程式，並設定 API 的標題與描述

# --- Pydantic 模型 ---
# 定義 PostCreate 模型，用於接收新增或更新的名言資料
# 定義 PostResponse 模型，包含自動生成的 ID，用於回傳給用戶端


class PostCreate(BaseModel):
    """用於接收 Client 端傳入的資料"""

    text: str
    author: str
    tags: str


class PostResponse(PostCreate):
    """用於回傳給 Client 端，包含自動生成的 ID"""

    id: int


# --- 資料庫工具函式 ---
# get_db: 建立並回傳 SQLite 資料庫連線，設定 Row 模式方便讀取


def get_db():
    """建立並回傳資料庫連線，設定 Row 讀取模式"""
    conn = sqlite3.connect("quotes.db")
    conn.row_factory = sqlite3.Row
    return conn


# --- API 端點 ---
# [GET] /: 回傳 API 歡迎訊息
# [GET] /quotes: 查詢所有名言，回傳名言列表
# [POST] /quotes: 新增一筆名言，回傳新增的名言資料
# [PUT] /quotes/{quote_id}: 更新指定 ID 的名言，回傳更新後的資料
# [DELETE] /quotes/{quote_id}: 刪除指定 ID 的名言，回傳成功訊息


@app.get("/")
def read_root():
    """回傳 API 歡迎訊息"""
    return {"message": "名言佳句API"}


# [GET] 查詢所有名言
# list[PostResponse]
@app.get("/quotes", response_model=list[PostResponse])
def get_quotes():
    conn = get_db()
    rows = conn.execute("SELECT * FROM quotes").fetchall()
    conn.close()
    # 將 sqlite3.Row 轉換為 dict 以確保 FastAPI 的資料驗證能正確執行
    return [dict(r) for r in rows]


# [POST] 新增一筆名言
@app.post("/quotes", response_model=PostResponse)
def create_quote(q: PostCreate):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)",
        (q.text, q.author, q.tags),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    # 回傳包含新 id 的完整名言物件
    return {**q.model_dump(), "id": new_id}


# [PUT] 更新指定 ID 的名言
@app.put("/quotes/{quote_id}", response_model=PostResponse)
def update_quote(quote_id: int, q: PostCreate):
    conn = get_db()
    cur = conn.execute(
        "UPDATE quotes SET text=?, author=?, tags=? WHERE id=?",
        (q.text, q.author, q.tags, quote_id),
    )

    if cur.rowcount == 0:
        conn.close()
        # 必須回傳指定的 404 訊息
        raise HTTPException(status_code=404, detail="Quote not found")

    conn.commit()
    conn.close()
    # 回傳更新後的完整物件
    return {**q.model_dump(), "id": quote_id}


# [DELETE] 刪除指定 ID 的名言
@app.delete("/quotes/{quote_id}")
def delete_quote(quote_id: int):
    conn = get_db()
    cur = conn.execute("DELETE FROM quotes WHERE id=?", (quote_id,))

    if cur.rowcount == 0:
        conn.close()
        # 必須回傳指定的 404 訊息
        raise HTTPException(status_code=404, detail="Quote not found")

    conn.commit()
    conn.close()
    # 回傳指定的成功訊息格式
    return {"message": "Quote deleted successfully"}
