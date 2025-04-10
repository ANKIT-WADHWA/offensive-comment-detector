import streamlit as st
import pandas as pd
from transformers import pipeline
import matplotlib.pyplot as plt
from io import BytesIO

# Page config
st.set_page_config(page_title="Offensive Comment Detector", layout="centered")

# Load model with fallback
try:
    classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)
    model_type = "toxic-bert"
except Exception as e:
    st.warning("⚠️ Failed to load 'unitary/toxic-bert'. Switching to fallback model.")
    classifier = pipeline("text-classification", model="martin-ha/toxic-comment-model", return_all_scores=True)
    model_type = "fallback"

# Label mappings and thresholds
label_mapping = {
    'toxic': 'toxicity',
    'severe_toxic': 'toxicity',
    'insult': 'harassment',
    'obscene': 'profanity',
    'identity_hate': 'hate speech',
    'threat': 'harassment',
    'non-toxic': None
}

custom_thresholds = {
    'identity_hate': 0.15,
    'threat': 0.5,
    'insult': 0.5,
    'toxic': 0.5,
    'severe_toxic': 0.5,
    'obscene': 0.5,
    'non-toxic': 1.0  # ignored
}

# Detection logic
def detect_offense_pipeline(comment):
    results = classifier(comment)

    if model_type == "toxic-bert":
        toxic_scores = {res['label'].lower(): res['score'] for res in results[0]}
    else:  # fallback model
        toxic_scores = {res['label'].lower(): res['score'] for res in results[0]}

    toxic_labels = [
        label for label, score in toxic_scores.items()
        if score > custom_thresholds.get(label, 0.5)
    ]
    offense_types = list({label_mapping[label] for label in toxic_labels if label in label_mapping and label_mapping[label]})
    is_offensive = len(offense_types) > 0
    explanation = "; ".join([f"{label} ({toxic_scores[label]:.2f})" for label in toxic_labels if label in label_mapping])
    return is_offensive, ", ".join(offense_types) if is_offensive else None, explanation if is_offensive else "No offense detected"

# Report generation
def generate_report(df):
    total = len(df)
    offensive_count = df['is_offensive'].sum()
    st.subheader(f"🔍 Offensive Comments Detected: {offensive_count}/{total}")

    all_offense_types = df[df['is_offensive']]['offense_type'].dropna().str.split(', ')
    flattened_types = [item for sublist in all_offense_types for item in sublist]
    offense_breakdown = pd.Series(flattened_types).value_counts()

    st.subheader("📊 Offense Type Breakdown")
    st.dataframe(offense_breakdown.rename("Count"))

    st.subheader("🔥 Top 5 Most Offensive Comments")
    df['offense_score'] = df['explanation'].str.count(';')
    top_5 = df[df['is_offensive']].sort_values(by='offense_score', ascending=False).head(5)
    for _, row in top_5.iterrows():
        st.markdown(f"- **{row['comment_text']}** → _{row['offense_type']}_")

    st.subheader("🧁 Offense Type Distribution (Pie Chart)")
    fig, ax = plt.subplots()
    offense_breakdown.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax)
    ax.set_ylabel('')
    ax.set_title("Offense Type Distribution")
    st.pyplot(fig)

# File processing
def process_file(df):
    results = []
    for _, row in df.iterrows():
        is_off, o_type, explanation = detect_offense_pipeline(row['comment_text'])
        results.append([is_off, o_type, explanation])
    df[['is_offensive', 'offense_type', 'explanation']] = results
    return df

# Streamlit UI
st.title("🚨 Offensive Comment Detector (LLM-Powered)")
st.markdown("Upload a CSV file with **comment_text** column to analyze for offensive content.")

uploaded_file = st.file_uploader("📁 Upload CSV", type=["csv"])
use_sample = st.checkbox("Use Sample Data", value=False)

if uploaded_file or use_sample:
    if use_sample:
        try:
            df = pd.read_csv("data/comments.csv")
            st.success("✅ Sample data loaded from `data/comments.csv`!")
        except Exception as e:
            st.error(f"❌ Failed to load sample data: {e}")
            st.stop()
    else:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"❌ Failed to read uploaded file: {e}")
            st.stop()

    st.write("### Preview")
    st.dataframe(df.head())

    if st.button("🚀 Analyze Comments"):
        with st.spinner("Analyzing..."):
            analyzed_df = process_file(df.copy())
            st.success("🎉 Analysis complete!")
            st.write("### 📝 Annotated Comments")
            st.dataframe(analyzed_df)

            generate_report(analyzed_df)

            # Download analyzed file
            csv = analyzed_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Results CSV",
                data=csv,
                file_name="analyzed_comments.csv",
                mime='text/csv'
            )
