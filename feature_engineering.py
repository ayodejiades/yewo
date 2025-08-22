import pandas as pd
import re
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()
        
        text_cols = ['job_title', 'company_name', 'company_desc', 'job_desc', 'job_requirement']
        for col in text_cols:
            df[col] = df[col].fillna('')

        full_text = df['job_title'] + ' ' + df['job_desc'] + ' ' + df['job_requirement']
        full_text_lower = full_text.str.lower()
        
        red_flags = ["whatsapp", "telegram", "fee", "payment", "registration", "bvn"]
        red_flag_count = full_text_lower.apply(lambda x: sum(flag in x for flag in red_flags))
        
        personal_emails = ["@gmail.com", "@yahoo.com", "@outlook.com"]
        has_personal_email = full_text_lower.apply(lambda x: 1 if any(email in x for email in personal_emails) else 0)
        
        phone_pattern = r'(?:(?:\+234|0)[789][01]\d{8})'
        has_mobile_number = full_text.apply(lambda x: 1 if re.search(phone_pattern, x) else 0)
        
        df['scam_score'] = (red_flag_count * 3) + (has_personal_email * 3) + (has_mobile_number * 3)
        df['job_desc_length'] = df['job_desc'].str.len()
        df['company_desc_length'] = df['company_desc'].str.len()
        df['percent_caps'] = df['job_desc'].apply(lambda x: sum(1 for c in x if c.isupper()) / (len(x) + 1))
        df['exclamation_count'] = df['job_desc'].str.count('!')
        df['has_company_name'] = (df['company_name'].str.len() > 3).astype(int)
        df['has_company_desc'] = (df['company_desc'].str.len() > 10).astype(int)
        df['has_job_requirement'] = (df['job_requirement'].str.len() > 10).astype(int)
        
        return df