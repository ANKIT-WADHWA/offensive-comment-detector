import pandas as pd

# Load CSV file
def load_comments(file_path):
    try:
        df = pd.read_csv(file_path)
        print("✅ File loaded successfully.\n")
        return df
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

# Display summary
def show_summary(df):
    total_comments = len(df)
    print(f"📝 Total comments: {total_comments}\n")
    print("🔍 Sample preview:")
    print(df.head())

# Main
if __name__ == "__main__":
    file_path = "D:\offensive-comment-detector\data\comments.csv"  # You can change this to your file path
    df = load_comments(file_path)
    if df is not None:
        show_summary(df)
