import streamlit as st
import pandas as pd
import joblib
import os
import re

st.set_page_config(page_title="Yewo - Job Scam Detector", layout="wide")

@st.cache_resource
def load_models():
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
Welcome to Yewo (Yoruba: "to check"), an AI-powered safety net for Nigerian job seekers. Our system uses a two-tier AI approach for maximum protection:
1.  A Nigerian-tuned model that identifies local scam tactics.
2.  A Global Expert model, trained on over 17,000 job posts, that detects general patterns of fraud.
""")
st.markdown("---")

if "job_title" not in st.session_state:
    st.session_state.job_title = ""
if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""
if "job_requirement" not in st.session_state:
    st.session_state.job_requirement = ""
if "company_name" not in st.session_state:
    st.session_state.company_name = ""
if "company_desc" not in st.session_state:
    st.session_state.company_desc = ""

col1, col2 = st.columns(2)

with col1:
    st.subheader("Job Details")
    st.text_input("Job Title", placeholder="e.g., Marketing Manager", key="job_title")
    st.text_area("Job Description", placeholder="e.g., We are looking for a skilled professional...", height=150, key="job_desc")
    st.text_area("Job Requirements", placeholder="e.g., 5+ years of experience with Python...", height=150, key="job_requirement")

with col2:
    st.subheader("Company Details")
    st.text_input("Company Name", placeholder="e.g., Dangote Group", key="company_name")
    st.text_area("Company Profile / Description", placeholder="e.g., A technology company solving payments problems...", height=150, key="company_desc")
    
    employment_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Temporary", "Internship"])
    department = st.selectbox("Department / Industry", [
        'Marketing & Communications', 'IT & Software', 'Sales', 'Admin', 'Manufacturing & Warehousing',
        'Accounting, Auditing & Finance', 'Engineering', 'Banking', 'Human Resources', 'Education',
        'Healthcare', 'Retail', 'Shipping & Logistics', 'Government', 'Finance', 'Hospitality', 'Other'
    ])
    
if st.button("Load an example"):
    st.session_state.job_title = "Urgent Personal Assistant (Work From Home)"
    st.session_state.job_desc = "A busy executive needs an assistant for immediate hire. No experience is needed. High salary paid weekly. You must be smart and ready to work fast. Send your CV directly to our manager on WhatsApp."
    st.session_state.job_requirement = "Must have a smartphone and internet access. A small payment of 5000 Naira is required for a registration and training fee. This is refundable after one month."
    st.session_state.company_name = "Global Reach Solutions"
    st.session_state.company_desc = "We are a fast-growing international company with partners all over the world."
    st.rerun()

st.markdown("---")

if st.button("Analyze Job Posting", use_container_width=True, type="primary"):
    with st.spinner('Yewo is analyzing the text... Please wait.'):
        job_title_val = st.session_state.job_title
        job_desc_val = st.session_state.job_desc
        
        if not job_title_val or not job_desc_val:
            st.warning("Please fill in at least the job title and job description for an accurate analysis.")
        else:
            job_requirement_val = st.session_state.job_requirement
            company_name_val = st.session_state.company_name
            company_desc_val = st.session_state.company_desc
            
            full_text = job_title_val + ' ' + job_desc_val + ' ' + job_requirement_val
            full_text_lower = full_text.lower()
            red_flags_list = ["whatsapp", "telegram", "fee", "payment", "registration", "bvn"]
            red_flag_count = sum(flag in full_text_lower for flag in red_flags_list)
            personal_emails_list = ["@gmail.com", "@yahoo.com", "@outlook.com"]
            has_personal_email = 1 if any(email in full_text_lower for email in personal_emails_list) else 0
            phone_pattern = r'(?:(?:\+234|0)[789][01]\d{8})'
            has_mobile_number = 1 if re.search(phone_pattern, full_text) else 0
            scam_score = (red_flag_count * 3) + (has_personal_email * 3) + (has_mobile_number * 3)
            
            input_data = {
                'job_desc_length': [len(job_desc_val)], 'company_desc_length': [len(company_desc_val)],
                'percent_caps': [sum(1 for c in job_desc_val if c.isupper()) / (len(job_desc_val) + 1)],
                'exclamation_count': [job_desc_val.count('!')], 'scam_score': [scam_score],
                'employment_type': [employment_type], 'department': [department],
                'has_company_name': [1 if len(company_name_val) > 3 else 0],
                'has_company_desc': [1 if len(company_desc_val) > 10 else 0],
                'has_job_requirement': [1 if len(job_requirement_val) > 10 else 0]
            }
            input_df = pd.DataFrame(input_data)
            
            nigerian_proba = nigerian_model.predict_proba(input_df)[0][1]
            PREDICTION_THRESHOLD = 0.35
            is_scam_nigerian = nigerian_proba >= PREDICTION_THRESHOLD
            
            global_text_input = job_title_val + ' ' + job_desc_val + ' ' + job_requirement_val
            is_scam_global = global_model.predict([global_text_input])[0]
            
            st.markdown("---")
            st.subheader("Analysis Result")
            
            if is_scam_nigerian:
                st.metric(label="Risk Level", value="High Risk", delta="Likely a Scam")
                st.error(f"Nigerian Model Confidence: {nigerian_proba:.2%}")
                with st.expander("See Detailed Reasoning"):
                    reasons = []
                    if scam_score > 0:
                        reasons.append("it contains high-risk indicators (like requests for payment, personal emails, or WhatsApp numbers).")
                    if len(job_desc_val) < 150 and not reasons:
                         reasons.append("the job description is unusually short and lacks detail.")
                    if not reasons:
                        reasons.append("it matches patterns commonly found in fraudulent job postings.")
                    st.markdown(f"Reasoning: Our Nigerian-focused model has flagged this post because " + ", ".join(reasons))
                    st.warning("Recommendation: Do NOT share personal details or make any payments. Avoid this opportunity.")

            elif is_scam_global:
                st.metric(label="Risk Level", value="Potential Risk", delta="Caution Advised")
                st.warning(f"Our Global Expert model detected unusual patterns.")
                with st.expander("See Detailed Reasoning"):
                    st.markdown("Our primary Nigerian model did not find a direct match for local scam tactics. However, our Global Expert model, trained on over 17,000 job posts, detected that the general language and structure of this post are similar to international job scams.")
                    st.info("Recommendation: This job may be legitimate, but it is unusual. Please research the company thoroughly before proceeding.")

            else:
                legit_probability = 1 - nigerian_proba
                st.metric(label="Risk Level", value="Low Risk", delta="Appears Legitimate")
                st.success(f"Nigerian Model Confidence: {legit_probability:.2%}")
                with st.expander("See Detailed Reasoning"):
                    st.markdown("Neither our Nigerian-focused model nor our Global Expert model detected high-risk indicators. As always, please conduct your own research on the company.")
st.markdown("---")
st.write("Made with ❤️ by O3")