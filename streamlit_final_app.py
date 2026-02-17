# # 
# import streamlit as st
# import joblib
# import numpy as np
# import mysql.connector
# import plotly.graph_objects as go
# import pandas as pd
# import hashlib
# 
# # ---------------------------------------
# # DATABASE CONNECTION (AUTO CREATE)
# # ---------------------------------------
# def get_connection():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="pass"  # <-- Change this to your MySQL password
#     )
#     cursor = conn.cursor()
#     cursor.execute("CREATE DATABASE IF NOT EXISTS emotion_app")
#     conn.database = "emotion_app"
# 
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             username VARCHAR(100) UNIQUE,
#             password VARCHAR(255)
#         )
#     """)
# 
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS predictions (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             username VARCHAR(100),
#             text_input TEXT,
#             emotion VARCHAR(50),
#             confidence FLOAT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
#     conn.commit()
#     return conn
# 
# # ---------------------------------------
# # HELPERS
# # ---------------------------------------
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()
# 
# # ---------------------------------------
# # LOAD MODEL & CONFIG
# # ---------------------------------------
# @st.cache_resource
# def load_bundle():
#     # Ensure 'emotion_model.joblib' is in your project folder
#     return joblib.load("emotion_model.joblib")
# 
# bundle = load_bundle()
# model = bundle["model"]
# vectorizer = bundle["vectorizer"]
# number_to_emotion = bundle["number_to_emotion"]
# 
# emoji_map = {
#     "joy": "😂", "sadness": "😢", "anger": "😡", "fear": "😨",
#     "love": "❤️", "surprise": "😲", "neutral": "😐", "disgust": "🤢", "shame": "😳"
# }
# 
# st.set_page_config(page_title="Emotion AI App", layout="wide")
# 
# # ---------------------------------------
# # SESSION STATE INIT
# # ---------------------------------------
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# 
# # =======================================
# # LOGIN / REGISTER PAGE
# # =======================================
# if not st.session_state.logged_in:
#     st.title("🔐 Emotion AI Login System")
# 
#     menu = st.radio("Select Option", ["Login", "Register"])
# 
#     # Use st.form with clear_on_submit=True to fix the input field persistence problem
#     with st.form(key="auth_form", clear_on_submit=True):
#         st.subheader(f"Please {menu}")
#         username_input = st.text_input("Username")
#         password_input = st.text_input("Password", type="password")
#         submit_button = st.form_submit_button(label=menu)
# 
#     if submit_button:
#         if username_input and password_input:
#             conn = get_connection()
#             cursor = conn.cursor()
# 
#             if menu == "Register":
#                 try:
#                     hashed = hash_password(password_input)
#                     cursor.execute(
#                         "INSERT INTO users (username, password) VALUES (%s,%s)",
#                         (username_input, hashed)
#                     )
#                     conn.commit()
#                     st.success("Account Created! You can now switch to Login.")
#                 except mysql.connector.Error:
#                     st.error("Username already exists")
# 
#             elif menu == "Login":
#                 hashed = hash_password(password_input)
#                 cursor.execute(
#                     "SELECT * FROM users WHERE username=%s AND password=%s",
#                     (username_input, hashed)
#                 )
#                 user = cursor.fetchone()
# 
#                 if user:
#                     st.session_state.logged_in = True
#                     st.session_state.username = username_input
#                     st.rerun() 
#                 else:
#                     st.error("Invalid Credentials")
# 
#             conn.close()
#         else:
#             st.warning("Please enter both username and password.")
# 
# # =======================================
# # MAIN APP AFTER LOGIN
# # =======================================
# else:
#     st.sidebar.title(f"👤 {st.session_state.username}")
#     page = st.sidebar.radio("Navigation", ["Predict Emotion", "View Report", "Logout"])
# 
#     if page == "Logout":
#         st.session_state.logged_in = False
#         st.rerun()
# 
#     elif page == "Predict Emotion":
#         st.title("🎭 Text Emotion Detection")
#         text = st.text_area("Enter your text", placeholder="How are you feeling?")
# 
#         if st.button("Predict"):
#             if text.strip() != "":
#                 # 1. Prediction
#                 X = vectorizer.transform([text])
#                 prediction = model.predict(X)[0]
#                 probabilities = model.predict_proba(X)[0]
# 
#                 emotion = number_to_emotion[prediction]
#                 confidence = float(np.max(probabilities))
#                 emoji = emoji_map.get(emotion.lower(), "🙂")
# 
#                 # 2. Database Save
#                 conn = get_connection()
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "INSERT INTO predictions (username, text_input, emotion, confidence) VALUES (%s,%s,%s,%s)",
#                     (st.session_state.username, text, emotion, confidence)
#                 )
#                 conn.commit()
#                 conn.close()
# 
#                 # 3. Layout Display
#                 col1, col2 = st.columns([1, 1])
# 
#                 with col1:
#                     st.markdown("### 🎯 Result")
#                     st.success(f"Predicted: **{emotion.upper()}** {emoji}")
# 
#                     # Confidence displayed as percentage
#                     st.markdown("### 📊 Confidence Score")
#                     st.info(f"**{confidence * 100:.2f}%**")
# 
#                 with col2:
#                     st.markdown("### 📈 All Probabilities")
# 
#                     emotions_list = list(number_to_emotion.values())
#                     # Colorful palette matching your reference
#                     colors = ['#8dd3c7', '#bebada', '#80b1d3', '#fdb462', '#fccde5', '#ffed6f']
# 
#                     fig = go.Figure(go.Bar(
#                         x=emotions_list, 
#                         y=probabilities, 
#                         marker_color=colors[:len(emotions_list)],
#                         text=[f"{p*100:.1f}%" for p in probabilities], # Label on bars
#                         textposition='outside',
#                         cliponaxis=False
#                     ))
# 
#                     fig.update_layout(
#                         title="Emotion Probability Distribution",
#                         xaxis_title="Emotions",
#                         yaxis_title="Probability",
#                         yaxis=dict(range=[0, 1.1]), # Headroom for labels
#                         xaxis={'tickangle': 45},
#                         margin=dict(l=20, r=20, t=40, b=20),
#                         height=450
#                     )
#                     st.plotly_chart(fig, use_container_width=True)
# 
#     elif page == "View Report":
#         st.title("📊 Your Prediction History")
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT text_input, emotion, confidence, created_at FROM predictions WHERE username=%s ORDER BY created_at DESC",
#             (st.session_state.username,)
#         )
#         data = cursor.fetchall()
#         conn.close()
# 
#         if not data:
#             st.info("No history found.")
#         else:
#             # Convert confidence back to readable percentage in the table
#             df = pd.DataFrame(data, columns=["Text", "Emotion", "Confidence", "Date"])
#             df["Confidence"] = df["Confidence"].apply(lambda x: f"{x*100:.2f}%")
# 
#             st.dataframe(df, use_container_width=True)
# 
#             csv = df.to_csv(index=False).encode("utf-8")
#             st.download_button("Download CSV Report", csv, "emotion_history.csv", "text/csv")
  
    # My sql code 

# import streamlit as st
# import joblib
# import numpy as np
# import mysql.connector
# import plotly.graph_objects as go
# import pandas as pd
# import hashlib

# # ---------------------------------------
# # DATABASE CONNECTION
# # ---------------------------------------
# def get_connection():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="pass"  # <-- Change this to your MySQL password
#     )
#     cursor = conn.cursor()
#     cursor.execute("CREATE DATABASE IF NOT EXISTS emotion_app")
#     conn.database = "emotion_app"

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             username VARCHAR(100) UNIQUE,
#             password VARCHAR(255)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS predictions (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             username VARCHAR(100),
#             text_input TEXT,
#             emotion VARCHAR(50),
#             confidence FLOAT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
#     conn.commit()
#     return conn

# # ---------------------------------------
# # HELPERS
# # ---------------------------------------
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# @st.cache_resource
# def load_bundle():
#     return joblib.load("emotion_model.joblib")

# # ---------------------------------------
# # APP CONFIG
# # ---------------------------------------
# st.set_page_config(page_title="Emotion AI App", layout="wide")

# bundle = load_bundle()
# model = bundle["model"]
# vectorizer = bundle["vectorizer"]
# number_to_emotion = bundle["number_to_emotion"]

# emoji_map = {
#     "joy": "😂", "sadness": "😢", "anger": "😡", "fear": "😨",
#     "love": "❤️", "surprise": "😲", "neutral": "😐", "disgust": "🤢", "shame": "😳"
# }

# # ---------------------------------------
# # SESSION STATE
# # ---------------------------------------
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# # =======================================
# # LOGIN / REGISTER (NO CSS)
# # =======================================
# if not st.session_state.logged_in:
#     st.title("🔐 Emotion AI Portal")
    
#     # Using columns to center the login form
#     _, col_mid, _ = st.columns([1, 2, 1])
    
#     with col_mid:
#         menu = st.segmented_control("Select Action", ["Login", "Register"], default="Login")
        
#         with st.form(key="auth_form", clear_on_submit=True):
#             st.subheader(menu)
#             u = st.text_input("Username")
#             p = st.text_input("Password", type="password")
#             submit = st.form_submit_button(menu, use_container_width=True)

#         if submit:
#             if u and p:
#                 conn = get_connection()
#                 cursor = conn.cursor()
#                 if menu == "Register":
#                     try:
#                         cursor.execute("INSERT INTO users (username, password) VALUES (%s,%s)", 
#                                        (u, hash_password(p)))
#                         conn.commit()
#                         st.success("Account created! You can now Login.")
#                     except: st.error("Username already exists.")
#                 else:
#                     cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", 
#                                    (u, hash_password(p)))
#                     if cursor.fetchone():
#                         st.session_state.logged_in = True
#                         st.session_state.username = u
#                         st.rerun()
#                     else: st.error("Invalid Credentials.")
#                 conn.close()
#             else:
#                 st.warning("Please fill both fields.")

# # =======================================
# # MAIN APP (NO CSS)
# # =======================================
# else:
#     st.sidebar.title(f"👤 {st.session_state.username}")
#     page = st.sidebar.radio("Navigation", ["Predict Emotion", "View History", "Logout"])

#     if page == "Logout":
#         st.session_state.logged_in = False
#         st.rerun()

#     elif page == "Predict Emotion":
#         st.title("🎭 Text Emotion Detection")
        
#         # Input Section
#         user_text = st.text_area("Enter your text below:", placeholder="How are you feeling?", height=150)
#         predict_btn = st.button("Analyze Emotion 🚀", use_container_width=True)

#         if predict_btn:
#             if user_text.strip():
#                 # Prediction logic
#                 X = vectorizer.transform([user_text])
#                 prediction = model.predict(X)[0]
#                 probs = model.predict_proba(X)[0]
                
#                 emotion_label = number_to_emotion[prediction]
#                 conf = float(np.max(probs))
#                 emoji = emoji_map.get(emotion_label.lower(), "✨")

#                 # Save to Database
#                 conn = get_connection()
#                 cursor = conn.cursor()
#                 cursor.execute("INSERT INTO predictions (username, text_input, emotion, confidence) VALUES (%s,%s,%s,%s)",
#                                (st.session_state.username, user_text, emotion_label, conf))
#                 conn.commit()
#                 conn.close()

#                 st.divider()

#                 # Results Layout
#                 col_left, col_right = st.columns([1, 1.2])

#                 with col_left:
#                     # 1. Show Entered Text
#                     st.subheader("📝 Your Input")
#                     st.info(f'"{user_text}"')

#                     # 2. Show Predicted Emotion
#                     st.subheader("🎯 Predicted Emotion")
#                     # Using a success box for a green, clean look
#                     st.success(f"### {emotion_label.upper()} {emoji}")

#                     # 3. Show Confidence Metric
#                     st.subheader("📊 Confidence Score")
#                     st.metric(label="Certainty", value=f"{conf*100:.2f}%")

#                 with col_right:
#                     st.subheader("📈 Probability Distribution")
#                     emotions = list(number_to_emotion.values())
                    
#                     # Native colorful palette for Plotly
#                     colors = ['#7f7f7f', '#bcbd22', '#17becf', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
                    
#                     fig = go.Figure(go.Bar(
#                         x=emotions, 
#                         y=probs,
#                         marker_color=colors[:len(emotions)],
#                         text=[f"{p*100:.1f}%" for p in probs],
#                         textposition='outside'
#                     ))
                    
#                     fig.update_layout(
#                         xaxis_title="Emotions",
#                         yaxis_title="Probability",
#                         yaxis=dict(range=[0, 1.1]),
#                         xaxis={'tickangle': 45},
#                         height=450,
#                         margin=dict(t=20)
#                     )
#                     st.plotly_chart(fig, use_container_width=True)
#             else:
#                 st.warning("Please enter some text to analyze.")

#     elif page == "View History":
#         st.title("📊 Your Prediction History")
#         conn = get_connection()
#         # Fetching data and converting to dataframe
#         query = "SELECT text_input, emotion, confidence, created_at FROM predictions WHERE username=%s ORDER BY created_at DESC"
#         df = pd.read_sql(query, conn, params=(st.session_state.username,))
#         conn.close()

#         if not df.empty:
#             # Formatting the table for better UI
#             df.columns = ["Entered Text", "Predicted Emotion", "Confidence", "Date & Time"]
#             df["Confidence"] = df["Confidence"].apply(lambda x: f"{x*100:.2f}%")
            
#             st.dataframe(df, use_container_width=True, hide_index=True)
            
#             # Download button
#             csv = df.to_csv(index=False).encode('utf-8')
#             st.download_button("📥 Download Report (CSV)", csv, "emotion_history.csv", "text/csv")
#         else:
#             st.info("You haven't made any predictions yet!")



# My sql code  to sqlite for deployemnt purpose

import streamlit as st
import joblib
import numpy as np
import sqlite3
import plotly.graph_objects as go
import pandas as pd
import hashlib

# ==========================================
# DATABASE CONNECTION (SQLite - Cloud Safe)
# ==========================================
def get_connection():
    conn = sqlite3.connect("emotion_app.db", check_same_thread=False)
    cursor = conn.cursor()

    # Create Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Create Predictions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            text_input TEXT,
            emotion TEXT,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    return conn


# ==========================================
# PASSWORD HASHING
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ==========================================
# LOAD MODEL (Cached)
# ==========================================
@st.cache_resource
def load_bundle():
    return joblib.load("emotion_model.joblib")


# ==========================================
# APP CONFIG
# ==========================================
st.set_page_config(page_title="Emotion AI App", layout="wide")

bundle = load_bundle()
model = bundle["model"]
vectorizer = bundle["vectorizer"]
number_to_emotion = bundle["number_to_emotion"]

emoji_map = {
    "joy": "😂",
    "sadness": "😢",
    "anger": "😡",
    "fear": "😨",
    "love": "❤️",
    "surprise": "😲",
    "neutral": "😐",
    "disgust": "🤢",
    "shame": "😳"
}

# ==========================================
# SESSION STATE
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ==========================================
# LOGIN / REGISTER PAGE
# ==========================================
if not st.session_state.logged_in:

    st.title("🔐 Emotion AI Portal")

    _, col_mid, _ = st.columns([1, 2, 1])

    with col_mid:

        menu = st.segmented_control(
            "Select Action",
            ["Login", "Register"],
            default="Login"
        )

        with st.form("auth_form", clear_on_submit=True):
            st.subheader(menu)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button(menu, use_container_width=True)

        if submit:
            if username and password:
                conn = get_connection()
                cursor = conn.cursor()

                if menu == "Register":
                    try:
                        cursor.execute(
                            "INSERT INTO users (username, password) VALUES (?,?)",
                            (username, hash_password(password))
                        )
                        conn.commit()
                        st.success("Account created! Please login.")
                    except:
                        st.error("Username already exists.")

                elif menu == "Login":
                    cursor.execute(
                        "SELECT * FROM users WHERE username=? AND password=?",
                        (username, hash_password(password))
                    )

                    user = cursor.fetchone()

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

                conn.close()
            else:
                st.warning("Please fill both fields.")


# ==========================================
# MAIN APP (AFTER LOGIN)
# ==========================================
else:

    st.sidebar.title(f"👤 {st.session_state.username}")
    page = st.sidebar.radio(
        "Navigation",
        ["Predict Emotion", "View History", "Logout"]
    )

    # -------------------------
    # LOGOUT
    # -------------------------
    if page == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    # -------------------------
    # PREDICT EMOTION
    # -------------------------
    elif page == "Predict Emotion":

        st.title("🎭 Text Emotion Detection")

        user_text = st.text_area(
            "Enter your text below:",
            placeholder="How are you feeling?",
            height=150
        )

        if st.button("Analyze Emotion 🚀", use_container_width=True):

            if user_text.strip():

                # Model Prediction
                X = vectorizer.transform([user_text])
                prediction = model.predict(X)[0]
                probabilities = model.predict_proba(X)[0]

                emotion = number_to_emotion[prediction]
                confidence = float(np.max(probabilities))
                emoji = emoji_map.get(emotion.lower(), "✨")

                # Save to DB
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO predictions (username, text_input, emotion, confidence) VALUES (?,?,?,?)",
                    (st.session_state.username, user_text, emotion, confidence)
                )
                conn.commit()
                conn.close()

                st.divider()

                col1, col2 = st.columns([1, 1.2])

                with col1:
                    st.subheader("📝 Your Input")
                    st.info(user_text)

                    st.subheader("🎯 Predicted Emotion")
                    st.success(f"{emotion.upper()} {emoji}")

                    st.subheader("📊 Confidence")
                    st.metric("Certainty", f"{confidence*100:.2f}%")

                with col2:
                    st.subheader("📈 Probability Distribution")

                    emotions = list(number_to_emotion.values())

                    fig = go.Figure(go.Bar(
                        x=emotions,
                        y=probabilities,
                        text=[f"{p*100:.1f}%" for p in probabilities],
                        textposition='outside'
                    ))

                    fig.update_layout(
                        xaxis_title="Emotions",
                        yaxis_title="Probability",
                        yaxis=dict(range=[0, 1.1]),
                        height=450
                    )

                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("Please enter some text.")

    # -------------------------
    # VIEW HISTORY
    # -------------------------
    elif page == "View History":

        st.title("📊 Your Prediction History")

        conn = get_connection()

        query = """
            SELECT text_input, emotion, confidence, created_at
            FROM predictions
            WHERE username=?
            ORDER BY created_at DESC
        """

        df = pd.read_sql(query, conn, params=(st.session_state.username,))
        conn.close()

        if not df.empty:

            df.columns = [
                "Entered Text",
                "Predicted Emotion",
                "Confidence",
                "Date & Time"
            ]

            df["Confidence"] = df["Confidence"].apply(
                lambda x: f"{x*100:.2f}%"
            )

            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV",
                csv,
                "emotion_history.csv",
                "text/csv"
            )

        else:
            st.info("No predictions yet.")
