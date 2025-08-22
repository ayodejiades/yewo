# Model Training and Development Process

This document details the process used to train the two-tier AI system for the Yewo: Job Scam Detector. Our approach combines a specialized Nigerian model with a general-purpose Global model for maximum accuracy.

**Primary Notebook:** `Yewo.ipynb`

## 1. Objective
The goal was to build a highly accurate system to classify job postings as legitimate or fraudulent. We recognized that while many scams are universal, some tactics are specific to the Nigerian context. This led to our two-model approach.

---

## 2. Model 1: The Nigerian-Tuned Model (`yewo.joblib`)

This model is a specialist, designed to be highly sensitive to local scam indicators.

### A. Datasets
- **Primary Dataset:** [Fake/Real Job Posting in Nigeria](https://www.kaggle.com/datasets/oyelajairemide/fakereal-job-posting-in-nigeria) from Kaggle.
- **Data Augmentation:** The initial dataset was small. We significantly improved it by manually creating 16 high-quality examples of common Nigerian scam tactics (e.g., requests for "WhatsApp" contact, "registration fees", "BVN") and legitimate corporate job postings (e.g., from GTBank, Dangote). This was critical for improving the model's local context awareness.

### B. The Pipeline: A Step-by-Step Process
Our training followed a standard machine learning pipeline:

#### **Feature Engineering**
We engineered features specifically to catch signals common in Nigeria:
- **`scam_score`:** A composite score that heavily penalizes the presence of keywords like "fee", "payment", "whatsapp", "bvn", and unprofessional email domains ("@gmail.com", "@yahoo.com").
- **Text Metadata:** Features like the length of the job description (`job_desc_length`), percentage of uppercase characters (`percent_caps`), and count of exclamation marks (`exclamation_count`).
- **Structural Features:** Binary flags indicating the presence of a company profile (`has_company_desc`) or job requirements (`has_job_requirement`).

#### **Model Selection & Training**
- We chose a `RandomForestClassifier` from Scikit-learn. This model is robust and performs well on the structured, tabular data we created.
- The combined dataset (original + augmented) was split into an 80% training set and a 20% testing set.
- **Result:** The final model achieved high accuracy on the unseen test data, with a particularly strong recall for the "fraudulent" class, ensuring we effectively catch common local scams.

---

## 3. Model 2: The Global Expert Model (`yewo2.joblib`)

This model is a generalist, trained to detect broader, more subtle patterns of fraudulent language that might be missed by the Nigerian model.

### A. Dataset
- **Primary Dataset:** [Real / Fake Job Postings Prediction](https://www.kaggle.com/datasets/shivankmp/real-or-fake-fake-jobposting-prediction) from Kaggle.
- **Description:** This is a large and comprehensive dataset containing **~18,000 job postings** from around the world. It includes a wide variety of industries and scam types, making it perfect for training a generalized text-based fraud detector.

### B. The Pipeline: A Text-Based Approach

The global model's pipeline is different, as it focuses purely on the nuances of the language used.

#### **Feature Engineering**
- **TF-IDF Vectorization:** We did not create manual features for this model. Instead, we used a `TfidfVectorizer` from Scikit-learn. This technique analyzes the frequency of all words in the job descriptions and converts the text into a sophisticated numerical representation. It automatically learns which words and phrases are most indicative of fraud on a large scale.

#### **Model Selection & Training**
- We used a `PassiveAggressiveClassifier`, a model that is highly efficient and effective for large-scale text classification tasks. It learns quickly from the vast amount of text data provided by the TF-IDF vectorizer.
- The model was trained on the full text of the job postings (title, description, etc.).
- **Result:** This model excels at identifying jobs that just "feel" fake based on their tone, grammar, and unusual phrasing, providing a crucial second layer of defense.

---

## 4. How to Reproduce
1.  Open the `Yewo.ipynb` notebook in Google Colab or Jupyter.
2.  Ensure you have the original dataset files (`CompiledjobListNigeria.csv` and the global `fake_job_postings.csv`) in the same directory.
3.  Run the cells sequentially from top to bottom. The notebook will perform all data augmentation, feature engineering, and training for **both models**. It will save the final `yewo.joblib` and `yewo2.joblib` model files in the `models/` folder.