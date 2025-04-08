import streamlit as st
import pandas as pd
from transformers import pipeline
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Offensive Comment Detector", layout="centered")

classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)

label_mapping = {
    'toxic': 'toxicity',
    'severe_toxic': 'toxicity',
    'insult': 'harassment',
    'obscene': 'profanity',
    'identity_hate': 'hate speech',
    'threat': 'harassment'
}

custom_thresholds = {
    'identity_hate': 0.15,
    'threat': 0.5,
    'insult': 0.5,
    'toxic': 0.5,
    'severe_toxic': 0.5,
    'obscene': 0.5
}

def detect_offense_pipeline(comment):
    results = classifier(comment)
    toxic_scores = {res['label'].lower(): res['score'] for res in results[0]}
    toxic_labels = [
        label for label, score in toxic_scores.items()
        if score > custom_thresholds.get(label, 0.5)
    ]
    offense_types = list({label_mapping[label] for label in toxic_labels if label in label_mapping})
    is_offensive = len(offense_types) > 0
    explanation = "; ".join([f"{label} ({toxic_scores[label]:.2f})" for label in toxic_labels if label in label_mapping])
    return is_offensive, ", ".join(offense_types) if is_offensive else None, explanation if is_offensive else "No offense detected"

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
        df = pd.DataFrame({
            'comment_id': [1, 2, 3],
            'username': ['alice', 'bob', 'charlie'],
            'comment_text': [
                "You are such an idiot!",
                "Have a great day!",
                "I hate your entire community."
            ]
        })
        st.success("Sample data loaded!")
    else:
        df = pd.read_csv(uploaded_file)

    st.write("### Preview")
    st.dataframe(df.head())

    if st.button("🚀 Analyze Comments"):
        with st.spinner("Analyzing..."):
            analyzed_df = process_file(df.copy())
            st.success("Analysis complete!")
            st.write("### Annotated Comments")
            st.dataframe(analyzed_df)

            generate_report(analyzed_df)

            # Download button
            csv = analyzed_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Results CSV",
                data=csv,
                file_name="analyzed_comments.csv",
                mime='text/csv'
            )
