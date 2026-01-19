import os
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List, Optional, Dict

app = FastAPI()

# เชื่อมต่อกับ Supabase ผ่าน Environment Variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- กลุ่มที่ 1: Endpoint สำหรับ Snapshot (Real-time) ---
@app.post("/update_account")
async def update_account(data: Dict):
    try:
        # ตัด "updated_at": "now()" ออกเพื่อให้ฐานข้อมูลจัดการเองอัตโนมัติ
        response = supabase.table("accounts").upsert(
            {
                "account_number": str(data.get("account_number")),
                "owner_name": data.get("owner_name"),
                "account_nickname": data.get("account_nickname"),
                "broker_name": data.get("broker_name"),
                "symbol": data.get("symbol"),
                "balance": float(data.get("balance", 0)),
                "equity": float(data.get("equity", 0)),
                "current_price": float(data.get("current_price", 0)),
                "buy_count": int(data.get("buy_count", 0)),
                "buy_lots": float(data.get("buy_lots", 0)),
                "sell_count": int(data.get("sell_count", 0)),
                "sell_lots": float(data.get("sell_lots", 0)),
                "orders_json": data.get("orders_json", [])
            },
            on_conflict="account_number"
        ).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        # พิมพ์ Error ออกมาในหน้า Logs ของ Render เพื่อให้เราตรวจสอบได้ง่ายขึ้น
        print(f"❌ Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- กลุ่มที่ 2: Endpoint สำหรับสถิติรายวัน (Daily Stats) ---
@app.post("/update_daily")
async def update_daily(data: Dict):
    try:
        response = supabase.table("daily_stats").upsert(
            {
                "account_number": str(data.get("account_number")),
                "record_date": data.get("record_date"), # รูปแบบ YYYY-MM-DD
                "symbol": data.get("symbol"),
                "daily_profit": float(data.get("daily_profit", 0)),
                "daily_lots": float(data.get("daily_lots", 0)),
                "daily_max_drawdown": float(data.get("daily_max_drawdown", 0))
            },
            on_conflict="account_number,record_date"
        ).execute()
        return {"status": "success", "type": "daily", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- กลุ่มที่ 3: Endpoint สำหรับประวัติการรวบไม้ (Closing Cycles) ---
@app.post("/add_cycle")
async def add_cycle(data: Dict):
    try:
        response = supabase.table("closing_cycles").insert({
            "account_number": str(data.get("account_number")),
            "magic_number": int(data.get("magic_number", 0)),
            "symbol": data.get("symbol"),
            "total_profit": float(data.get("total_profit", 0)),
            "total_lots": float(data.get("total_lots", 0)),
            "order_count": int(data.get("order_count", 0)),
            "start_time": data.get("start_time"),
            "end_time": data.get("end_time"),
            "closed_orders_json": data.get("closed_orders_json", [])
        }).execute()
        return {"status": "success", "type": "cycle", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Forex Multi-Port API is running!"}
