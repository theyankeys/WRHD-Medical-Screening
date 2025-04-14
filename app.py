import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
import time

# Department mapping
departments = {
    "Public Health": "PH",
    "Port Health and Aviation": "PO",
    "Reference Lab": "RL",
    "Office of RDHS": "RD",
    "Clinical Care Department": "CC",
    "HASS & Finance": "HF",
    "Human Resource": "HR",
    "Regional Medical Stores": "RM"
}

# Initialize session state
if 'records' not in st.session_state:
    st.session_state['records'] = []
if 'reset_form' not in st.session_state:
    st.session_state['reset_form'] = False
if 'show_unique_code' not in st.session_state:
    st.session_state.show_unique_code = False
if 'unique_code_time' not in st.session_state:
    st.session_state.unique_code_time = None

# Data file path
DATA_FILE = "medical_records.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=['DOB'])
            st.session_state['records'] = df.to_dict('records')
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.session_state['records'] = []

def save_data():
    try:
        df = pd.DataFrame(st.session_state['records'])
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Failed to save data: {str(e)}")
        return False

load_data()

def calculate_bmi(weight, height):
    if height > 0:
        bmi = weight / (height ** 2)
        if bmi < 18.5:
            classification = "Underweight"
        elif 18.5 <= bmi < 24.9:
            classification = "Normal weight"
        elif 25 <= bmi < 29.9:
            classification = "Overweight"
        else:
            classification = "Obesity"
        return round(bmi, 2), classification
    return None, None

def calculate_age(dob):
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def generate_unique_id(first_name, last_name, department_code):
    department_code = departments.get(department_code, "NA")
    unique_id = f"{first_name[0].upper()}{last_name[0].upper()}{department_code}{str(len(st.session_state['records'])+1).zfill(4)}"
    return unique_id

# Sidebar navigation
st.sidebar.title("WRHD Medical Screening Tool")
section = st.sidebar.radio("Select Section", [
    "General Information", 
    "Blood Pressure", 
    "Blood Glucose", 
    "BMI", 
    "Visual Acuity", 
    "General Assessment",
    "Data Export"
])

# ========================
# GENERAL INFORMATION SECTION
# ========================
if section == "General Information":
    st.title("General Information")
    
    # Display unique code if it's been less than 5 minutes since generation
    if st.session_state.show_unique_code and st.session_state.unique_code_time:
        elapsed = (datetime.now() - st.session_state.unique_code_time).seconds / 60
        if elapsed < 5:  # Show for 5 minutes
            st.success(f"Registered Patient Code: {st.session_state.last_unique_code}")
        else:
            st.session_state.show_unique_code = False
    
    if st.button("🆕 New Registration"):
        st.session_state.reset_form = True
        st.session_state.show_unique_code = False
        st.rerun()
    
    with st.form(key='general_info_form'):
        # Reset form if requested
        default_values = {
            'first_name': '',
            'middle_name': '',
            'last_name': '',
            'dob': None,
            'sex': '',
            'department': '',
            'job_title': '',
            'email': '',
            'phone': ''
        } if st.session_state['reset_form'] else {
            'first_name': '',
            'middle_name': '',
            'last_name': '',
            'dob': None,
            'sex': '',
            'department': '',
            'job_title': '',
            'email': '',
            'phone': ''
        }
        st.session_state['reset_form'] = False
        
        # Name fields in 3 columns
        col1, col2, col3 = st.columns(3)
        with col1:
            first_name = st.text_input("First Name*", value=default_values['first_name'])
        with col2:
            middle_name = st.text_input("Middle Name", value=default_values['middle_name'])
        with col3:
            last_name = st.text_input("Last Name*", value=default_values['last_name'])
        
        # Other fields in 2 columns
        col_a, col_b = st.columns(2)
        with col_a:
            dob = st.date_input("Date of Birth*", 
                              value=default_values['dob'],
                              max_value=datetime.today())
            sex = st.selectbox("Sex*", ["", "Male", "Female", "Other"])
            job_title = st.text_input("Job Title", value=default_values['job_title'])
        
        with col_b:
            department = st.selectbox("Department*", [""] + list(departments.keys()))
            email = st.text_input("Email", value=default_values['email'])
            phone_number = st.text_input("Phone Number", value=default_values['phone'])
        
        # Calculate age
        age = calculate_age(dob) if dob else None
        if age:
            st.write(f"**Age:** {age}")
        
        # Save button
        if st.form_submit_button("💾 Save Record", type="primary"):
            if all([first_name, last_name, dob, sex, department]):
                unique_code = generate_unique_id(first_name, last_name, department)
                st.session_state.last_unique_code = unique_code
                st.session_state.show_unique_code = True
                st.session_state.unique_code_time = datetime.now()
                try:
                    unique_code = generate_unique_id(first_name, last_name, department)
                    new_record = {
                        'First Name': first_name.strip(),
                        'Middle Name': middle_name.strip(),
                        'Last Name': last_name.strip(),
                        'DOB': dob,
                        'Age': age,
                        'Sex': sex,
                        'Department': department,
                        'Job Title': job_title.strip(),
                        'Email': email.strip(),
                        'Phone Number': phone_number.strip(),
                        'Unique Code': unique_code,
                        'Registration Date': datetime.today().strftime('%Y-%m-%d')
                    }
                    st.session_state['records'].append(new_record)
                    if save_data():
                        st.success(f"✅ Patient registered successfully! Unique Code: {unique_code}")
                        st.session_state['reset_form'] = True
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("⚠️ Please fill all required fields (*)")

# ========================
# BLOOD PRESSURE SECTION
# ========================
elif section == "Blood Pressure":
    st.title("Blood Pressure")
    search_term = st.text_input("🔍 Search by Name or Unique Code")
    
    if search_term:
        matches = [
            r for r in st.session_state['records']
            if (search_term.lower() in f"{r.get('First Name', '')} {r.get('Last Name', '')}".lower() 
                or search_term.lower() in str(r.get('Unique Code', '')).lower())
        ]
        
        if matches:
            record = matches[0]
            st.write(f"Unique Code: {record['Unique Code']}")
            
            st.subheader(f"Patient: {record['First Name']} {record['Last Name']}")
            st.write(f"**Unique Code:** {record['Unique Code']} | **Age:** {record.get('Age', 'N/A')}")
            
            with st.form("bp_form"):
                col1, col2 = st.columns(2)
                with col1:
                    systolic = st.number_input("Systolic (mmHg)",  
                                             value=0,
                                             step=1)
                with col2:
                    diastolic = st.number_input("Diastolic (mmHg)", 
                                              value=0,
                                              step=1)
                
                bp_notes = st.text_area("Clinical Notes")
                
                if st.form_submit_button("💾 Save Blood Pressure"):
                    record['Blood Pressure'] = f"{systolic}/{diastolic}"
                    record['BP Date'] = datetime.today().strftime('%Y-%m-%d')
                    record['BP Notes'] = bp_notes
                    if save_data():
                        st.success(f"✅ Blood pressure saved: {systolic}/{diastolic} mmHg")
                    else:
                        st.error("❌ Failed to save blood pressure data")
        else:
            st.warning("⚠️ No matching patients found")
    else:
        st.info("ℹ️ Please enter a patient name or unique code to search")

# ========================
# GENERAL ASSESSMENT SECTION
# ========================
elif section == "General Assessment":
    st.title("Comprehensive Patient Assessment")
    search_term = st.text_input("🔍 Search by Name or Unique Code")
    
    if search_term:
        search_term = str(search_term).lower()
        matches = [
            r for r in st.session_state['records']
            if (search_term in f"{r.get('First Name', '')} {r.get('Last Name', '')}".lower() 
                or search_term in str(r.get('Unique Code', '')).lower())
        ]
        
        if matches:
            if len(matches) > 1:
                selected = st.selectbox("Select patient", 
                                      [f"{m['First Name']} {m['Last Name']} ({m['Unique Code']})" 
                                       for m in matches])
                record = matches[[f"{m['First Name']} {m['Last Name']} ({m['Unique Code']})" 
                                for m in matches].index(selected)]
            else:
                record = matches[0]
            
            st.subheader(f"Patient: {record['First Name']} {record['Last Name']}")
            st.write(f"**Unique Code:** {record['Unique Code']} | **Age:** {record.get('Age', 'N/A')}")
            
            # Display all data in expandable table
            with st.expander("📋 View Complete Patient Record", expanded=True):
                # Filter out empty values
                display_data = {k: v for k, v in record.items() if v not in [None, ""]}
                st.table(pd.DataFrame.from_dict(display_data, orient='index', columns=['Value']))
            
            # Risk assessment
            risk_factors = []
            if 'Blood Pressure' in record:
                try:
                    systolic, diastolic = map(int, record['Blood Pressure'].split('/'))
                    if systolic > 140 or diastolic > 90:
                        risk_factors.append("Hypertension")
                except:
                    pass
            
            if 'BMI' in record and record['BMI'] > 30:
                risk_factors.append("Obesity")
            
            if risk_factors:
                st.warning(f"🚨 Risk Factors Detected: {', '.join(risk_factors)}")
            
            # Assessment form
            with st.form("assessment_form"):
                clinical_notes = st.text_area("Clinical Assessment Notes",
                                            value=record.get('Clinical Notes', ''))
                
                referred = st.checkbox("Refer to specialist",
                                     value=record.get('Referred', False))
                
                if referred:
                    referral_details = st.text_input("Referral details",
                                                    value=record.get('Referral Details', ''))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Assessment"):
                        record['Clinical Notes'] = clinical_notes
                        if save_data():
                            st.success("✅ Assessment saved successfully!")
                with col2:
                    if st.form_submit_button("🚑 Refer Patient"):
                        record['Referred'] = True
                        record['Referral Date'] = datetime.today().strftime('%Y-%m-%d')
                        record['Referral Details'] = referral_details if referred else ''
                        if save_data():
                            st.success("✅ Patient referred successfully!")
                            st.balloons()
        else:
            st.warning("⚠️ No matching patients found")
    else:
        st.info("ℹ️ Please enter a patient name or unique code to search")

# ========================
# BMI SECTION
# ========================
elif section == "BMI":
    st.title("BMI Calculation")
    search_term = st.text_input("🔍 Search by Name or Unique Code")
    
    if search_term:
        search_term = str(search_term).lower()
        matches = [
            r for r in st.session_state['records']
            if (search_term in f"{r.get('First Name', '')} {r.get('Last Name', '')}".lower() 
                or search_term in str(r.get('Unique Code', '')).lower())
        ]
        
        if matches:
            if len(matches) > 1:
                selected = st.selectbox("Select patient", 
                                      [f"{m['First Name']} {m['Last Name']} ({m['Unique Code']})" 
                                       for m in matches])
                record = matches[[f"{m['First Name']} {m['Last Name']} ({m['Unique Code']})" 
                                for m in matches].index(selected)]
            else:
                record = matches[0]
            
            st.subheader(f"Patient: {record['First Name']} {record['Last Name']}")
            st.write(f"**Unique Code:** {record['Unique Code']} | **Age:** {record.get('Age', 'N/A')}")
            
            with st.form("bmi_form"):
                col1, col2 = st.columns(2)
                with col1:
                    weight = st.number_input("Weight (kg)", 
                                           min_value=0.0, 
                                           max_value=300.0, 
                                           value=0.0,
                                           step=0.1)
                with col2:
                    height = st.number_input("Height (m)", 
                                            min_value=0.0, 
                                            max_value=3.5, 
                                            value=0.0,
                                            step=0.01)
                
                if weight > 0 and height > 0:
                    bmi, classification = calculate_bmi(weight, height)
                    st.metric("BMI", f"{bmi} ({classification})")
                
                if st.form_submit_button("💾 Save BMI"):
                    record['Weight'] = weight
                    record['Height'] = height
                    record['BMI'] = bmi
                    record['BMI Classification'] = classification
                    record['BMI Date'] = datetime.today().strftime('%Y-%m-%d')
                    if save_data():
                        st.success(f"✅ BMI {bmi} ({classification}) saved successfully!")
                    else:
                        st.error("❌ Failed to save BMI data")
        else:
            st.warning("⚠️ No matching patients found")
    else:
        st.info("ℹ️ Please enter a patient name or unique code to search")

# ========================
# VISUAL ACUITY SECTION
# ========================
elif section == "Visual Acuity":
    st.title("Visual Acuity")
    search_term = st.text_input("🔍 Search by Name or Unique Code")
    
    if search_term:
        search_term = str(search_term).lower()
        matches = [
            r for r in st.session_state['records']
            if (search_term in f"{r.get('First Name', '')} {r.get('Last Name', '')}".lower() 
                or search_term in str(r.get('Unique Code', '')).lower())
        ]
        
        if matches:
            if len(matches) > 1:
                selected = st.selectbox("Select patient", 
                                      [f"{m['First Name']} {m['Last Name']} ({m['Unique Code']})" 
                                       for m in matches])
                record = matches[[f"{m['First Name']} {m['Last Name']} ({m['Unique Code']})" 
                                for m in matches].index(selected)]
            else:
                record = matches[0]
            
            st.subheader(f"Patient: {record['First Name']} {record['Last Name']}")
            st.write(f"**Unique Code:** {record['Unique Code']} | **Age:** {record.get('Age', 'N/A')}")
            
            with st.form("vision_form"):
                col1, col2 = st.columns(2)
                with col1:
                    right_eye = st.text_input("Right Eye (e.g., 6/6)",
                                             value=record.get('Visual Acuity Right', ''))
                with col2:
                    left_eye = st.text_input("Left Eye (e.g., 6/6)",
                                            value=record.get('Visual Acuity Left', ''))
                
                with_glasses = st.checkbox("Tested with glasses/contacts",
                                         value=record.get('With Glasses', False))
                
                if st.form_submit_button("💾 Save Visual Acuity"):
                    record['Visual Acuity Right'] = right_eye
                    record['Visual Acuity Left'] = left_eye
                    record['Vision Test Date'] = datetime.today().strftime('%Y-%m-%d')
                    record['With Glasses'] = with_glasses
                    if save_data():
                        st.success("✅ Visual acuity saved successfully!")
                    else:
                        st.error("❌ Failed to save visual acuity data")
        else:
            st.warning("⚠️ No matching patients found")
    else:
        st.info("ℹ️ Please enter a patient name or unique code to search")

# ========================
# BLOOD GLUCOSE SECTION
# ========================
elif section == "Blood Glucose":
    st.title("Blood Glucose")
    search_term = st.text_input("🔍 Search by Name or Unique Code")
    
    if search_term:
        search_term = str(search_term).lower()
        matches = [
            r for r in st.session_state['records']
            if (search_term in f"{r.get('First Name', '')} {r.get('Last Name', '')}".lower() 
                or search_term in str(r.get('Unique Code', '')).lower())
        ]
        if matches:
            if len(matches) > 1:
                selected = st.selectbox("Select patient", 
                                      [f"{m['First Name']} {m['Last Name']} ({m['Unique Code']})" 
                                       for m in matches])
                record = matches[[f"{m['First Name']} {m['Last Name']} ({m['Unique Code']})" 
                                for m in matches].index(selected)]
            else:
                record = matches[0]
            
            st.subheader(f"Patient: {record['First Name']} {record['Last Name']}")
            st.write(f"**Unique Code:** {record['Unique Code']} | **Age:** {record.get('Age', 'N/A')}")
            
            with st.form("glucose_form"):
                glucose = st.number_input("Blood Glucose (mg/dL)", 
                                        value=0.0,
                                        step=0.1,
                                        format="%.1f")
                
                fasting = st.radio("Fasting Status",
                                  ["Fasting", "Non-fasting"],
                                  index=0 if record.get('Fasting Status') == "Fasting" else 1)
                
                if st.form_submit_button("💾 Save Glucose Reading"):
                    record['Blood Glucose'] = glucose
                    record['Glucose Date'] = datetime.today().strftime('%Y-%m-%d')
                    record['Fasting Status'] = fasting
                    if save_data():
                        st.success(f"✅ Glucose level {glucose} mg/dL ({fasting}) saved!")
                    else:
                        st.error("❌ Failed to save glucose data")
        else:
            st.warning("⚠️ No matching patients found")
    else:
        st.info("ℹ️ Please enter a patient name or unique code to search")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function: Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0

if "last_attempt_time" not in st.session_state:
    st.session_state["last_attempt_time"] = None
    
# ========================
# DATA EXPORT SECTION
# ========================
elif section == "Data Export":
    st.title("Data Management")

    # Authentication
    st.subheader("Login Required")

    # Define user credentials (hashed passwords)
    credentials = {"wrhd_ms": hash_password("@#Bluebird95")}  # Example credentials

    if not st.session_state["authenticated"]:
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")

    # Rate limiting: Check attempts
    if st.session_state["login_attempts"] >= 3:
        cooldown_time = 60  # 60 seconds cooldown
        if st.session_state["last_attempt_time"] and time.time() - st.session_state["last_attempt_time"] < cooldown_time:
            st.error("Too many failed attempts. Please wait before retrying.")
            st.stop()
        else:
            st.session_state["login_attempts"] = 0

    if st.button("🔒 Login"):
        hashed_input_password = hash_password(password)

        if username in credentials and credentials[username] == hashed_input_password:
            st.session_state["authenticated"] = True
            st.success("✅ Login successful!")
        else:
            st.session_state["login_attempts"] += 1
            st.session_state["last_attempt_time"] = time.time()
            st.error("❌ Invalid username or password")

if st.session_state["authenticated"]:  # Corrected alignment
    st.success("You are authenticated!")

    # Logout button
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["password"] = ""
        st.info("Logged out successfully!")
        st.stop()

    if st.session_state['records']:
        st.success(f"ℹ️ Found {len(st.session_state['records'])} patient records")

        # Show sample data
        st.subheader("Sample Data")
        st.dataframe(pd.DataFrame(st.session_state['records']).head())

        # Export options
        st.subheader("Export Data")
        csv = pd.DataFrame(st.session_state['records']).to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="medical_records.csv",
            mime="text/csv"
        )

        if st.button("🔄 Refresh Data"):
            load_data()
            st.rerun()
    else:
        st.warning("⚠️ No patient records found")
