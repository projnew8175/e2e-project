from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / "e2e_project.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_code TEXT UNIQUE NOT NULL,
        project_name TEXT NOT NULL,
        customer TEXT,
        country TEXT,
        business_unit TEXT,
        project_manager TEXT,
        order_value REAL DEFAULT 0,
        planned_cost REAL DEFAULT 0,
        actual_cost REAL DEFAULT 0,
        revenue_taken REAL DEFAULT 0,
        status TEXT DEFAULT 'Setup'
    );
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        owner TEXT,
        due_date TEXT,
        status TEXT DEFAULT 'Open',
        FOREIGN KEY(project_id) REFERENCES projects(id)
    );
    CREATE TABLE IF NOT EXISTS risks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        owner TEXT,
        severity TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Open',
        FOREIGN KEY(project_id) REFERENCES projects(id)
    );
    """)
    conn.commit()
    conn.close()

@app.template_filter("money")
def money(v):
    return f"{float(v or 0):,.2f}"

@app.route("/")
def dashboard():
    conn = get_db()
    projects = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    stats = {
        "projects": conn.execute("SELECT COUNT(*) c FROM projects").fetchone()["c"],
        "open_actions": conn.execute("SELECT COUNT(*) c FROM actions WHERE status='Open'").fetchone()["c"],
        "open_risks": conn.execute("SELECT COUNT(*) c FROM risks WHERE status='Open'").fetchone()["c"],
        "order_value": conn.execute("SELECT COALESCE(SUM(order_value),0) s FROM projects").fetchone()["s"]
    }
    conn.close()
    return render_template("dashboard.html", projects=projects, stats=stats)

@app.route("/projects/new", methods=["GET","POST"])
def new_project():
    if request.method == "POST":
        data = request.form
        try:
            conn = get_db()
            conn.execute("""INSERT INTO projects
                (project_code, project_name, customer, country, business_unit,
                 project_manager, order_value, planned_cost, status)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (data["project_code"], data["project_name"], data["customer"],
                 data["country"], data["business_unit"], data["project_manager"],
                 float(data["order_value"] or 0), float(data["planned_cost"] or 0),
                 data["status"]))
            conn.commit()
            conn.close()
            flash("Project created successfully.", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Could not create project: {e}", "danger")
    return render_template("project_form.html")

@app.route("/projects/<int:pid>")
def project(pid):
    conn = get_db()
    p = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    actions = conn.execute("SELECT * FROM actions WHERE project_id=? ORDER BY id DESC", (pid,)).fetchall()
    risks = conn.execute("SELECT * FROM risks WHERE project_id=? ORDER BY id DESC", (pid,)).fetchall()
    conn.close()
    if not p:
        return "Project not found", 404
    gm = (p["order_value"] or 0) - (p["planned_cost"] or 0)
    completion = ((p["actual_cost"] or 0) / p["planned_cost"] * 100) if p["planned_cost"] else 0
    gm_taken = (p["revenue_taken"] or 0) - (p["actual_cost"] or 0)
    return render_template("project.html", p=p, actions=actions, risks=risks,
                           gm=gm, completion=completion, gm_taken=gm_taken)

@app.post("/projects/<int:pid>/update")
def update_project(pid):
    d = request.form
    conn = get_db()
    conn.execute("""UPDATE projects SET actual_cost=?, revenue_taken=?, status=? WHERE id=?""",
                 (float(d["actual_cost"] or 0), float(d["revenue_taken"] or 0),
                  d["status"], pid))
    conn.commit(); conn.close()
    flash("Project updated.", "success")
    return redirect(url_for("project", pid=pid))

@app.post("/projects/<int:pid>/action")
def add_action(pid):
    d = request.form
    conn = get_db()
    conn.execute("INSERT INTO actions(project_id,action,owner,due_date,status) VALUES(?,?,?,?,?)",
                 (pid,d["action"],d["owner"],d["due_date"],"Open"))
    conn.commit(); conn.close()
    return redirect(url_for("project", pid=pid))

@app.post("/projects/<int:pid>/risk")
def add_risk(pid):
    d = request.form
    conn = get_db()
    conn.execute("INSERT INTO risks(project_id,description,owner,severity,status) VALUES(?,?,?,?,?)",
                 (pid,d["description"],d["owner"],d["severity"],"Open"))
    conn.commit(); conn.close()
    return redirect(url_for("project", pid=pid))

@app.route("/sap", methods=["GET","POST"])
def sap():
    if request.method == "POST":
        flash("SAP VA01 simulation order saved. No real SAP transaction was performed.", "success")
    return render_template("sap.html")

@app.route("/checklist")
def checklist():
    return render_template("checklist.html")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
