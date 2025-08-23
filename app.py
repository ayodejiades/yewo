import gradio as gr
import pandas as pd
import joblib
import os
import re

try:
    nigerian_model_path = os.path.join('models', 'yewo.joblib')
    global_model_path = os.path.join('models', 'yewo2.joblib')
    
    nigerian_model = joblib.load(nigerian_model_path)
    global_model = joblib.load(global_model_path)
    print("Models loaded successfully.")
    
except Exception as e:
    print(f"FATAL ERROR: Could not load models. App cannot start. Error: {e}")
    nigerian_model = None
    global_model = None


def analyze_job_posting(job_title, job_desc, job_requirement, company_name, company_desc, employment_type, department):
    """
    Analyzes job details using the two-tier AI model and returns a formatted string with the result.
    """

    if not job_title or not job_desc:
        return "Please fill in at least the Job Title and Job Description for an accurate analysis."

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
        'job_desc_length': [len(job_desc)], 'company_desc_length': [len(company_desc)],
        'percent_caps': [sum(1 for c in c in job_desc if c.isupper()) / (len(job_desc) + 1)],
        'exclamation_count': [job_desc.count('!')], 'scam_score': [scam_score],
        'employment_type': [employment_type], 'department': [department],
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
    
    if is_scam_nigerian:
        return (f"HIGH RISK: LIKELY A SCAM (Nigerian Model Confidence: {nigerian_proba:.0%})\n\n"
                f"**Reasoning:** Our Nigerian-focused model has flagged this post because it contains high-risk indicators "
                f"(like requests for payment, personal emails, or WhatsApp numbers) or matches patterns commonly found in fraudulent job postings.\n\n"
                f"**Recommendation:** Do NOT share personal details or make any payments. Avoid this opportunity.")

    elif is_scam_global:
        return (f"CAUTION: POTENTIAL RISK DETECTED\n\n"
                f"**Reasoning:** Our primary Nigerian model did not find a direct match for local scam tactics. "
                f"However, our Global Expert model, trained on over 17,000 job posts, detected that the general language "
                f"and structure of this post are similar to international job scams.\n\n"
                f"**Recommendation:** This job may be legitimate, but it is unusual. Please research the company thoroughly before proceeding.")

    else:
        legit_probability = 1 - nigerian_proba
        return (f"LOW RISK: APPEARS LEGITIMATE (Nigerian Model Confidence: {legit_probability:.0%})\n\n"
                f"**Reasoning:** Neither our Nigerian-focused model nor our Global Expert model detected high-risk indicators. "
                f"As always, please conduct your own research on the company.")


inputs = [
    gr.Textbox(label="Job Title", placeholder="e.g., Marketing Manager"),
    gr.Textbox(label="Job Description", placeholder="e.g., We are looking for a skilled professional...", lines=5),
    gr.Textbox(label="Job Requirements", placeholder="e.g., 5+ years of experience with Python...", lines=5),
    gr.Textbox(label="Company Name", placeholder="e.g., Dangote Group"),
    gr.Textbox(label="Company Profile / Description", placeholder="e.g., A technology company solving payments problems...", lines=5),
    gr.Dropdown(label="Employment Type", choices=["Full-time", "Part-time", "Contract", "Temporary", "Internship"]),
    gr.Dropdown(label="Department / Industry", choices=[
        'Marketing & Communications', 'IT & Software', 'Sales', 'Admin', 'Manufacturing & Warehousing',
        'Accounting, Auditing & Finance', 'Engineering', 'Banking', 'Human Resources', 'Education',
        'Healthcare', 'Retail', 'Shipping & Logistics', 'Government', 'Finance', 'Hospitality', 'Other'
    ])
]

outputs = gr.Markdown(label="Analysis Result") 

interface = gr.Interface(
    fn=analyze_job_posting,
    inputs=inputs,
    outputs=outputs,
    title="Yewo: The Nigerian Job Scam Detector",
    description="An AI safety net for Nigerian job seekers using a two-tier model to detect local and global scam tactics."
)

if __name__ == "__main__":
    interface.launch()