from app import init_db, get_db
init_db()
c=get_db()
c.execute("""INSERT OR IGNORE INTO projects
(project_code,project_name,customer,country,business_unit,project_manager,order_value,planned_cost,actual_cost,revenue_taken,status)
VALUES ('PRJ-1001','Sample E2E Project','Demo Customer','India','Solutions','Project Manager',1000000,700000,280000,350000,'Execution')""")
c.commit(); c.close()
print("Demo data added.")
