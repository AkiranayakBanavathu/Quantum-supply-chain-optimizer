from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3, json, os
from classical.classical_optimizer import greedy_optimize
from quantum.quantum_optimizer import quantum_optimize

app = Flask(__name__)
app.secret_key = "hackathon-demo-secret-change-me"
DB = os.path.join("database", "supply_chain.db")
app.jinja_env.globals.update(enumerate=enumerate, range=range)

def get_db():
    os.makedirs("database", exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_db()
    con.executescript('''
    CREATE TABLE IF NOT EXISTS warehouses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, supply INTEGER NOT NULL, location TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS stores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, demand INTEGER NOT NULL, location TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS costs(
        warehouse_id INTEGER NOT NULL, store_id INTEGER NOT NULL,
        cost REAL NOT NULL, PRIMARY KEY(warehouse_id, store_id));
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        classical_cost REAL, quantum_cost REAL, method TEXT);
    ''')
    if con.execute("SELECT COUNT(*) FROM warehouses").fetchone()[0] == 0:
        with open("data/demo_data.json", encoding="utf-8") as f:
            data = json.load(f)
        for w in data["warehouses"]:
            con.execute("INSERT INTO warehouses(name,supply,location) VALUES(?,?,?)",
                        (w["name"], w["supply"], w["location"]))
        for s in data["stores"]:
            con.execute("INSERT INTO stores(name,demand,location) VALUES(?,?,?)",
                        (s["name"], s["demand"], s["location"]))
        ws = con.execute("SELECT id FROM warehouses ORDER BY id").fetchall()
        ss = con.execute("SELECT id FROM stores ORDER BY id").fetchall()
        for i, w in enumerate(ws):
            for j, s in enumerate(ss):
                con.execute("INSERT INTO costs VALUES(?,?,?)", (w["id"], s["id"], data["costs"][i][j]))
    con.commit(); con.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["logged_in"] = True
            session["username"] = "admin"
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    con = get_db()
    warehouses = con.execute("SELECT * FROM warehouses ORDER BY id").fetchall()
    stores = con.execute("SELECT * FROM stores ORDER BY id").fetchall()
    history = con.execute("SELECT * FROM history ORDER BY id DESC LIMIT 5").fetchall()
    con.close()
    return render_template("dashboard.html", warehouses=warehouses, stores=stores,
                           history=history,
                           total_supply=sum(w["supply"] for w in warehouses),
                           total_demand=sum(s["demand"] for s in stores))

@app.route("/warehouses", methods=["GET", "POST"])
@login_required
def warehouses():
    con = get_db()
    if request.method == "POST":
        con.execute("INSERT INTO warehouses(name,supply,location) VALUES(?,?,?)",
                    (request.form["name"], int(request.form["supply"]), request.form["location"]))
        con.commit()
        flash("Warehouse added successfully.")
    rows = con.execute("SELECT * FROM warehouses ORDER BY id").fetchall()
    con.close()
    return render_template("warehouses.html", warehouses=rows)

@app.route("/warehouses/delete/<int:item_id>")
@login_required
def delete_warehouse(item_id):
    con = get_db()
    con.execute("DELETE FROM costs WHERE warehouse_id=?", (item_id,))
    con.execute("DELETE FROM warehouses WHERE id=?", (item_id,))
    con.commit(); con.close()
    return redirect(url_for("warehouses"))

@app.route("/stores", methods=["GET", "POST"])
@login_required
def stores():
    con = get_db()
    if request.method == "POST":
        con.execute("INSERT INTO stores(name,demand,location) VALUES(?,?,?)",
                    (request.form["name"], int(request.form["demand"]), request.form["location"]))
        con.commit()
        flash("Store added successfully.")
    rows = con.execute("SELECT * FROM stores ORDER BY id").fetchall()
    con.close()
    return render_template("stores.html", stores=rows)

@app.route("/stores/delete/<int:item_id>")
@login_required
def delete_store(item_id):
    con = get_db()
    con.execute("DELETE FROM costs WHERE store_id=?", (item_id,))
    con.execute("DELETE FROM stores WHERE id=?", (item_id,))
    con.commit(); con.close()
    return redirect(url_for("stores"))

@app.route("/optimization", methods=["GET", "POST"])
@login_required
def optimization():
    result = None
    if request.method == "POST":
        con = get_db()
        warehouses = [dict(x) for x in con.execute("SELECT * FROM warehouses ORDER BY id").fetchall()]
        stores = [dict(x) for x in con.execute("SELECT * FROM stores ORDER BY id").fetchall()]
        costs = []
        for w in warehouses:
            row = []
            for s in stores:
                found = con.execute("SELECT cost FROM costs WHERE warehouse_id=? AND store_id=?",
                                    (w["id"], s["id"])).fetchone()
                row.append(found["cost"] if found else 1)
            costs.append(row)
        classical = greedy_optimize(warehouses, stores, costs)
        quantum = quantum_optimize(warehouses, stores, costs)
        con.execute("INSERT INTO history(classical_cost,quantum_cost,method) VALUES(?,?,?)",
                    (classical["cost"], quantum["cost"], quantum["method"]))
        con.commit(); con.close()
        result = {"classical": classical, "quantum": quantum,
                  "warehouses": warehouses, "stores": stores, "costs": costs}
    return render_template("optimization.html", result=result)

@app.route("/history")
@login_required
def history():
    con = get_db()
    rows = con.execute("SELECT * FROM history ORDER BY id DESC").fetchall()
    con.close()
    return render_template("history.html", history=rows)

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
