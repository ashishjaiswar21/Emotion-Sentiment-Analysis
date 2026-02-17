# 🎭 Emotion AI Login System

A full-stack Machine Learning web application built using **Streamlit** and **SQLite** that performs text-based emotion detection with secure user authentication.

---

## 🚀 Features

- 🔐 User Registration & Login (Secure Password Hashing)
- 🎭 Text Emotion Detection using ML model
- 📊 Confidence Score & Probability Distribution Graph
- 📝 User Prediction History
- 📥 Download History as CSV
- 💾 Local Database using SQLite (Auto-creates on first run)
- ⚡ Fast and lightweight deployment on Streamlit Cloud

---

## 🧠 Machine Learning Model

- Model trained using **Scikit-learn**
- Text Vectorization using **CountVectorizer / TF-IDF**
- Classification algorithm (Logistic Regression / Naive Bayes / etc.)
- Saved using **Joblib**
- Emotion categories include:

  - Joy  
  - Sadness  
  - Anger  
  - Fear  
  - Love  
  - Surprise  
  - Neutral  
  - Disgust  
  - Shame  

---

## 🛠 Tech Stack

- Python
- Streamlit
- SQLite
- Scikit-learn
- Pandas
- Plotly
- Joblib
- Hashlib (Password Security)

---

## 📁 Project Structure

emotion-ai-app/
│
├── streamlit_app.py # Main application file
├── emotion_model.joblib # Trained ML model bundle
├── requirements.txt # Project dependencies
├── emotion_app.db # SQLite database (auto-created)
├── .gitignore
└── README.md


---

## ▶️ How to Run Locally

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/emotion-ai-app.git
cd emotion-ai-app
2️⃣ Create Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run Application
streamlit run streamlit_app.py
5️⃣ Open in Browser
http://localhost:8501