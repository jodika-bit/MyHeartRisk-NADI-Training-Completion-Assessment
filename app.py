import streamlit as st
import pandas as pd
from datetime import datetime
import json
import hashlib
import base64
from pathlib import Path
from io import BytesIO
from html import escape

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except Exception:
    FPDF_AVAILABLE = False


# ============================================================
# MyHeartRisk NADI Training Completion Assessment
# Streamlit App
# Author: CARE Institute UiTM / MyHeartRisk Team
# Purpose:
#   - Train and assess NADI users using 10 dummy case scenarios
#   - Validate pathway selection, expected result, and action decision
#   - Complete knowledge check
#   - Generate certificate of completion after passing
# ============================================================

st.set_page_config(
    page_title="MyHeartRisk NADI Certification",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# CONFIGURATION
# -----------------------------
PASS_MARK = 80
TOTAL_CASES_REQUIRED = 10

GOOGLE_FORM_URL = "https://forms.gle/TG4Ah7w18BdwUwFC6"
CERTIFICATE_VERIFY_BASE_URL = "https://myheartrisk.uitm.edu.my/verify"

# Certificate assets. Keep these files in the /assets folder.
APP_DIR = Path(__file__).parent
ASSET_DIR = APP_DIR / "assets"
UITM_CARE_LOGO = ASSET_DIR / "uitm_care_logo.png"
MYHEARTRISK_ICON = ASSET_DIR / "myheartrisk_icon.png"
SIGNATURE_IMAGE = ASSET_DIR / "signature_sazzli.png"
GOLD_SEAL_IMAGE = ASSET_DIR / "myheartrisk_gold_seal.png"


# -----------------------------
# CASE SCENARIOS
# -----------------------------
CASES = [
    {
        "case_no": 1,
        "title": "Low-risk community participant",
        "name": "Ahmad Hakim Razali",
        "ic": "Test 1",
        "dob_age": "29 Nov 1994 (31 years)",
        "gender": "Male",
        "race": "Malay",
        "phone": "012-345 6789",
        "state_centre": "Selangor / Sri Meranti Sri Damansara",
        "residential_area": "Urban",
        "occupation": "Technician",
        "marital_status": "Single",
        "education": "Diploma",
        "height_weight": "172 cm / 70 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Never",
            "Diabetes": "No",
            "Total Cholesterol": "4.7 mmol/L",
            "HDL": "1.3 mmol/L",
            "BP": "117/68 mmHg",
            "HR": "73 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "FRS Low + REDISCOVER Low",
        "expected_action": "Lifestyle advice + optional nudges",
        "teaching_point": "Low-risk community case. Reinforce healthy lifestyle and optional digital nudges.",
    },
    {
        "case_no": 2,
        "title": "Intermediate FRS with smoking risk",
        "name": "Siti Aisyah Mohd Fadzil",
        "ic": "Test 2",
        "dob_age": "10 May 1976 (49 years)",
        "gender": "Female",
        "race": "Malay",
        "phone": "013-778 2211",
        "state_centre": "Johor / NADI Muar",
        "residential_area": "Semi-urban",
        "occupation": "Clerk",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "158 cm / 68 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Current smoker",
            "Diabetes": "No",
            "Total Cholesterol": "5.6 mmol/L",
            "HDL": "1.1 mmol/L",
            "BP": "145/88 mmHg",
            "HR": "86 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "FRS Intermediate + REDISCOVER Low",
        "expected_action": "KK follow-up 4–12 weeks + smoking support + nudges opt-in",
        "teaching_point": "Intermediate risk needs clinic follow-up, smoking support and nudges.",
    },
    {
        "case_no": 3,
        "title": "High-risk community participant",
        "name": "Muthu Kumar Ramasamy",
        "ic": "Test 3",
        "dob_age": "2 Feb 1970 (56 years)",
        "gender": "Male",
        "race": "Indian",
        "phone": "017-600 4455",
        "state_centre": "Perak / NADI Bagan Datuk",
        "residential_area": "Rural",
        "occupation": "Lorry driver",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "168 cm / 88 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Former smoker",
            "Diabetes": "Yes",
            "Total Cholesterol": "6.2 mmol/L",
            "HDL": "0.9 mmol/L",
            "BP": "165/95 mmHg",
            "HR": "92 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "FRS High + REDISCOVER Low",
        "expected_action": "Referral letter + follow-up 1–2 weeks + nudges opt-in",
        "teaching_point": "High FRS should trigger referral action even if REDISCOVER is low.",
    },
    {
        "case_no": 4,
        "title": "Highest-risk rule case",
        "name": "Lim Wei Jian",
        "ic": "Test 4",
        "dob_age": "3 Mar 1974 (52 years)",
        "gender": "Male",
        "race": "Chinese",
        "phone": "012-034 5678",
        "state_centre": "Selangor / Sri Meranti Sri Damansara",
        "residential_area": "Urban",
        "occupation": "Sales executive",
        "marital_status": "Married",
        "education": "University",
        "height_weight": "160 cm / 60 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Current smoker",
            "Diabetes": "Yes",
            "Total Cholesterol": "5.6 mmol/L",
            "HDL": "1.3 mmol/L",
            "BP": "120/60 mmHg",
            "HR": "70 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "FRS High + REDISCOVER Low",
        "expected_action": "Follow highest action level → referral letter",
        "teaching_point": "If any model is high risk, staff should follow the highest urgency action.",
    },
    {
        "case_no": 5,
        "title": "Low calculated risk but very high BP",
        "name": "Nurul Izzati Hassan",
        "ic": "Test 5",
        "dob_age": "18 Aug 1985 (40 years)",
        "gender": "Female",
        "race": "Malay",
        "phone": "019-222 1100",
        "state_centre": "Sabah / NADI Tawau",
        "residential_area": "Rural",
        "occupation": "Trader",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "155 cm / 74 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Never",
            "Diabetes": "No",
            "Total Cholesterol": "5.0 mmol/L",
            "HDL": "1.4 mmol/L",
            "BP": "170/100 mmHg",
            "HR": "98 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "FRS Low + REDISCOVER Low",
        "expected_action": "Repeat BP; if persistently high, urgent clinic follow-up; referral if threshold met",
        "teaching_point": "A low model risk does not mean ignoring a very high blood pressure reading.",
    },
    {
        "case_no": 6,
        "title": "Missing lipid values and caregiver phone",
        "name": "Haji Osman Mat Yusof",
        "ic": "Test 6",
        "dob_age": "7 Jul 1959 (67 years)",
        "gender": "Male",
        "race": "Malay",
        "phone": "No personal phone",
        "caregiver": "Rohani Osman (Daughter) / 016-778 8899",
        "state_centre": "Kelantan / NADI Pasir Mas",
        "residential_area": "Rural",
        "occupation": "Retired",
        "marital_status": "Married",
        "education": "Primary",
        "height_weight": "165 cm / 72 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Current smoker",
            "Diabetes": "Unknown",
            "Total Cholesterol": "Not available",
            "HDL": "Not available",
            "BP": "152/92 mmHg",
            "HR": "88 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "System warning: estimated/default values OR block if mandatory",
        "expected_action": "Do not guess; advise clinic lipid test; use caregiver contact with consent",
        "teaching_point": "Unknown values must not be guessed. Caregiver contact requires consent.",
    },
    {
        "case_no": 7,
        "title": "Stable post-ACS on medications",
        "name": "Mohd Faizal Zulkifli",
        "ic": "Test 7",
        "dob_age": "12 Jan 1968 (58 years)",
        "gender": "Male",
        "race": "Malay",
        "phone": "Not stated",
        "caregiver": "Rohani Osman (Daughter) / 016-778 8899",
        "state_centre": "Selangor / NADI Subang",
        "residential_area": "Urban",
        "occupation": "Security guard",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "152 cm / 69 kg",
        "heart_attack_history": "Yes",
        "inputs": {
            "Killip": "I",
            "Renal Disease": "No",
            "PCI": "Yes",
            "Beta blocker": "Yes",
            "ACE inhibitor": "Yes",
            "Statin": "Yes",
            "HR": "70 bpm",
            "Total Cholesterol": "5.2 mmol/L",
            "Fasting Glucose": "5.5 mmol/L",
        },
        "expected_pathway": "ACS",
        "expected_result": "ACS Low",
        "expected_action": "Reinforce adherence + planned clinic follow-up + nudges optional",
        "teaching_point": "Stable ACS patient with medication adherence still needs planned follow-up.",
    },
    {
        "case_no": 8,
        "title": "ACS high-risk with renal disease",
        "name": "Rosmah Binti Salleh",
        "ic": "Test 8",
        "dob_age": "22 Oct 1963 (62 years)",
        "gender": "Female",
        "race": "Malay",
        "phone": "014-555 1212",
        "state_centre": "Sarawak / NADI Sibu",
        "residential_area": "Semi-urban",
        "occupation": "Housewife",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "150 cm / 70 kg",
        "heart_attack_history": "Yes",
        "inputs": {
            "Killip": "II",
            "Renal Disease": "Yes",
            "PCI": "Yes",
            "Beta blocker": "Yes",
            "ACE inhibitor": "Yes",
            "Statin": "Yes",
            "HR": "85 bpm",
            "SBP": "150 mmHg",
            "Total Cholesterol": "6.0 mmol/L",
            "Fasting Glucose": "9.0 mmol/L",
        },
        "expected_pathway": "ACS",
        "expected_result": "ACS High",
        "expected_action": "Referral letter if threshold met; follow-up soon 1–2 weeks",
        "teaching_point": "ACS high-risk case needs timely clinic or hospital follow-up.",
    },
    {
        "case_no": 9,
        "title": "ACS high-risk Killip III",
        "name": "Rajoo A/L Subramaniam",
        "ic": "Test 9",
        "dob_age": "3 Mar 1961 (65 years)",
        "gender": "Male",
        "race": "Indian",
        "phone": "012334455",
        "state_centre": "Penang / NADI Seberang Perai",
        "residential_area": "Urban",
        "occupation": "Retired",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "166 cm / 84 kg",
        "heart_attack_history": "Yes",
        "inputs": {
            "Killip": "III",
            "Renal Disease": "Yes",
            "PCI": "No",
            "Beta blocker": "No",
            "ACE inhibitor": "No",
            "Statin": "No",
            "Systolic": "135 mmHg",
            "HR": "100 bpm",
            "Total Cholesterol": "7.0 mmol/L",
            "Fasting Glucose": "10.0 mmol/L",
        },
        "expected_pathway": "ACS",
        "expected_result": "ACS High",
        "expected_action": "Urgent referral + referral letter mandatory + safety advice",
        "teaching_point": "High-risk ACS with Killip III and uncontrolled risk factors requires urgent referral.",
    },
    {
        "case_no": 10,
        "title": "ACS with estimated/default values",
        "name": "Siti Nuzha Binti Ahmad",
        "ic": "Test 10",
        "dob_age": "19 Sep 1993 (32 years)",
        "gender": "Female",
        "race": "Malay",
        "phone": "01123223232",
        "state_centre": "Pahang / NADI Pekan",
        "residential_area": "Semi-urban",
        "occupation": "Not working",
        "marital_status": "Married",
        "education": "University",
        "height_weight": "154 cm / 50 kg",
        "heart_attack_history": "Yes",
        "inputs": {
            "Killip": "III",
            "Renal Disease": "Unknown → default used",
            "PCI": "Yes",
            "Beta blocker": "Yes",
            "ACE inhibitor": "Yes",
            "Statin": "Yes",
            "Systolic": "140 mmHg",
            "HR": "90 bpm",
            "Total Cholesterol": "7.0 mmol/L",
            "Fasting Glucose": "7.5 mmol/L",
        },
        "expected_pathway": "ACS",
        "expected_result": "ACS calculated + warning: estimated/default values used",
        "expected_action": "Referral based on category; advise clinic confirmation of unknown variables",
        "teaching_point": "If default values are used, the result must clearly warn staff and advise confirmation.",
    },
]


# -----------------------------
# KNOWLEDGE CHECK
# -----------------------------
KNOWLEDGE_QUESTIONS = [
    {
        "question": "If the participant has NO previous heart attack or ACS, which pathway should be used?",
        "options": ["ACS pathway only", "FRS + REDISCOVER pathway", "Referral pathway only", "Medication pathway only"],
        "answer": "FRS + REDISCOVER pathway",
        "explanation": "No previous heart attack means the community screening pathway is used.",
    },
    {
        "question": "If the participant has been diagnosed before with heart attack or ACS, which pathway should be used?",
        "options": ["FRS only", "REDISCOVER only", "ACS pathway", "No assessment needed"],
        "answer": "ACS pathway",
        "explanation": "Previous heart attack or ACS should trigger the ACS pathway.",
    },
    {
        "question": "If FRS result is High but REDISCOVER result is Low, what should NADI staff do?",
        "options": ["Ignore the high result", "Follow the Low result", "Follow the highest action level", "Repeat the whole assessment only"],
        "answer": "Follow the highest action level",
        "explanation": "The action level should follow the highest urgency result.",
    },
    {
        "question": "For a participant with high FRS result, what is the correct NADI action?",
        "options": ["Lifestyle advice only", "Referral letter and follow-up advice", "No action if participant feels well", "Delete the assessment"],
        "answer": "Referral letter and follow-up advice",
        "explanation": "High-risk participants should receive referral and follow-up advice.",
    },
    {
        "question": "If the participant does not know their cholesterol result, what should staff do?",
        "options": ["Guess the value", "Enter a normal value", "Mark as not available / not sure", "Use another participant’s value"],
        "answer": "Mark as not available / not sure",
        "explanation": "Unknown values must not be guessed.",
    },
    {
        "question": "If the participant says they take medicine but do not know the medicine name, what should be selected?",
        "options": ["No", "Yes, but medicine name unknown", "Stop the assessment", "Assume no medication"],
        "answer": "Yes, but medicine name unknown",
        "explanation": "Medication uncertainty should be captured without wrongly marking as No.",
    },
    {
        "question": "If BP is 170/100 mmHg during screening, what should staff do?",
        "options": ["Ignore it", "Repeat BP and advise clinic follow-up if still high", "Tell participant it is normal", "Enter a lower value"],
        "answer": "Repeat BP and advise clinic follow-up if still high",
        "explanation": "Very high BP requires repeat measurement and clinical follow-up.",
    },
    {
        "question": "If the participant has no phone and uses a caregiver’s number, what is required?",
        "options": ["Use caregiver number without asking", "Use any available phone number", "Obtain consent to use caregiver contact", "Do not record any contact"],
        "answer": "Obtain consent to use caregiver contact",
        "explanation": "Caregiver phone use requires consent.",
    },
    {
        "question": "If a post-heart attack participant says the doctor told them there was “water in the lungs”, what does this suggest?",
        "options": ["No heart failure signs", "Pulmonary oedema / higher ACS severity", "Normal finding", "Smoking history only"],
        "answer": "Pulmonary oedema / higher ACS severity",
        "explanation": "Water in the lungs is a high-severity ACS/heart failure indicator.",
    },
    {
        "question": "For an ACS participant with high-risk result, what should NADI staff do?",
        "options": ["Give lifestyle advice only", "Generate referral/follow-up letter and advise clinic or hospital review", "Ignore because heart attack already happened", "Repeat screening next year only"],
        "answer": "Generate referral/follow-up letter and advise clinic or hospital review",
        "explanation": "ACS high risk requires referral and follow-up.",
    },
    {
        "question": "If a participant currently has chest pain, severe breathlessness, fainting, or sweating, what should staff do?",
        "options": ["Continue routine screening only", "Send WhatsApp advice only", "Advise urgent medical assessment", "Wait for certificate verification"],
        "answer": "Advise urgent medical assessment",
        "explanation": "Current warning symptoms require urgent medical assessment.",
    },
    {
        "question": "How should the participant receive the result through WhatsApp?",
        "options": ["Admin sends result to any number", "Participant scans QR, starts WhatsApp chat, details are verified, then result is sent", "Result is posted in public group", "Result is shared with all NADI staff"],
        "answer": "Participant scans QR, starts WhatsApp chat, details are verified, then result is sent",
        "explanation": "Identity should be verified before sending results.",
    },
    {
        "question": "If the participant is high risk, what should be sent?",
        "options": ["Result summary only", "Referral letter only", "Result summary plus referral letter", "No result should be sent"],
        "answer": "Result summary plus referral letter",
        "explanation": "High-risk participants should receive the result summary and referral letter.",
    },
    {
        "question": "Which statement is correct about data privacy?",
        "options": ["Results can be shared with anyone", "Results should be shared only with the verified participant or consented caregiver", "Results can be posted in a NADI WhatsApp group", "Results can be sent without checking identity"],
        "answer": "Results should be shared only with the verified participant or consented caregiver",
        "explanation": "Results must be shared privately and only after verification/consent.",
    },
    {
        "question": "When should the Certificate of Completion be issued?",
        "options": ["After login only", "After completing one case", "After completing all 10 cases, submitting the form, and passing the knowledge check", "Before training starts"],
        "answer": "After completing all 10 cases, submitting the form, and passing the knowledge check",
        "explanation": "Certification requires full completion and competency check.",
    },
]


# -----------------------------
# STYLES
# -----------------------------
def inject_css():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 38px;
            font-weight: 800;
            color: #003B73;
            margin-bottom: 0;
        }
        .subtitle {
            font-size: 18px;
            color: #4A6378;
            margin-top: 0;
        }
        .metric-card {
            background: #F3F8FF;
            border: 1px solid #D8E7F7;
            border-radius: 14px;
            padding: 16px;
            text-align: center;
        }
        .section-card {
            background: #FFFFFF;
            border: 1px solid #E5EAF0;
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }
        .success-box {
            background: #EAF7EE;
            border-left: 6px solid #17A34A;
            border-radius: 12px;
            padding: 14px;
        }
        .warning-box {
            background: #FFF8E6;
            border-left: 6px solid #F2A900;
            border-radius: 12px;
            padding: 14px;
        }
        .danger-box {
            background: #FDECEC;
            border-left: 6px solid #D92D20;
            border-radius: 12px;
            padding: 14px;
        }
        .blue-box {
            background: #EAF3FF;
            border-left: 6px solid #005B96;
            border-radius: 12px;
            padding: 14px;
        }
        .small-text {
            font-size: 13px;
            color: #536878;
        }
        .certificate {
            position: relative;
            border: 10px solid #D4AF37;
            padding: 34px 42px 28px 42px;
            border-radius: 20px;
            background: radial-gradient(circle at top, #ffffff 0%, #fffaf0 55%, #fff3d5 100%);
            text-align: center;
            font-family: Arial, sans-serif;
            min-height: 690px;
            box-shadow: 0 8px 28px rgba(0,0,0,0.12);
            overflow: hidden;
        }
        .certificate::before {
            content: "";
            position: absolute;
            inset: 18px;
            border: 2px solid #0B4A7B;
            border-radius: 14px;
            pointer-events: none;
        }
        .certificate-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 10px;
        }
        .cert-logo-left {
            height: 70px;
            max-width: 420px;
            object-fit: contain;
        }
        .cert-logo-right {
            height: 70px;
            width: 70px;
            object-fit: contain;
        }
        .certificate h1 {
            color: #003B73;
            font-size: 42px;
            margin: 4px 0 2px 0;
            letter-spacing: 0.5px;
        }
        .certificate h2 {
            color: #D92D20;
            font-size: 28px;
            margin: 8px 0 8px 0;
            letter-spacing: 1px;
        }
        .certificate .programme {
            color: #003B73;
            font-size: 16px;
            margin-bottom: 22px;
        }
        .certificate .name {
            font-size: 34px;
            font-weight: 800;
            color: #003B73;
            border-bottom: 3px solid #D4AF37;
            display: inline-block;
            padding: 8px 28px;
            margin: 12px 0 18px 0;
            min-width: 55%;
        }
        .certificate .statement {
            max-width: 780px;
            margin: 0 auto;
            line-height: 1.55;
            font-size: 16px;
        }
        .certificate-meta {
            margin: 26px auto 20px auto;
            font-size: 14px;
            color: #1B2B3A;
        }
        .signature-block {
            margin: 12px auto 8px auto;
            text-align: center;
        }
        .signature-img {
            height: 82px;
            object-fit: contain;
            margin-bottom: -8px;
        }
        .signature-line {
            width: 260px;
            border-top: 1.5px solid #1B2B3A;
            margin: 0 auto 6px auto;
        }
        .certificate .cert-footer {
            margin-top: 18px;
            color: #536878;
            font-size: 12px;
        }
        .seal-img {
            position: absolute;
            right: 48px;
            bottom: 52px;
            height: 92px;
            width: 92px;
            object-fit: contain;
            opacity: 0.95;
        }
        @keyframes celebratePulse {
            0% { transform: scale(1); box-shadow: 0 0 0 rgba(23,163,74,0.25); }
            50% { transform: scale(1.01); box-shadow: 0 8px 24px rgba(23,163,74,0.20); }
            100% { transform: scale(1); box-shadow: 0 0 0 rgba(23,163,74,0.25); }
        }
        .celebration-banner {
            background: linear-gradient(90deg, #EAF7EE, #EAF3FF);
            border: 1px solid #B7E4C7;
            border-left: 8px solid #17A34A;
            border-radius: 16px;
            padding: 16px 18px;
            margin: 14px 0;
            animation: celebratePulse 1.2s ease-in-out 1;
        }
        .celebration-title {
            font-size: 20px;
            font-weight: 800;
            color: #0B5D1E;
            margin-bottom: 4px;
        }
        .celebration-detail {
            color: #1B2B3A;
            font-size: 15px;
        }
        .next-action-box {
            background: #F8FBFF;
            border: 1px dashed #0B4A7B;
            border-radius: 14px;
            padding: 14px;
            margin-top: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# HELPERS
# -----------------------------
def init_state():
    defaults = {
        "current_step": "1. Training",
        "trainee": {},
        "case_answers": {},
        "knowledge_answers": {},
        "google_form_submitted": False,
        "declaration_agreed": False,
        "certificate_id": None,
        "section_completed": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value



def mark_section_complete(section_name: str):
    """Record that a training section has been completed."""
    st.session_state.section_completed[section_name] = True


def celebrate_once(event_key: str, message: str = "Section completed. Well done!"):
    """
    Show balloons/toast once per milestone so the app does not keep celebrating
    on every rerun.
    """
    state_key = f"celebrated_{event_key}"
    if not st.session_state.get(state_key, False):
        st.balloons()
        try:
            st.toast(message, icon="🎉")
        except Exception:
            pass
        st.session_state[state_key] = True


def celebration_banner(title: str, detail: str):
    """Show a visual completion banner."""
    st.markdown(
        f"""
        <div class="celebration-banner">
            <div class="celebration-title">🎉 {title}</div>
            <div class="celebration-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def go_next_button(label: str, next_step: str, key: str):
    """Reusable primary next button."""
    if st.button(label, type="primary", key=key):
        st.session_state.current_step = next_step
        st.rerun()


def image_data_uri(path: Path) -> str:
    """Return a base64 data URI for embedding local images in the HTML certificate."""
    try:
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    except Exception:
        return ""
    return ""


def safe_pdf_image(pdf, path: Path, x: float, y: float, w: float = 0, h: float = 0):
    """Insert image into FPDF only if the image exists."""
    try:
        if path.exists():
            pdf.image(str(path), x=x, y=y, w=w, h=h)
    except Exception:
        # Continue certificate generation even if one image fails.
        pass


def get_certificate_id(name: str, email: str) -> str:
    today = datetime.now().strftime("%Y%m%d")
    raw = f"{name}-{email}-{today}-MyHeartRisk-NADI"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:8].upper()
    return f"MHR-NADI-{today}-{digest}"


def get_case_score():
    total = len(CASES)
    correct = 0
    for case in CASES:
        ans = st.session_state.case_answers.get(case["case_no"], {})
        if (
            ans.get("completed")
            and ans.get("pathway") == case["expected_pathway"]
            and ans.get("result") == case["expected_result"]
            and ans.get("action") == case["expected_action"]
        ):
            correct += 1
    return correct, total


def get_knowledge_score():
    total = len(KNOWLEDGE_QUESTIONS)
    correct = 0
    for i, q in enumerate(KNOWLEDGE_QUESTIONS):
        if st.session_state.knowledge_answers.get(i) == q["answer"]:
            correct += 1
    percent = round((correct / total) * 100, 1) if total else 0
    return correct, total, percent


def is_eligible():
    case_correct, case_total = get_case_score()
    knowledge_correct, knowledge_total, knowledge_percent = get_knowledge_score()
    trainee = st.session_state.trainee
    required_trainee = all([
        trainee.get("full_name"),
        trainee.get("email"),
        trainee.get("role"),
        trainee.get("centre"),
        trainee.get("state"),
    ])
    return (
        required_trainee
        and case_correct == case_total
        and knowledge_percent >= PASS_MARK
        and st.session_state.google_form_submitted
        and st.session_state.declaration_agreed
    )


def trainee_table():
    trainee = st.session_state.trainee
    return pd.DataFrame(
        [
            ["Full name", trainee.get("full_name", "")],
            ["Email", trainee.get("email", "")],
            ["Phone", trainee.get("phone", "")],
            ["Role", trainee.get("role", "")],
            ["Organisation", trainee.get("organisation", "")],
            ["NADI centre / site", trainee.get("centre", "")],
            ["State", trainee.get("state", "")],
            ["Training mode", trainee.get("mode", "")],
            ["Cohort", trainee.get("cohort", "")],
        ],
        columns=["Item", "Details"],
    )


def build_completion_record():
    case_correct, case_total = get_case_score()
    knowledge_correct, knowledge_total, knowledge_percent = get_knowledge_score()
    trainee = st.session_state.trainee
    cert_id = st.session_state.certificate_id or get_certificate_id(
        trainee.get("full_name", "UNKNOWN"),
        trainee.get("email", "UNKNOWN"),
    )

    record = {
        "app": "MyHeartRisk NADI Training Completion Assessment",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "trainee": trainee,
        "completion": {
            "case_score": f"{case_correct}/{case_total}",
            "knowledge_score": f"{knowledge_correct}/{knowledge_total}",
            "knowledge_percent": knowledge_percent,
            "google_form_submitted": st.session_state.google_form_submitted,
            "declaration_agreed": st.session_state.declaration_agreed,
            "eligible_for_certificate": is_eligible(),
            "certificate_id": cert_id,
        },
        "case_answers": st.session_state.case_answers,
        "knowledge_answers": st.session_state.knowledge_answers,
    }
    return record


def certificate_html():
    trainee = st.session_state.trainee
    full_name = escape(trainee.get("full_name", "[FULL NAME]"))
    mode = escape(trainee.get("mode", "Online / Hybrid / Onsite"))
    cohort = escape(trainee.get("cohort", "1"))
    today = datetime.now().strftime("%d %b %Y")
    cert_id = st.session_state.certificate_id or get_certificate_id(
        trainee.get("full_name", ""),
        trainee.get("email", ""),
    )
    verify_url = f"{CERTIFICATE_VERIFY_BASE_URL}/{cert_id}"

    uitm_logo = image_data_uri(UITM_CARE_LOGO)
    mhr_icon = image_data_uri(MYHEARTRISK_ICON)
    signature = image_data_uri(SIGNATURE_IMAGE)
    gold_seal = image_data_uri(GOLD_SEAL_IMAGE)

    left_logo_html = f'<img class="cert-logo-left" src="{uitm_logo}" />' if uitm_logo else '<div></div>'
    right_logo_html = f'<img class="cert-logo-right" src="{mhr_icon}" />' if mhr_icon else '<div></div>'
    signature_html = f'<img class="signature-img" src="{signature}" />' if signature else ''
    seal_html = f'<img class="seal-img" src="{gold_seal}" />' if gold_seal else ''

    return f"""
    <div class="certificate">
        <div class="certificate-top">
            {left_logo_html}
            {right_logo_html}
        </div>
        <h1>MyHeartRisk</h1>
        <h2>CERTIFICATE OF COMPLETION</h2>
        <p class="programme"><strong>NADI MADANI: Jantung Sihat [MyHeartRisk] - Train-the-Trainer (ToT)</strong></p>
        <p>This certificate is proudly presented to</p>
        <div class="name">{full_name}</div>
        <p class="statement">
            For successfully completing the MyHeartRisk Train-the-Trainer programme and
            demonstrating competency to conduct standardized cardiovascular risk screening
            and participant counselling at NADI centres.
        </p>
        <p class="certificate-meta"><strong>Date of Completion:</strong> {today} &nbsp; | &nbsp; <strong>Venue/Mode:</strong> {mode} &nbsp; | &nbsp; <strong>Cohort:</strong> {cohort}</p>
        <div class="signature-block">
            {signature_html}
            <div class="signature-line"></div>
            <p><strong>Prof. Dr. Sazzli Shahlan Kasim</strong><br/>Director of CARE Institute, UiTM</p>
        </div>
        <p class="cert-footer"><strong>Certificate ID:</strong> {cert_id} &nbsp; • &nbsp; <strong>Verification:</strong> {verify_url}</p>
        <p class="cert-footer">Generated by CARE Institute UiTM x NADI/MCMC</p>
        {seal_html}
    </div>
    """

def generate_certificate_pdf():
    trainee = st.session_state.trainee
    full_name = trainee.get("full_name", "[FULL NAME]")
    mode = trainee.get("mode", "Online / Hybrid / Onsite")
    cohort = trainee.get("cohort", "1")
    today = datetime.now().strftime("%d %b %Y")
    cert_id = st.session_state.certificate_id or get_certificate_id(
        trainee.get("full_name", ""),
        trainee.get("email", ""),
    )

    if not FPDF_AVAILABLE:
        return None

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    # Background and borders
    pdf.set_fill_color(255, 250, 240)
    pdf.rect(0, 0, 297, 210, style="F")

    pdf.set_draw_color(212, 175, 55)
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)

    pdf.set_draw_color(0, 59, 115)
    pdf.set_line_width(0.7)
    pdf.rect(15, 15, 267, 180)

    # Logos from uploaded PPT certificate template
    safe_pdf_image(pdf, UITM_CARE_LOGO, x=21, y=21, w=118)
    safe_pdf_image(pdf, MYHEARTRISK_ICON, x=256, y=20, w=18)

    pdf.set_xy(0, 42)
    pdf.set_font("Helvetica", "B", 34)
    pdf.set_text_color(0, 59, 115)
    pdf.cell(0, 18, "MyHeartRisk", ln=True, align="C")

    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(217, 45, 32)
    pdf.cell(0, 14, "CERTIFICATE OF COMPLETION", ln=True, align="C")

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(0, 59, 115)
    pdf.cell(0, 10, "NADI MADANI: Jantung Sihat [MyHeartRisk] - Train-the-Trainer (ToT)", ln=True, align="C")

    pdf.ln(7)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "This certificate is proudly presented to", ln=True, align="C")

    pdf.set_font("Helvetica", "B", 27)
    pdf.set_text_color(0, 59, 115)
    pdf.cell(0, 16, full_name[:80], ln=True, align="C")

    # Name underline
    pdf.set_draw_color(212, 175, 55)
    pdf.set_line_width(0.8)
    pdf.line(78, 112, 219, 112)

    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(0, 0, 0)
    paragraph = (
        "For successfully completing the MyHeartRisk Train-the-Trainer programme and demonstrating competency "
        "to conduct standardized cardiovascular risk screening and participant counselling at NADI centres."
    )
    pdf.set_x(34)
    pdf.multi_cell(230, 7, paragraph, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Date of Completion: {today}   |   Venue/Mode: {mode}   |   Cohort: {cohort}", ln=True, align="C")

    # Signature image and signatory details
    safe_pdf_image(pdf, SIGNATURE_IMAGE, x=128, y=145, w=43)
    pdf.set_draw_color(27, 43, 58)
    pdf.set_line_width(0.4)
    pdf.line(103, 169, 194, 169)
    pdf.set_xy(0, 170)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "Prof. Dr. Sazzli Shahlan Kasim", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Director of CARE Institute, UiTM", ln=True, align="C")

    # Optional gold seal / badge
    if GOLD_SEAL_IMAGE.exists():
        safe_pdf_image(pdf, GOLD_SEAL_IMAGE, x=239, y=149, w=27)

    pdf.set_y(187)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(83, 104, 120)
    pdf.cell(0, 5, f"Certificate ID: {cert_id}   |   Verification: {CERTIFICATE_VERIFY_BASE_URL}/{cert_id}", ln=True, align="C")
    pdf.cell(0, 5, "Generated by CARE Institute UiTM x NADI/MCMC", ln=True, align="C")

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)


# -----------------------------
# SIDEBAR
# -----------------------------
def sidebar():
    st.sidebar.markdown("## ❤️ MyHeartRisk")
    st.sidebar.markdown("### NADI Certification")
    steps = [
        "1. Training",
        "2. Trainee Details",
        "3. Case Scenarios",
        "4. Knowledge Check",
        "5. Google Form",
        "6. Certificate",
    ]

    selected = st.sidebar.radio(
        "Go to section",
        options=steps,
        index=steps.index(st.session_state.current_step)
        if st.session_state.current_step in steps
        else 0,
    )
    st.session_state.current_step = selected

    st.sidebar.divider()

    case_correct, case_total = get_case_score()
    knowledge_correct, knowledge_total, knowledge_percent = get_knowledge_score()

    st.sidebar.metric("Case completion", f"{case_correct}/{case_total}")
    st.sidebar.metric("Knowledge score", f"{knowledge_percent}%")
    st.sidebar.metric("Pass mark", f"{PASS_MARK}%")

    if is_eligible():
        st.sidebar.success("Eligible for certificate")
    else:
        st.sidebar.warning("Not yet eligible")

    st.sidebar.divider()
    st.sidebar.markdown("### Session progress")
    completed_sections = st.session_state.get("section_completed", {})
    for section_label in [
        "Training briefing",
        "Trainee details",
        "Case scenarios",
        "Knowledge check",
        "Google form",
        "Certificate",
    ]:
        if completed_sections.get(section_label):
            st.sidebar.success(f"✅ {section_label}")
        else:
            st.sidebar.caption(f"⬜ {section_label}")

    st.sidebar.divider()
    st.sidebar.caption("Training rule: complete all 10 cases, submit form, pass knowledge check, and agree declaration.")


# -----------------------------
# PAGES
# -----------------------------
def page_training():
    st.markdown('<p class="main-title">MyHeartRisk NADI Training Completion Assessment</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">10 Case Scenarios + Knowledge Check → Certificate of Completion</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card"><h3>10</h3><p>Case Scenarios</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><h3>15</h3><p>Knowledge Questions</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h3>{PASS_MARK}%</h3><p>Pass Mark</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><h3>1</h3><p>Certificate</p></div>', unsafe_allow_html=True)

    st.markdown("### Training flow")
    st.markdown(
        """
        <div class="blue-box">
        <strong>Training → Complete 10 cases → Compare expected outputs → Submit Google Form → Knowledge Check → Admin verification → Certificate</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### What the trainee must learn")
    st.write(
        """
        - Select the correct pathway:
          - **Heart Attack History = No → FRS + REDISCOVER**
          - **Heart Attack History = Yes → ACS pathway**
        - Use **Not sure / Not available** instead of guessing.
        - Follow the **highest-risk action rule**.
        - Generate referral or follow-up advice for high-risk participants.
        - Deliver results privately through verified participant or consented caregiver contact.
        """
    )

    st.markdown("### Certification requirement")
    st.markdown(
        f"""
        <div class="success-box">
        Certificate is unlocked only after all conditions are met:<br>
        1. Trainee details completed<br>
        2. All {TOTAL_CASES_REQUIRED} cases completed correctly<br>
        3. Knowledge check score ≥ {PASS_MARK}%<br>
        4. Google Form submission declared<br>
        5. SOP declaration agreed
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="next-action-box"><strong>Complete this session:</strong> Click below after reading the training flow and certification requirement.</div>', unsafe_allow_html=True)

    if st.button("✅ Mark Training Briefing Complete", type="primary", key="complete_training_briefing"):
        mark_section_complete("Training briefing")
        celebrate_once("training_briefing", "Training briefing completed.")
        celebration_banner("Training Briefing Completed", "You may now proceed to trainee details.")

    if st.session_state.section_completed.get("Training briefing"):
        go_next_button("Next: Enter Trainee Details ➜", "2. Trainee Details", "next_to_trainee_details")


def page_trainee_details():
    st.title("Trainee Details")

    with st.form("trainee_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full name *", value=st.session_state.trainee.get("full_name", ""))
            email = st.text_input("Email *", value=st.session_state.trainee.get("email", ""))
            phone = st.text_input("Phone number", value=st.session_state.trainee.get("phone", ""))
            role = st.selectbox(
                "Role *",
                ["", "NADI staff", "Admin", "Nurse", "Medical officer", "Research assistant", "Volunteer", "Other"],
                index=0,
            )
        with col2:
            organisation = st.text_input("Organisation", value=st.session_state.trainee.get("organisation", "NADI / MCMC"))
            centre = st.text_input("NADI centre / screening site *", value=st.session_state.trainee.get("centre", ""))
            state = st.selectbox(
                "State *",
                [
                    "",
                    "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang",
                    "Perak", "Perlis", "Pulau Pinang", "Sabah", "Sarawak", "Selangor",
                    "Terengganu", "WP Kuala Lumpur", "WP Labuan", "WP Putrajaya",
                ],
                index=0,
            )
            mode = st.selectbox("Venue / Mode", ["Online", "Hybrid", "Onsite"], index=0)
            cohort = st.text_input("Cohort", value=st.session_state.trainee.get("cohort", "1"))

        submitted = st.form_submit_button("Save trainee details", type="primary")

    if submitted:
        st.session_state.trainee = {
            "full_name": full_name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "role": role,
            "organisation": organisation.strip(),
            "centre": centre.strip(),
            "state": state,
            "mode": mode,
            "cohort": cohort.strip(),
        }
        if full_name and email and role and centre and state:
            mark_section_complete("Trainee details")
            celebrate_once("trainee_details", "Trainee details completed.")
            st.success("Trainee details saved.")
            celebration_banner("Trainee Details Completed", "Your profile has been saved. Continue to the 10 case scenario assessment.")
        else:
            st.warning("Please complete all required fields marked with *.")

    if st.session_state.trainee:
        st.markdown("### Saved trainee profile")
        st.dataframe(trainee_table(), use_container_width=True, hide_index=True)

    if st.session_state.section_completed.get("Trainee details"):
        go_next_button("Next: Start 10 Case Scenarios ➜", "3. Case Scenarios", "next_to_cases")
    else:
        st.info("Save complete trainee details first to unlock the next section.")


def case_card(case):
    st.markdown(f"## Case {case['case_no']}: {case['title']}")

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Participant demographics")
        demo_rows = [
            ["Name", case["name"]],
            ["IC", case["ic"]],
            ["DOB / Age", case["dob_age"]],
            ["Gender", case["gender"]],
            ["Race", case["race"]],
            ["Phone", case.get("phone", "")],
            ["Caregiver", case.get("caregiver", "-")],
            ["State / Centre", case["state_centre"]],
            ["Residential Area", case["residential_area"]],
            ["Occupation", case["occupation"]],
            ["Marital Status", case["marital_status"]],
            ["Education Level", case["education"]],
            ["Height / Weight", case["height_weight"]],
            ["Heart Attack History", case["heart_attack_history"]],
        ]
        st.dataframe(pd.DataFrame(demo_rows, columns=["Item", "Details"]), use_container_width=True, hide_index=True)

    with right:
        st.markdown("#### Risk inputs")
        input_rows = [[k, v] for k, v in case["inputs"].items()]
        st.dataframe(pd.DataFrame(input_rows, columns=["Input", "Value"]), use_container_width=True, hide_index=True)

        if case["heart_attack_history"].lower() == "yes":
            st.markdown('<div class="danger-box"><strong>Expected pathway:</strong> ACS pathway</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box"><strong>Expected pathway:</strong> FRS + REDISCOVER pathway</div>', unsafe_allow_html=True)

    st.markdown("#### Trainee assessment")
    ans_key = case["case_no"]
    prev = st.session_state.case_answers.get(ans_key, {})

    col1, col2, col3 = st.columns(3)
    with col1:
        completed = st.checkbox(
            f"I completed Case {case['case_no']} in MyHeartRisk",
            value=prev.get("completed", False),
            key=f"completed_{ans_key}",
        )
    with col2:
        pathway = st.selectbox(
            "Pathway selected",
            ["", "FRS + REDISCOVER", "ACS"],
            index=["", "FRS + REDISCOVER", "ACS"].index(prev.get("pathway", "")) if prev.get("pathway", "") in ["", "FRS + REDISCOVER", "ACS"] else 0,
            key=f"pathway_{ans_key}",
        )
    with col3:
        result_options = [""] + sorted({c["expected_result"] for c in CASES})
        result = st.selectbox(
            "System result obtained",
            result_options,
            index=result_options.index(prev.get("result", "")) if prev.get("result", "") in result_options else 0,
            key=f"result_{ans_key}",
        )

    action_options = [""] + [c["expected_action"] for c in CASES]
    action = st.selectbox(
        "NADI action selected",
        action_options,
        index=action_options.index(prev.get("action", "")) if prev.get("action", "") in action_options else 0,
        key=f"action_{ans_key}",
    )

    if st.button(f"Save Case {case['case_no']} answer", key=f"save_case_{ans_key}"):
        st.session_state.case_answers[ans_key] = {
            "completed": completed,
            "pathway": pathway,
            "result": result,
            "action": action,
        }
        if (
            completed
            and pathway == case["expected_pathway"]
            and result == case["expected_result"]
            and action == case["expected_action"]
        ):
            celebrate_once(f"case_{case['case_no']}_completed", f"Case {case['case_no']} completed correctly.")
            st.success("Correct. Case saved.")
            celebration_banner(
                f"Case {case['case_no']} Completed",
                "Pathway, result and NADI action match the expected answer."
            )
        else:
            st.error("Please recheck the expected pathway, result, or NADI action.")

    with st.expander("Show expected answer and teaching point"):
        st.write(f"**Expected pathway:** {case['expected_pathway']}")
        st.write(f"**Expected result:** {case['expected_result']}")
        st.write(f"**Expected action:** {case['expected_action']}")
        st.info(case["teaching_point"])


def page_cases():
    st.title("10 Case Scenario Assessment")

    st.markdown(
        """
        Complete all 10 dummy cases in the MyHeartRisk system, then record the pathway, result and NADI action here.
        """
    )

    case_correct, case_total = get_case_score()
    st.progress(case_correct / case_total)
    st.caption(f"Correct cases saved: {case_correct}/{case_total}")

    tabs = st.tabs([f"Case {c['case_no']}" for c in CASES])
    for tab, case in zip(tabs, CASES):
        with tab:
            case_card(case)

    st.divider()
    if case_correct == case_total:
        mark_section_complete("Case scenarios")
        celebrate_once("all_cases_complete", "All 10 case scenarios completed.")
        st.success("All 10 cases are completed correctly.")
        celebration_banner("10 Case Scenarios Completed", "You have completed all FRS + REDISCOVER and ACS scenario checks.")
        go_next_button("Next: Complete Knowledge Check ➜", "4. Knowledge Check", "next_to_knowledge")
    else:
        st.warning("Please complete and save all 10 cases correctly before certification.")
        st.button("Next: Complete Knowledge Check ➜", disabled=True, key="next_to_knowledge_disabled")


def page_knowledge():
    st.title("Knowledge Check")

    st.markdown(
        f"""
        Answer all questions. Passing mark is **{PASS_MARK}%**.
        """
    )

    for i, q in enumerate(KNOWLEDGE_QUESTIONS):
        st.markdown(f"### Q{i+1}. {q['question']}")
        current = st.session_state.knowledge_answers.get(i)
        option_index = q["options"].index(current) if current in q["options"] else None

        selected = st.radio(
            "Choose one answer",
            q["options"],
            index=option_index,
            key=f"knowledge_{i}",
        )
        st.session_state.knowledge_answers[i] = selected

        with st.expander("Show explanation after answering"):
            if selected == q["answer"]:
                st.success(f"Correct. {q['explanation']}")
            else:
                st.error(f"Correct answer: {q['answer']}. {q['explanation']}")

    correct, total, percent = get_knowledge_score()
    st.divider()
    st.metric("Knowledge score", f"{percent}% ({correct}/{total})")

    if percent >= PASS_MARK:
        mark_section_complete("Knowledge check")
        celebrate_once("knowledge_passed", "Knowledge check passed.")
        st.success("Knowledge check passed.")
        celebration_banner("Knowledge Check Passed", f"Your score is {percent}%. You may proceed to the Google Form completion record.")
        go_next_button("Next: Submit Google Form Record ➜", "5. Google Form", "next_to_google_form")
    else:
        st.error("Knowledge check not yet passed. Please review the answers.")
        st.button("Next: Submit Google Form Record ➜", disabled=True, key="next_to_google_form_disabled")


def page_google_form():
    st.title("Google Form Completion Record")

    st.markdown(
        """
        After completing the case scenarios and knowledge check, submit the official Google Form completion record.
        Replace the Google Form link in the source code with your actual form link.
        """
    )

    st.link_button("Open Google Form", GOOGLE_FORM_URL)

    st.divider()

    st.session_state.google_form_submitted = st.checkbox(
        "I confirm that I have submitted the Google Form completion record.",
        value=st.session_state.google_form_submitted,
    )

    st.session_state.declaration_agreed = st.checkbox(
        "I declare that I completed the 10 cases myself and will follow the MyHeartRisk SOP, including not guessing unknown answers.",
        value=st.session_state.declaration_agreed,
    )

    if st.session_state.google_form_submitted and st.session_state.declaration_agreed:
        mark_section_complete("Google form")
        celebrate_once("google_form_completed", "Google Form and declaration completed.")
        celebration_banner("Google Form Record Completed", "Your completion declaration is recorded. You may proceed to certificate verification.")

    record = build_completion_record()
    st.download_button(
        "Download completion evidence JSON",
        data=json.dumps(record, indent=2),
        file_name=f"myheartrisk_completion_evidence_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
    )

    if st.session_state.section_completed.get("Google form"):
        go_next_button("Next: View Certificate ➜", "6. Certificate", "next_to_certificate")
    else:
        st.button("Next: View Certificate ➜", disabled=True, key="next_to_certificate_disabled")


def page_certificate():
    st.title("Certificate of Completion")

    if st.session_state.trainee.get("full_name") and st.session_state.trainee.get("email"):
        st.session_state.certificate_id = get_certificate_id(
            st.session_state.trainee.get("full_name", ""),
            st.session_state.trainee.get("email", ""),
        )

    case_correct, case_total = get_case_score()
    knowledge_correct, knowledge_total, knowledge_percent = get_knowledge_score()

    status_rows = [
        ["Trainee details completed", "Yes" if st.session_state.trainee.get("full_name") and st.session_state.trainee.get("email") else "No"],
        ["All 10 cases correct", f"{case_correct}/{case_total}"],
        ["Knowledge check", f"{knowledge_percent}%"],
        ["Google Form submitted", "Yes" if st.session_state.google_form_submitted else "No"],
        ["Declaration agreed", "Yes" if st.session_state.declaration_agreed else "No"],
    ]
    st.dataframe(pd.DataFrame(status_rows, columns=["Requirement", "Status"]), use_container_width=True, hide_index=True)

    if is_eligible():
        mark_section_complete("Certificate")
        celebrate_once("certificate_unlocked", "Certificate unlocked. Congratulations!")
        st.success("Congratulations. Certificate is unlocked.")
        celebration_banner("Certificate Unlocked", "The trainee has completed all requirements and is now eligible for the certificate.")

        html = certificate_html()
        st.markdown(html, unsafe_allow_html=True)

        st.download_button(
            "Download certificate HTML",
            data=html,
            file_name=f"MyHeartRisk_Certificate_{st.session_state.certificate_id}.html",
            mime="text/html",
        )

        pdf_bytes = generate_certificate_pdf()
        if pdf_bytes:
            st.download_button(
                "Download certificate PDF",
                data=pdf_bytes,
                file_name=f"MyHeartRisk_Certificate_{st.session_state.certificate_id}.pdf",
                mime="application/pdf",
            )
        else:
            st.info("PDF generation requires fpdf2. Install using: pip install fpdf2")

        st.markdown(
            """
            <div class="success-box">
            The user is now certified as a MyHeartRisk NADI Screener.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Certificate is locked. Please complete all requirements first.")


# -----------------------------
# MAIN
# -----------------------------
def main():
    inject_css()
    init_state()
    sidebar()

    if st.session_state.current_step == "1. Training":
        page_training()
    elif st.session_state.current_step == "2. Trainee Details":
        page_trainee_details()
    elif st.session_state.current_step == "3. Case Scenarios":
        page_cases()
    elif st.session_state.current_step == "4. Knowledge Check":
        page_knowledge()
    elif st.session_state.current_step == "5. Google Form":
        page_google_form()
    elif st.session_state.current_step == "6. Certificate":
        page_certificate()


if __name__ == "__main__":
    main()
