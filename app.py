import streamlit as st
import pandas as pd
import joblib
import os
import re
from feature_engineering import FeatureEngineer

st.set_page_config(page_title="Yewo", layout="wide")
@st.cache_resource

def load_models():
    try:
        nigerian_model_path = os.path.join('models', 'yewo.joblib')
        global_model_path = os.path.join('models', 'yewo2.joblib')
        nigerian_pipeline = joblib.load(nigerian_model_path)
        global_pipeline = joblib.load(global_model_path)
        return nigerian_pipeline, global_pipeline
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None

nigerian_model, global_model = load_models()
if not nigerian_model or not global_model:
    st.stop()

def load_scam_example():
    st.session_state.job_title = "Urgent Hotel Receptionist (No Experience)"
    st.session_state.job_desc = "A new luxury hotel in Victoria Island is urgently seeking receptionists. No prior experience is necessary as we will provide full training. This is an immediate start position with a competitive salary. All interested candidates should forward their CV to our recruitment manager at hotelcareer.lekki@gmail.com for immediate processing."
    st.session_state.job_requirement = "Must be smart, presentable, and ready to work. There is a mandatory, non-refundable payment of 7,500 Naira required to cover your uniform and for registration with our HR agency. Contact Mr. John on WhatsApp at 08012345678 to complete your registration fee payment."
    st.session_state.company_name = "Platinum Towers Hotel & Suites"
    st.session_state.company_desc = "We are an international hospitality brand."
    
st.title("Yewo: The Nigerian Job Scam Detector")
st.markdown("""
Welcome to Yewo (Yoruba: "to check"), an AI-powered safety net for Nigerian job seekers. Our system uses a two-tier AI approach for maximum protection:
1.  A Nigerian-tuned model that identifies local scam tactics.
2.  A Global Expert model, trained on over 17,000 job posts, that detects general patterns of fraud.
""")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Job Details")
    st.text_input("Job Title", placeholder="e.g., Marketing Manager", key="job_title")
    st.text_area("Job Description", placeholder="e.g., We are looking for...", height=150, key="job_desc")
    st.text_area("Job Requirements", placeholder="e.g., 5+ years of experience...", height=150, key="job_requirement")

with col2:
    st.subheader("Company Details")
    st.text_input("Company Name", placeholder="e.g., Dangote Group", key="company_name")
    st.text_area("Company Profile / Description", placeholder="e.g., A technology company...", height=150, key="company_desc")
    employment_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Temporary", "Internship"])
    department = st.selectbox("Department / Industry", ['Marketing & Communications', 'IT & Software', 'Sales', 'Admin', 'Manufacturing & Warehousing', 'Accounting, Auditing & Finance', 'Engineering', 'Banking', 'Human Resources', 'Education', 'Healthcare', 'Retail', 'Shipping & Logistics', 'Government', 'Finance', 'Hospitality', 'Other'])

st.button("Load an example", on_click=load_scam_example)
st.markdown("---")

if st.button("Analyze Job Posting", use_container_width=True, type="primary"):
    with st.spinner('Yewo is analyzing the text... Please wait.'):
        if not st.session_state.job_title or not st.session_state.job_desc:
            st.warning("Please fill in at least the job title and job description for an accurate analysis.")
        else:
            input_data = {
                'job_title': [st.session_state.job_title],
                'job_desc': [st.session_state.job_desc],
                'job_requirement': [st.session_state.job_requirement],
                'company_name': [st.session_state.company_name],
                'company_desc': [st.session_state.company_desc],
                'employment_type': [employment_type],
                'department': [department],
                'salary': [''],
                'location': ['']
            }
            input_df = pd.DataFrame(input_data)
            
            nigerian_proba = nigerian_model.predict_proba(input_df)[0][1]
            
            global_text_input = st.session_state.job_title + ' ' + st.session_state.job_desc
            is_scam_global = global_model.predict([global_text_input])[0]
            
            st.markdown("---")
            st.subheader("Analysis Result")
            
            HIGH_RISK_THRESHOLD = 0.50
            POTENTIAL_RISK_THRESHOLD = 0.35

            if nigerian_proba >= HIGH_RISK_THRESHOLD:
                st.metric(label="Risk Level", value="High Risk", delta="Likely a Scam")
                st.error(f"Nigerian Model Confidence (Scam): {nigerian_proba:.2%}")
                with st.expander("See Detailed Reasoning"):
                    st.warning("Recommendation: Strongly advise against proceeding. Our primary model detected strong indicators of a local scam.")

            elif nigerian_proba >= POTENTIAL_RISK_THRESHOLD:
                st.metric(label="Risk Level", value="Potential Risk", delta="Caution Advised")
                st.warning(f"Nigerian Model Confidence (Scam): {nigerian_proba:.2%}")
                with st.expander("See Detailed Reasoning"):
                    st.info("Our primary model found some characteristics that are common in fraudulent postings, but they are not conclusive. Please research the company thoroughly and be very cautious.")
            
            else:
                if is_scam_global == 1:
                    st.metric(label="Risk Level", value="Potential Risk", delta="Caution Advised")
                    st.warning(f"Nigerian Model classified as low risk, but the Global Model flagged unusual language.")
                    with st.expander("See Detailed Reasoning"):
                        st.info("Our Nigerian model did not find explicit local scam tactics. However, our Global model found that the general language is similar to international scams. This is a low-priority warning, but extra research on the company is recommended.")
                
                else:
                    legit_proba = 1 - nigerian_proba
                    st.metric(label="Risk Level", value="Low Risk", delta="Appears Legitimate")
                    st.success(f"Nigerian Model Confidence (Legitimate): {legit_proba:.2%}")
                    with st.expander("See Detailed Reasoning"):
                        st.markdown("Our analysis did not detect significant high-risk indicators. As always, please conduct your own research on the company before sharing personal information.")

st.markdown("---")
st.write("Made with ❤️ by Futuremakers(O3)")