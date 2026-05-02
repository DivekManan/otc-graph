import sqlite3
import random
from datetime import datetime, timedelta

def seed():
    conn = sqlite3.connect("otc.db")
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        city TEXT,
        country TEXT,
        credit_limit REAL
    );
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        unit_price REAL,
        uom TEXT
    );
    CREATE TABLE IF NOT EXISTS addresses (
        id TEXT PRIMARY KEY,
        customer_id TEXT,
        street TEXT,
        city TEXT,
        state TEXT,
        country TEXT,
        type TEXT
    );
    CREATE TABLE IF NOT EXISTS sales_orders (
        id TEXT PRIMARY KEY,
        customer_id TEXT,
        order_date TEXT,
        status TEXT,
        total_amount REAL,
        currency TEXT
    );
    CREATE TABLE IF NOT EXISTS sales_order_items (
        id TEXT PRIMARY KEY,
        order_id TEXT,
        product_id TEXT,
        quantity INTEGER,
        unit_price REAL,
        amount REAL
    );
    CREATE TABLE IF NOT EXISTS deliveries (
        id TEXT PRIMARY KEY,
        order_id TEXT,
        customer_id TEXT,
        delivery_date TEXT,
        status TEXT,
        plant TEXT,
        address_id TEXT
    );
    CREATE TABLE IF NOT EXISTS billing_documents (
        id TEXT PRIMARY KEY,
        order_id TEXT,
        delivery_id TEXT,
        customer_id TEXT,
        billing_date TEXT,
        amount REAL,
        status TEXT,
        type TEXT
    );
    CREATE TABLE IF NOT EXISTS payments (
        id TEXT PRIMARY KEY,
        billing_id TEXT,
        customer_id TEXT,
        payment_date TEXT,
        amount REAL,
        method TEXT,
        status TEXT
    );
    CREATE TABLE IF NOT EXISTS journal_entries (
        id TEXT PRIMARY KEY,
        billing_id TEXT,
        entry_date TEXT,
        account TEXT,
        debit REAL,
        credit REAL,
        description TEXT
    );
    """)

    random.seed(42)
    cities = ["Mumbai","Delhi","Bangalore","Hyderabad","Chennai","Pune","Kolkata","Ahmedabad"]
    categories = ["Electronics","Machinery","Raw Materials","Consumables","Software"]
    plants = ["PLANT_MH01","PLANT_DL02","PLANT_BL03","PLANT_HY04"]

    # Customers
    customers = []
    for i in range(1, 21):
        cid = f"CUST{i:04d}"
        customers.append(cid)
        cur.execute("INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?,?)",
            (cid, f"Customer {i}", f"cust{i}@example.com",
             random.choice(cities), "India", random.randint(100000,500000)))

    # Products
    products = []
    product_names = ["Laptop","Server","Router","Switch","Printer","Scanner",
                     "Monitor","Keyboard","Mouse","UPS","Cable","HDD","SSD",
                     "RAM Module","Power Supply","Cooling Fan","GPU","CPU","Motherboard","NIC"]
    for i, pname in enumerate(product_names, 1):
        pid = f"MAT{i:04d}"
        products.append(pid)
        cur.execute("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)",
            (pid, pname, random.choice(categories),
             round(random.uniform(500,50000),2), "EA"))

    # Addresses
    for cid in customers:
        for atype in ["SHIP","BILL"]:
            cur.execute("INSERT OR IGNORE INTO addresses VALUES (?,?,?,?,?,?,?)",
                (f"ADDR_{cid}_{atype}", cid,
                 f"{random.randint(1,999)} Main St",
                 random.choice(cities), "MH", "India", atype))

    base_date = datetime(2023, 1, 1)

    # Sales Orders — some complete, some broken flows
    orders_created = []
    for i in range(1, 51):
        oid = f"SO{i:06d}"
        cid = random.choice(customers)
        odate = base_date + timedelta(days=random.randint(0, 365))
        status = random.choice(["COMPLETE","COMPLETE","COMPLETE","PARTIAL","OPEN"])
        total = 0
        items = random.randint(1,4)
        order_items = []
        for j in range(items):
            pid = random.choice(products)
            qty = random.randint(1,20)
            price = random.uniform(500,50000)
            amt = round(qty * price, 2)
            total += amt
            order_items.append((f"SOI{i:04d}{j:02d}", oid, pid, qty, round(price,2), amt))
        cur.execute("INSERT OR IGNORE INTO sales_orders VALUES (?,?,?,?,?,?)",
            (oid, cid, odate.strftime("%Y-%m-%d"), status, round(total,2), "INR"))
        for item in order_items:
            cur.execute("INSERT OR IGNORE INTO sales_order_items VALUES (?,?,?,?,?,?)", item)
        orders_created.append((oid, cid, odate, status, round(total,2)))

    # Deliveries — ~80% of orders get deliveries
    deliveries_created = []
    for (oid, cid, odate, status, total) in orders_created:
        if random.random() < 0.82:
            did = f"DEL{oid[2:]}"
            ddate = odate + timedelta(days=random.randint(2,14))
            dstatus = random.choice(["DELIVERED","DELIVERED","DELIVERED","IN_TRANSIT","FAILED"])
            plant = random.choice(plants)
            addr_id = f"ADDR_{cid}_SHIP"
            cur.execute("INSERT OR IGNORE INTO deliveries VALUES (?,?,?,?,?,?,?)",
                (did, oid, cid, ddate.strftime("%Y-%m-%d"), dstatus, plant, addr_id))
            deliveries_created.append((did, oid, cid, ddate, dstatus, total))

    # Billing Documents — ~75% of delivered orders get billed
    billing_created = []
    for (did, oid, cid, ddate, dstatus, total) in deliveries_created:
        if dstatus == "DELIVERED" and random.random() < 0.85:
            bid = f"BILL{oid[2:]}"
            bdate = ddate + timedelta(days=random.randint(1,7))
            cur.execute("INSERT OR IGNORE INTO billing_documents VALUES (?,?,?,?,?,?,?,?)",
                (bid, oid, did, cid, bdate.strftime("%Y-%m-%d"),
                 round(total * random.uniform(0.95,1.05), 2),
                 "POSTED", "F2"))
            billing_created.append((bid, oid, did, cid, bdate, total))

    # Payments — ~70% of billed get paid
    for (bid, oid, did, cid, bdate, total) in billing_created:
        if random.random() < 0.75:
            pdate = bdate + timedelta(days=random.randint(5,30))
            cur.execute("INSERT OR IGNORE INTO payments VALUES (?,?,?,?,?,?,?)",
                (f"PAY{bid[4:]}", bid, cid,
                 pdate.strftime("%Y-%m-%d"),
                 round(total, 2),
                 random.choice(["NEFT","RTGS","CHEQUE","ONLINE"]),
                 "CLEARED"))

    # Journal Entries for billed docs
    for (bid, oid, did, cid, bdate, total) in billing_created:
        cur.execute("INSERT OR IGNORE INTO journal_entries VALUES (?,?,?,?,?,?,?)",
            (f"JE{bid[4:]}", bid,
             bdate.strftime("%Y-%m-%d"),
             "AR_RECEIVABLES",
             round(total,2), 0,
             f"Revenue posting for {bid}"))
        cur.execute("INSERT OR IGNORE INTO journal_entries VALUES (?,?,?,?,?,?,?)",
            (f"JE{bid[4:]}_CR", bid,
             bdate.strftime("%Y-%m-%d"),
             "REVENUE",
             0, round(total,2),
             f"Revenue credit for {bid}"))

    conn.commit()
    conn.close()
    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed()