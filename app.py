import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from PIL import Image
import io

# Database setup
def init_db():
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                machine_name TEXT,
                technician TEXT,
                work_done TEXT,
                issues TEXT,
                condition TEXT,
                photo BLOB)''')
    conn.commit()
    conn.close()

def save_log(machine, technician, work_done, issues, condition, photo):
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO logs 
                (timestamp, machine_name, technician, work_done, issues, condition, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (datetime.now().strftime("%Y-%m-%d %H:%M"),
                machine, technician, work_done, issues, condition, photo))
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect('maintenance.db')
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def get_last_service(machine):
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute("SELECT timestamp FROM logs WHERE machine_name=? ORDER BY timestamp DESC LIMIT 1", (machine,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Initialize database
init_db()

# Page config
st.set_page_config(page_title="Machine Maintenance Tracker", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Submit Maintenance Log", "Manager Dashboard"])

# Machines list
MACHINES = ["Winding Machine #1", "Winding Machine #2", "Winding Machine #3"]

if page == "Submit Maintenance Log":
    st.title("🔧 Maintenance Log")
    st.subheader("Submit your maintenance report")

    with st.form("maintenance_form"):
        machine = st.selectbox("Machine Name", MACHINES)
        technician = st.text_input("Your Name", placeholder="Enter your name")
        work_done = st.text_area("What work was done?", placeholder="Describe the maintenance work...")
        issues = st.text_area("Any issues found?", placeholder="Describe any problems found...")
        condition = st.selectbox("Machine Condition After Service", 
                                ["Good", "Needs Attention", "Critical - Call Manager Now"])
        photo = st.file_uploader("Take a photo of the machine", type=["jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button("Submit Report", use_container_width=True)
        
        if submitted:
            if not technician:
                st.error("Please enter your name!")
            elif not work_done:
                st.error("Please describe the work done!")
            else:
                photo_data = photo.read() if photo else None
                save_log(machine, technician, work_done, issues, condition, photo_data)
                st.success("✅ Maintenance log submitted successfully!")
                st.balloons()

elif page == "Manager Dashboard":
    st.title("📊 Manager Dashboard")
    
    # Machine status overview
    st.subheader("Machine Status Overview")
    
    cols = st.columns(len(MACHINES))
    for i, machine in enumerate(MACHINES):
        last_service = get_last_service(machine)
        with cols[i]:
            if last_service is None:
                st.error(f"🔴 {machine}\nNever serviced!")
            else:
                last_date = datetime.strptime(last_service, "%Y-%m-%d %H:%M")
                days_ago = (datetime.now() - last_date).days
                if days_ago <= 7:
                    st.success(f"🟢 {machine}\nServiced {days_ago} days ago")
                elif days_ago <= 14:
                    st.warning(f"🟡 {machine}\nServiced {days_ago} days ago")
                else:
                    st.error(f"🔴 {machine}\nServiced {days_ago} days ago")
    
    # Recent logs
    st.subheader("Recent Maintenance Logs")
    df = get_logs()
    if df.empty:
        st.info("No maintenance logs yet.")
    else:
        st.dataframe(df[['timestamp', 'machine_name', 'technician', 
                         'work_done', 'issues', 'condition']], 
                    use_container_width=True)

