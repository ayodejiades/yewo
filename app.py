import streamlit as st
import pandas as pd
import joblib
import os
import re

st.set_page_config(page_title="Yewo - Job Scam Detector", layout="wide", page_icon="🔎")


@st.cache_resource
def load_models():
    """
    Loads both the Nigerian and Global models using platform-independent paths.
    This function is cached to run only once, preventing reloading on every interaction.
    """
    try:
        nigerian_model_path = os.path.join('models', 'yewo.joblib')
        global_model_path = os.path.join('models', 'yewo2.joblib')
        
        nigerian_pipeline = joblib.load(nigerian_model_path)
        global_pipeline = joblib.load(global_model_path)
        
        print("Models loaded successfully.")
        return nigerian_pipeline, global_pipeline
        
    except Exception as e:
        st.error(f"Error loading models: {e}")
        st.error("Please ensure 'yewo.joblib' and 'yewo2.joblib' are in the 'models' folder.")
        return None, None


nigerian_model, global_model = load_models()
if not nigerian_model or not global_model:
    st.stop()


st.title("Yewo: The Nigerian Job Scam Detector")
st.markdown("""
Welcome to **Yewo** (Yoruba: "to check"), an AI-powered safety net for Nigerian job seekers. Our system uses a **two-tier AI approach** for maximum protection:
1.  A **Nigerian-tuned model** that identifies local scam tactics.
2.  A **Global Expert model**, trained on over 17,000 job posts, that detects general patterns of fraud.
""")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Job Details")
    job_title = st.text_input("Job Title", placeholder="e.g., Marketing Manager")
    job_desc = st.text_area("Job Description", placeholder="e.g., We are looking for a skilled professional...", height=150)
    job_requirement = st.text_area("Job Requirements", placeholder="e.g., 5+ years of experience with Python...", height=150)

with col2:
    st.subheader("Company Details")
    company_name = st.text_input("Company Name", placeholder="e.g., Dangote Group")
    company_desc = st.text_area("Company Profile / Description", placeholder="e.g., A technology company solving payments problems...", height=150)
    
    employment_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Temporary", "Internship"])
    department = st.selectbox("Department / Industry", [
        'Marketing & Communications', 'IT & Software', 'Sales', 'Admin', 'Manufacturing & Warehousing',
        'Accounting, Auditing & Finance', 'Engineering', 'Banking', 'Human Resources', 'Education',
        'Healthcare', 'Retail', 'Shipping & Logistics', 'Government', 'Finance', 'Hospitality', 'Other'
    ])

st.markdown("---")

if st.button("Analyze Job Posting", use_container_width=True, type="primary"):
    if not job_title or not job_desc:
        st.warning("Please fill in at least the Job Title and Job Description for an accurate analysis.")
    else:

        full_text = job_title + ' ' + job_desc + ' ' + job_requirement
        full_text_lower = full_text.lower()
        
        red_flags_list = ["whatsapp", "telegram", "fee", "payment", "registration", "bvn"]
        red_flag_count = sum(flag in full_text_lower for flag in red_flags_list)
        
        personal_emails_list = ["@gmail.com", "@yahoo.com", "@outlook.com"]
        has_personal_email = 1 if any(email in full_text_lower for email in personal_emails_list) else 0
        
        phone_pattern = r'(?:(?:\+234|0)[789][01]\d{8})'
        has_mobile_number = 1 if re.search(phone_pattern, full_text) else 0
        
        scam_score = (red_flag_count * 3) + (has_personal_email * 3) + (has_mobile_number * 3)
        

        input_data = {
            'job_desc_length': [len(job_desc)],
            'company_desc_length': [len(company_desc)],
            'percent_caps': [sum(1 for c in job_desc if c.isupper()) / (len(job_desc) + 1)],
            'exclamation_count': [job_desc.count('!')],
            'scam_score': [scam_score],
            'employment_type': [employment_type],
            'department': [department],
            'has_company_name': [1 if len(company_name) > 3 else 0],
            'has_company_desc': [1 if len(company_desc) > 10 else 0],
            'has_job_requirement': [1 if len(job_requirement) > 10 else 0]
        }
        input_df = pd.DataFrame(input_data)
        

        nigerian_proba = nigerian_model.predict_proba(input_df)[0][1]
        PREDICTION_THRESHOLD = 0.35
        is_scam_nigerian = nigerian_proba >= PREDICTION_THRESHOLD
        
        global_text_input = job_title + ' ' + job_desc + ' ' + job_requirement
        is_scam_global = global_model.predict([global_text_input])[0]
        
        st.markdown("---")
        st.subheader("Analysis Result")
        
        if is_scam_nigerian:
            st.error(f"**High Risk: LIKELY A SCAM.** (Nigerian Model Confidence: {nigerian_proba:.0%})")
            reasons = []
            if scam_score > 0:
                reasons.append("it contains high-risk indicators (like requests for payment, personal emails, or WhatsApp numbers).")
            if len(job_desc) < 150 and not reasons:
                 reasons.append("the job description is unusually short and lacks detail.")
            if not reasons:
                reasons.append("it matches patterns commonly found in fraudulent job postings.")
            st.markdown(f"**Reasoning:** Our Nigerian-focused model has flagged this post because " + ", ".join(reasons))
            st.warning("**Recommendation:** Do NOT share personal details or make any payments. Avoid this opportunity.")

        elif is_scam_global:
            st.warning(f"**Caution: POTENTIAL RISK DETECTED.**")
            st.markdown("Our primary Nigerian model did not find a direct match for local scam tactics. However, our **Global Expert model**, trained on over 17,000 job posts, detected that the **general language and structure** of this post are similar to international job scams.")
            st.info("**Recommendation:** This job may be legitimate, but it is unusual. Please research the company thoroughly before proceeding.")

        else:
            legit_probability = 1 - nigerian_proba
            st.success(f"**Low Risk: Appears Legitimate.** (Nigerian Model Confidence: {legit_probability:.0%})")
            st.markdown("Neither our Nigerian-focused model nor our Global Expert model detected high-risk indicators. As always, please conduct your own research on the company.")
st.sidebar.markdown("---")
st.sidebar.write("Made with ❤️ by O3")