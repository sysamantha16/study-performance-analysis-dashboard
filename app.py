import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, ttest_ind

st.set_page_config(page_title="Study Performance Analysis", layout="wide")

st.title("📊 Study Hours vs. GPA Dashboard")

st.markdown("""
Upload an Excel file with columns like `Name`, `Age`, `Study Hours`, and `GPA`.  
We’ll visualize study behavior and run basic statistics.
""")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        # Normalize column names
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Try to identify the needed columns
        study_col = next((col for col in df.columns if "study" in col and "hour" in col), None)
        score_col = next((col for col in df.columns if "gpa" in col or "score" in col), None)

        if not study_col or not score_col:
            st.error("❌ Required columns missing. Please make sure your file includes something like 'Study Hours' and 'GPA'.")
            st.stop()

        df.rename(columns={study_col: "study_hours", score_col: "gpa"}, inplace=True)

        st.subheader("📋 Raw Data Preview")
        st.dataframe(df)

        st.subheader("📈 Summary Statistics")
        st.write(df[["study_hours", "gpa"]].describe())

        # Charts
        st.subheader("📊 Visualizations")
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            sns.histplot(df["study_hours"], kde=True, ax=ax)
            ax.set_title("Distribution of Study Hours")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            sns.histplot(df["gpa"], kde=True, color="orange", ax=ax)
            ax.set_title("Distribution of GPA")
            st.pyplot(fig)

        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x="study_hours", y="gpa", hue=df.get("age", None), palette="coolwarm", ax=ax)
        ax.set_title("Study Hours vs GPA")
        st.pyplot(fig)


        st.subheader("📌 Correlation Analysis")

        fig, ax = plt.subplots()
        sns.regplot(data=df, x="study_hours", y="gpa", scatter_kws={"color": "blue"}, line_kws={"color": "red"}, ax=ax)
        ax.set_title("Study Hours vs GPA with Regression Line")
        st.pyplot(fig)

        corr, p_value = pearsonr(df["study_hours"], df["gpa"])
        st.write(f"**Pearson Correlation Coefficient**: {corr:.4f}")
        st.write(f"**p-value**: {p_value:.6f}")
        if p_value < 0.05:
            st.success("✅ Statistically significant relationship.")
        else:
            st.warning("⚠️ No statistically significant relationship.")


        st.subheader("📉 Hypothesis Test (Study Hours Groups)")

        df["group"] = pd.cut(df["study_hours"], bins=[0, 5, 10, 100], labels=["<5h", "5-10h", ">10h"])

        fig, ax = plt.subplots()
        sns.boxplot(data=df, x="group", y="gpa", palette="pastel", ax=ax)
        ax.set_title("GPA Distribution by Study Hour Groups")
        st.pyplot(fig)

        # Perform T-test: <5h vs >10h
        try:
            t1, t2 = df[df["group"] == "<5h"]["gpa"], df[df["group"] == ">10h"]["gpa"]
            t_stat, p_val = ttest_ind(t1, t2, equal_var=False)
            st.write(f"**T-test between '<5h' and '>10h' groups**")
            st.write(f"t-statistic: {t_stat:.4f}, p-value: {p_val:.6f}")
            if p_val < 0.05:
                st.success("✅ Significant difference in GPA between the two groups.")
            else:
                st.warning("⚠️ No significant difference found.")
        except KeyError:
            st.warning("⚠️ Not enough data in <5h or >10h groups for t-test.")

        st.subheader("📝 Limitations")
        st.markdown("""
        - Small sample size can affect significance
        - Self-reported data may contain bias
        - Correlation ≠ causation
        """)

    except Exception as e:
        st.error(f"⚠️ Error loading file: {e}")
