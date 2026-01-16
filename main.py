from fastapi import FastAPI
from supabase import create_client, Client
import json

app = FastAPI()

# ใส่ค่าจาก Settings > API ใน Supabase ของคุณ
SUPABASE_URL = "https://jiwtorjzszrybfxztasm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imppd3Rvcmp6c3pyeWJmeHp0YXNtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg1MzQ1OTUsImV4cCI6MjA4NDExMDU5NX0.pTL5ZARYH5thEMDHHbaxBQdgoo5GEHGe08bXYQ2VKeY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.post("/update_account")
async def update_account(data: dict):
    try:
        # พิมพ์ดูข้อมูลที่ส่งมา (ทางหน้าจอ Log ของ Render)
        print(f"Syncing Account: {data.get('account_number')}")
        
        # แก้ไขบรรทัดนี้: เพิ่ม on_conflict เพื่อบอกว่าถ้าเลขพอร์ตซ้ำ ให้ทับข้อมูลเดิม
        response = supabase.table("accounts").upsert(
            {
                "account_number": str(data.get("account_number")),
                "balance": float(data.get("balance", 0)),
                "equity": float(data.get("equity", 0)),
                "current_price": float(data.get("current_price", 0)),
                "updated_at": "now()" # บันทึกเวลาที่อัปเดตล่าสุด
            },
            on_conflict="account_number"  # <--- จุดสำคัญคือบรรทัดนี้ครับ
        ).execute()
        
        return {"status": "success", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
