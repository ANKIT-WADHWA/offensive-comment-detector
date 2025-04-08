🔗 **[Live Demo](https://offensive-comment-detector-fksppamv69m6vmfmjggwgw.streamlit.app/)** — Try the app instantly in your browser:  
`https://offensive-comment-detector-fksppamv69m6vmfmjggwgw.streamlit.app/`
----
## 📌 Overview

This repository provides a **Streamlit-based web application** that detects **offensive, toxic, or hateful comments** using a **BERT-based LLM classifier**. Upload a CSV file or try sample data to analyze text for various types of harmful language and receive insights with visualizations.

## 🛠 Features

**✅ Real-time Comment Analysis**  
- Supports input via CSV or sample data.  
- Detects **toxicity**, **hate speech**, **profanity**, **harassment**, and more.

**✅ Multi-label Classification**  
- Uses `unitary/toxic-bert` transformer model.  
- Applies **custom thresholds** to determine offense severity.

**✅ Streamlit UI**  
- Clean interface to upload files, visualize results, and download annotated data.

**✅ Explanation & Score**  
- Highlights offensive categories with confidence scores.

**✅ Insightful Analytics**  
- Pie chart of offense types.  
- Top 5 most offensive comments shown.  
- Offense category breakdown.

---


## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/offensive-comment-detector.git
cd offensive-comment-detector
```

---

### 2️⃣ Create Virtual Environment & Install Dependencies

```bash
python -m venv venv

# For Windows
venv\Scripts\activate

# For macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

### 3️⃣ Launch the Streamlit App

```bash
streamlit run main.py
```
