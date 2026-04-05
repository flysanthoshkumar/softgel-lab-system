import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# DB
conn = sqlite3.connect("lab.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS standards(name TEXT, qty REAL, expiry TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS consumption(name TEXT, qty REAL, date TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")

# Default user
cursor.execute("INSERT OR IGNORE INTO users VALUES('admin','1234')")
conn.commit()

# LOGIN
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("Softgel Healthcare Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        data = cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd)).fetchone()
        if data:
            st.session_state.login = True
        else:
            st.error("Invalid Login")
    st.stop()

# APP
st.title("Softgel Healthcare Lab System")

menu = st.sidebar.selectbox("Menu", ["Dashboard","Add Stock","Consume","Alerts","Reports"])

if menu=="Dashboard":
    df = pd.read_sql("SELECT * FROM standards", conn)
    st.dataframe(df)
    if not df.empty:
        st.bar_chart(df.set_index("name")["qty"])

if menu=="Add Stock":
    name = st.selectbox("Standard", ["Paracetamol","Ibuprofen","Caffeine"])
    qty = st.number_input("Quantity")
    expiry = st.date_input("Expiry")

    if st.button("Add"):
        cursor.execute("INSERT INTO standards VALUES (?,?,?)",(name,qty,str(expiry)))
        conn.commit()
        st.success("Stock Added")

if menu=="Consume":
    name = st.selectbox("Standard", ["Paracetamol","Ibuprofen","Caffeine"])
    qty = st.number_input("Used Qty")

    if st.button("Consume"):
        cursor.execute("UPDATE standards SET qty=qty-? WHERE name=?",(qty,name))
        cursor.execute("INSERT INTO consumption VALUES (?,?,?)",(name,qty,str(datetime.now())))
        conn.commit()
        st.success("Updated")

if menu=="Alerts":
    data = cursor.execute("SELECT name, qty, expiry FROM standards").fetchall()
    for d in data:
        if d[1] < 5:
            st.warning(f"{d[0]} Low Stock")
        exp = datetime.strptime(d[2], "%Y-%m-%d")
        if exp - datetime.now() < timedelta(days=30):
            st.warning(f"{d[0]} Expiring Soon")

if menu=="Reports":
    df = pd.read_sql("SELECT * FROM standards", conn)
    st.download_button("Download Report", df.to_csv(), "Softgel_Report.csv")
