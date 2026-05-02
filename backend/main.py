from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import build_graph, get_node_neighbors
from llm import query_llm
from database import execute_query
import os

app = FastAPI(title="Order-to-Cash Graph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.get("/")
def root():
    return {"status": "Order-to-Cash Graph API running"}

@app.get("/api/graph")
def get_graph():
    return build_graph()

@app.get("/api/graph/expand/{node_id}")
def expand_node(node_id: str):
    return get_node_neighbors(node_id)

@app.post("/api/chat")
def chat(req: ChatRequest):
    result = query_llm(req.message)
    return result

@app.get("/api/stats")
def get_stats():
    return {
        "customers": execute_query("SELECT COUNT(*) as c FROM customers")[0]["c"],
        "sales_orders": execute_query("SELECT COUNT(*) as c FROM sales_orders")[0]["c"],
        "deliveries": execute_query("SELECT COUNT(*) as c FROM deliveries")[0]["c"],
        "billing_documents": execute_query("SELECT COUNT(*) as c FROM billing_documents")[0]["c"],
        "payments": execute_query("SELECT COUNT(*) as c FROM payments")[0]["c"],
        "products": execute_query("SELECT COUNT(*) as c FROM products")[0]["c"],
        "broken_flows": execute_query("""
            SELECT COUNT(*) as c FROM sales_orders so
            WHERE NOT EXISTS (SELECT 1 FROM billing_documents b WHERE b.order_id=so.id)
            AND EXISTS (SELECT 1 FROM deliveries d WHERE d.order_id=so.id)
        """)[0]["c"]
    }

if __name__ == "__main__":
    import uvicorn
    from seed_data import seed
    if not os.path.exists("otc.db"):
        seed()
    uvicorn.run(app, host="127.0.0.1", port=8000)