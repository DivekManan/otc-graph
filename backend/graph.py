from database import execute_query
import networkx as nx

def build_graph(limit_nodes=80):
    G = nx.DiGraph()
    nodes = []
    edges = []

    # Customers
    custs = execute_query("SELECT id, name, city FROM customers LIMIT 8")
    for c in custs:
        G.add_node(c["id"], type="customer", label=c["name"], city=c["city"])
        nodes.append({"id": c["id"], "label": c["name"][:16], "group": "customer",
                       "title": f"Customer\n{c['name']}\n{c['city']}"})

    # Products
    prods = execute_query("SELECT id, name, category, unit_price FROM products LIMIT 10")
    for p in prods:
        G.add_node(p["id"], type="product", label=p["name"])
        nodes.append({"id": p["id"], "label": p["name"][:14], "group": "product",
                       "title": f"Product\n{p['name']}\n₹{p['unit_price']}"})

    # Sales Orders (sample)
    orders = execute_query("""
        SELECT so.id, so.customer_id, so.order_date, so.status, so.total_amount
        FROM sales_orders so LIMIT 15
    """)
    for o in orders:
        G.add_node(o["id"], type="sales_order", label=o["id"])
        nodes.append({"id": o["id"], "label": o["id"], "group": "sales_order",
                       "title": f"Sales Order\n{o['id']}\nStatus: {o['status']}\n₹{o['total_amount']}"})
        if o["customer_id"] in G.nodes:
            G.add_edge(o["customer_id"], o["id"], relation="PLACED")
            edges.append({"from": o["customer_id"], "to": o["id"], "label": "PLACED"})

    # Order Items → Products
    items = execute_query("""
        SELECT soi.order_id, soi.product_id, soi.quantity
        FROM sales_order_items soi
        WHERE soi.order_id IN (SELECT id FROM sales_orders LIMIT 15)
        LIMIT 25
    """)
    for it in items:
        if it["order_id"] in G.nodes and it["product_id"] in G.nodes:
            G.add_edge(it["order_id"], it["product_id"], relation="CONTAINS")
            edges.append({"from": it["order_id"], "to": it["product_id"],
                           "label": f"qty:{it['quantity']}"})

    # Deliveries
    delivs = execute_query("""
        SELECT d.id, d.order_id, d.status, d.plant, d.delivery_date
        FROM deliveries d
        WHERE d.order_id IN (SELECT id FROM sales_orders LIMIT 15)
        LIMIT 15
    """)
    for d in delivs:
        G.add_node(d["id"], type="delivery", label=d["id"])
        nodes.append({"id": d["id"], "label": d["id"], "group": "delivery",
                       "title": f"Delivery\n{d['id']}\n{d['status']}\nPlant: {d['plant']}"})
        if d["order_id"] in G.nodes:
            G.add_edge(d["order_id"], d["id"], relation="FULFILLED_BY")
            edges.append({"from": d["order_id"], "to": d["id"], "label": "FULFILLED_BY"})

    # Billing Documents
    bills = execute_query("""
        SELECT b.id, b.order_id, b.delivery_id, b.amount, b.status
        FROM billing_documents b
        WHERE b.order_id IN (SELECT id FROM sales_orders LIMIT 15)
        LIMIT 12
    """)
    for b in bills:
        G.add_node(b["id"], type="billing", label=b["id"])
        nodes.append({"id": b["id"], "label": b["id"], "group": "billing",
                       "title": f"Billing Doc\n{b['id']}\n₹{b['amount']}\n{b['status']}"})
        if b["delivery_id"] and b["delivery_id"] in G.nodes:
            G.add_edge(b["delivery_id"], b["id"], relation="BILLED_AS")
            edges.append({"from": b["delivery_id"], "to": b["id"], "label": "BILLED_AS"})
        elif b["order_id"] in G.nodes:
            G.add_edge(b["order_id"], b["id"], relation="BILLED_AS")
            edges.append({"from": b["order_id"], "to": b["id"], "label": "BILLED_AS"})

    # Payments
    pays = execute_query("""
        SELECT p.id, p.billing_id, p.amount, p.status, p.method
        FROM payments p
        WHERE p.billing_id IN (SELECT id FROM billing_documents LIMIT 12)
        LIMIT 10
    """)
    for p in pays:
        G.add_node(p["id"], type="payment", label=p["id"])
        nodes.append({"id": p["id"], "label": p["id"], "group": "payment",
                       "title": f"Payment\n{p['id']}\n₹{p['amount']}\n{p['method']}"})
        if p["billing_id"] in G.nodes:
            G.add_edge(p["billing_id"], p["id"], relation="SETTLED_BY")
            edges.append({"from": p["billing_id"], "to": p["id"], "label": "SETTLED_BY"})

    return {"nodes": nodes, "edges": edges}


def get_node_neighbors(node_id: str):
    """Return expanded neighbors for a given node"""
    result = {"nodes": [], "edges": []}
    
    # Detect type from prefix
    if node_id.startswith("CUST"):
        orders = execute_query(
            "SELECT id, status, total_amount, order_date FROM sales_orders WHERE customer_id=?",
            (node_id,))
        for o in orders:
            result["nodes"].append({"id": o["id"], "label": o["id"], "group": "sales_order",
                "title": f"SO\n{o['id']}\n{o['status']}\n₹{o['total_amount']}"})
            result["edges"].append({"from": node_id, "to": o["id"], "label": "PLACED"})

    elif node_id.startswith("SO"):
        items = execute_query(
            """SELECT soi.product_id, p.name, soi.quantity, soi.amount
               FROM sales_order_items soi JOIN products p ON soi.product_id=p.id
               WHERE soi.order_id=?""", (node_id,))
        for it in items:
            result["nodes"].append({"id": it["product_id"], "label": it["name"][:14],
                "group": "product", "title": f"Product\n{it['name']}"})
            result["edges"].append({"from": node_id, "to": it["product_id"],
                "label": f"qty:{it['quantity']}"})
        
        delivs = execute_query(
            "SELECT id, status, delivery_date, plant FROM deliveries WHERE order_id=?", (node_id,))
        for d in delivs:
            result["nodes"].append({"id": d["id"], "label": d["id"], "group": "delivery",
                "title": f"Delivery\n{d['id']}\n{d['status']}"})
            result["edges"].append({"from": node_id, "to": d["id"], "label": "FULFILLED_BY"})

        bills = execute_query(
            "SELECT id, amount, status FROM billing_documents WHERE order_id=?", (node_id,))
        for b in bills:
            result["nodes"].append({"id": b["id"], "label": b["id"], "group": "billing",
                "title": f"Bill\n{b['id']}\n₹{b['amount']}"})
            result["edges"].append({"from": node_id, "to": b["id"], "label": "BILLED_AS"})

    elif node_id.startswith("BILL"):
        pays = execute_query(
            "SELECT id, amount, method, status FROM payments WHERE billing_id=?", (node_id,))
        for p in pays:
            result["nodes"].append({"id": p["id"], "label": p["id"], "group": "payment",
                "title": f"Payment\n{p['id']}\n{p['method']}"})
            result["edges"].append({"from": node_id, "to": p["id"], "label": "SETTLED_BY"})
        
        jes = execute_query(
            "SELECT id, account, debit, credit FROM journal_entries WHERE billing_id=?", (node_id,))
        for je in jes:
            result["nodes"].append({"id": je["id"], "label": je["id"][:12], "group": "journal",
                "title": f"Journal Entry\n{je['account']}\nDr:{je['debit']} Cr:{je['credit']}"})
            result["edges"].append({"from": node_id, "to": je["id"], "label": "POSTED_TO"})

    return result