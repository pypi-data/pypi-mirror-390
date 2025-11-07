import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def smart_viz(df):
    """
    Automatically generate important EDA charts for a dataset.
    """

    print("\n[Essentia] 📊 Starting Smart Visualization...\n")
    sns.set(style="whitegrid")

    # 1️⃣ Correlation Heatmap (for numeric data)
    num_df = df.select_dtypes(include=['int64', 'float64'])
    if not num_df.empty:
        print("[Essentia] 🔹 Correlation Heatmap for Numerical Features:")
        plt.figure(figsize=(8, 5))
        sns.heatmap(num_df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Heatmap")
        plt.show()
    else:
        print("[Essentia] ⚠️ No numerical columns for correlation heatmap.")

    # 2️⃣ Distribution of each numeric column
    for col in num_df.columns:
        plt.figure(figsize=(6, 4))
        sns.histplot(df[col], kde=True, color='skyblue')
        plt.title(f"Distribution of {col}")
        plt.show()

    # 3️⃣ Count plot for categorical columns
    cat_df = df.select_dtypes(include=['object'])
    for col in cat_df.columns:
        plt.figure(figsize=(6, 4))
        sns.countplot(y=col, data=df, palette="viridis")
        plt.title(f"Count of Categories in {col}")
        plt.show()

    # 4️⃣ Boxplot for outlier detection
    if not num_df.empty:
        for col in num_df.columns:
            plt.figure(figsize=(6, 4))
            sns.boxplot(x=df[col], color="lightgreen")
            plt.title(f"Boxplot for {col}")
            plt.show()

    # 5️⃣ Pairplot for overall numeric relationships
    if len(num_df.columns) > 1:
        print("[Essentia] 🔹 Pairplot for Numeric Relationships:")
        sns.pairplot(num_df)
        plt.show()

    print("\n[Essentia] ✅ Smart Visualization Completed!\n")
