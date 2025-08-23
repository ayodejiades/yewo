# Yewo: The Nigerian Job Scam Detector

**Live Demo:** [Yewo](https://yewoai.streamlit.app)

## The Problem
Job scams are a significant threat to Nigerian job seekers, leading to financial loss and personal danger. Fraudulent actors often lure victims with fake job postings that seem legitimate.

## Our Solution
Yewo (Yoruba for "to check") is an AI-powered tool that acts as a safety net. It uses a sophisticated two-tier AI system to analyze job postings for signs of fraud:
1.  A **Nigerian-tuned model** trained on local data to detect specific regional scam tactics.
2.  A **Global Expert model** trained on a large international dataset to catch general fraudulent patterns.

## How to Run Locally
1.  Clone the repository: `git clone https://github.com/ayodejiades/yewo.git`
2.  Navigate to the project directory: `cd yewo`
3.  Install the required libraries: `pip install -r requirements.txt`
4.  Run the Streamlit app: `streamlit run app.py`

## Tech Stack
- **Language:** Python
- **Framework:** Streamlit
- **Machine Learning:** Scikit-learn, Pandas, Joblib
- **Deployment:** Streamlit Community Cloud

## Model Training Process
For a detailed, step-by-step walkthrough of our data cleaning, feature engineering, and model training process, please see the **[Model Training README](./training/README.md)**.
