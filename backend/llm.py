import google.generativeai as genai
import os, json, re
from database import execute_query, get_schema
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("AIzaSyCRuD1bP409NJKSz8rI63inUj4JOpJ66p0") 
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set!")
genai.configure(api_key=api_key)

# Auto-pick first available flash model
def get_model():
    try:
        available = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
        flash = [m for m in available if "flash" in m.lower()]
        pro   = [m for m in available if "pro" in m.lower()]
        name  = flash[0] if flash else (pro[0] if pro else available[0])
        print(f"✅ Using Gemini model: {name}")
        return genai.GenerativeModel(name)
    except Exception as e:
        print(f"⚠️ Model list failed, using fallback: {e}")
        return genai.GenerativeModel("gemini-pro")

model = get_model()

DOMAIN_KEYWORDS = [
    "order","delivery","invoice","billing","payment","customer","product",
    "material","sales","shipment","journal","entry","plant","amount","status",
    "complete","pending","flow","trace","document","fulfilled","billed","paid",
    "revenue","receivable","quantity","price","date","report","list","show",
    "find","get","how many","which","what","who","count","top","highest","lowest",
    "broken","incomplete","missing","overdue","total","average","sum","tell me about"
]

def is_domain_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in DOMAIN_KEYWORDS)

SYSTEM_PROMPT = """You are a data analyst assistant for an SAP Order-to-Cash system.
You ONLY answer questions about the following business data:
- customers, products, addresses
- sales_orders, sales_order_items
- deliveries, billing_documents, payments, journal_entries

DATABASE SCHEMA:
{schema}

When the user asks a question:
1. Generate a valid SQLite SQL query
2. Return ONLY a JSON object in this exact format (no markdown, no backticks):
{{"sql": "SELECT ...", "explanation": "brief explanation"}}

Rules:
- Use only the tables listed above
- SQLite syntax only
- Always include meaningful column aliases
- For "broken flows": orders with delivery but no billing, or billing but no payment
- Return ONLY the raw JSON object, nothing else
"""

def query_llm(user_question: str):
    if not is_domain_query(user_question):
        return {
            "answer": "⚠️ This system is designed to answer questions related to the Order-to-Cash dataset only. Please ask about orders, deliveries, billing, payments, customers, or products.",
            "sql": None,
            "data": None
        }

    schema = get_schema()
    schema_text = "\n".join([
        f"Table: {tbl}\n  Columns: {', '.join(c['name'] for c in cols)}"
        for tbl, cols in schema.items()
    ])

    try:
        prompt = SYSTEM_PROMPT.format(schema=schema_text) + f"\n\nUser question: {user_question}"
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()

        parsed = json.loads(raw)
        sql = parsed.get("sql", "")

        try:
            data = execute_query(sql)
        except Exception as e:
            return {"answer": f"SQL execution error: {str(e)}", "sql": sql, "data": None}

        answer_prompt = f"""
You are an Order-to-Cash data analyst. The user asked: "{user_question}"
The SQL query returned this data: {json.dumps(data[:20], default=str)}
Write a clear, concise business answer in 2-4 sentences.
Use specific numbers from the data. Do not mention SQL.
"""
        answer_resp = model.generate_content(answer_prompt)
        return {
            "answer": answer_resp.text.strip(),
            "sql": sql,
            "data": data[:50]
        }

    except json.JSONDecodeError:
        return {"answer": "I couldn't parse the query properly. Please rephrase your question.", "sql": None, "data": None}
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "sql": None, "data": None}