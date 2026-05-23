import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import fitz
import requests

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Smart Personal Finance Management System",
    layout="wide"
)

# =========================================================
# SESSION STATES
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "registered" not in st.session_state:
    st.session_state.registered = False

if "saved_username" not in st.session_state:
    st.session_state.saved_username = ""

if "saved_password" not in st.session_state:
    st.session_state.saved_password = ""

# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown("""
    <style>

    .stApp{
        background: linear-gradient(
            135deg,
            #1E3C72,
            #2A5298,
            #4A90E2
        );
    }

    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}

    /* TITLE */

    .title{
        text-align:center;
        font-size:54px;
        font-weight:800;
        color:white;
        margin-top:30px;
        margin-bottom:10px;
    }

    .subtitle{
        text-align:center;
        color:#EAEAEA;
        font-size:22px;
        margin-bottom:45px;
    }

    /* CREATE ACCOUNT / LOGIN HEADINGS */

    h3{
        color:white !important;
        font-size:36px !important;
        font-weight:800 !important;
        margin-bottom:25px !important;
    }

    /* LABELS */

    label{
        color:white !important;
        font-size:24px !important;
        font-weight:700 !important;
    }

    /* INPUT BOXES */

    .stTextInput input{
        background-color:white !important;
        color:black !important;
        font-size:20px !important;
        border-radius:12px !important;
        padding:16px !important;
        border:none !important;
    }

    /* BUTTON */

    .stButton button{
        background: linear-gradient(
            90deg,
            #2196F3,
            #64B5F6
        ) !important;

        color:white !important;
        font-size:20px !important;
        font-weight:700 !important;

        border:none !important;
        border-radius:12px !important;

        width:100% !important;
        height:55px !important;
    }

    .stButton button:hover{
        transform:scale(1.01);
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='title'>Smart Personal Finance Management System</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>AI-Driven Expense Analysis & Prediction</div>",
        unsafe_allow_html=True
    )

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        # =====================================================
        # SIGN UP
        # =====================================================

        if not st.session_state.registered:

            st.subheader("Create Account")

            new_user = st.text_input("Create Username")

            new_pass = st.text_input(
                "Create Password",
                type="password"
            )

            signup = st.button("Sign Up")

            if signup:

                if new_user and new_pass:

                    st.session_state.saved_username = new_user
                    st.session_state.saved_password = new_pass
                    st.session_state.registered = True

                    st.success("Account Created Successfully")

                    st.rerun()

                else:
                    st.error("Please fill all fields")

        # =====================================================
        # LOGIN
        # =====================================================

        else:

            st.subheader("Login")

            username = st.text_input("Username")

            password = st.text_input(
                "Password",
                type="password"
            )

            login_btn = st.button("Login")

            if login_btn:

                if (
                    username == st.session_state.saved_username
                    and
                    password == st.session_state.saved_password
                ):

                    st.session_state.logged_in = True

                    st.success("Login Successful")

                    st.rerun()

                else:
                    st.error("Invalid Username or Password")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# =========================================================
# DASHBOARD STYLE
# =========================================================

st.markdown("""
<style>

.title-dashboard{
    font-size:42px;
    font-weight:800;
    text-align:center;
    margin-bottom:25px;
}

.section{
    font-size:28px;
    font-weight:700;
    margin-top:25px;
    margin-bottom:15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_text(pdf):

    text = ""

    pdf.seek(0)

    doc = fitz.open(stream=pdf.read(), filetype="pdf")

    for page in doc:
        text += page.get_text()

    doc.close()

    return text

# =========================================================
# PARSE TRANSACTIONS
# =========================================================

def parse_transactions(text):

    lines = text.split("\\n")

    data = []

    merchant = None
    date = None

    for line in lines:

        line = line.strip()

        date_match = re.search(
            r"\\d{1,2}\\s\\w{3},?\\s\\d{4}",
            line
        )

        if date_match:
            date = date_match.group()

        if "Paid to" in line:
            merchant = line.split("Paid to")[-1].strip()

        amount = re.search(
            r"₹[\\d,]+\\.?\\d*",
            line
        )

        if amount and merchant:

            amt = float(
                amount.group()
                .replace("₹","")
                .replace(",","")
            )

            data.append({
                "date": date,
                "merchant": merchant,
                "amount": amt,
                "type": "debit"
            })

            merchant = None

    return pd.DataFrame(data)

# =========================================================
# CATEGORY CLASSIFIER
# =========================================================

def classify(merchant):

    m = merchant.lower()

    if "swiggy" in m or "zomato" in m:
        return "Food"

    if "amazon" in m or "flipkart" in m:
        return "Shopping"

    if "mart" in m or "store" in m:
        return "Groceries"

    if "petrol" in m or "fuel" in m:
        return "Fuel"

    if "medical" in m:
        return "Healthcare"

    if "uber" in m or "ola" in m:
        return "Transport"

    if "recharge" in m:
        return "Recharge"

    return "Others"

# =========================================================
# PIE CHART
# =========================================================

def pie_chart(category_totals):

    fig, ax = plt.subplots(figsize=(4,4))

    total = category_totals.sum()

    percent = (
        category_totals / total * 100
    ).round(1)

    labels = [
        f"{c} ({percent[c]}%)"
        for c in category_totals.index
    ]

    wedges,_ = ax.pie(
        category_totals,
        startangle=90
    )

    ax.axis("equal")

    ax.set_title("Expense Distribution")

    ax.legend(
        wedges,
        labels,
        loc="center left",
        bbox_to_anchor=(-0.6,0.5)
    )

    st.pyplot(fig)

# =========================================================
# BAR CHART
# =========================================================

def bar_chart(category_totals):

    fig, ax = plt.subplots(figsize=(4,4))

    category_totals.plot(
        kind="barh",
        ax=ax
    )

    ax.set_title("Category Spending")

    st.pyplot(fig)

# =========================================================
# MONTHLY TREND
# =========================================================

def monthly_chart(df):

    df["parsed_date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    monthly = df.groupby(
        df["parsed_date"].dt.to_period("M")
    )["amount"].sum()

    monthly.index = monthly.index.astype(str)

    fig, ax = plt.subplots(figsize=(4,4))

    monthly.plot(marker="o", ax=ax)

    ax.set_title("Monthly Trend")

    st.pyplot(fig)

# =========================================================
# DASHBOARD TITLE
# =========================================================

st.markdown(
    "<div class='title-dashboard'>AI Personal Finance Dashboard</div>",
    unsafe_allow_html=True
)

income = st.number_input(
    "Monthly Income ₹",
    value=0
)

budget = st.number_input(
    "Monthly Budget ₹",
    value=0
)

mode = st.radio(
    "Select Input Method",
    ["Upload Transaction File","Manual Entry"]
)

df = None

# =========================================================
# PDF MODE
# =========================================================

if mode == "Upload Transaction File":

    file = st.file_uploader(
        "Upload transaction PDF",
        type=["pdf"]
    )

    analyze = st.button("Analyze")

    if file and analyze:

        text = extract_text(file)

        df = parse_transactions(text)

        if not df.empty:
            df["Category"] = df["merchant"].apply(classify)

# =========================================================
# MANUAL ENTRY MODE
# =========================================================

elif mode == "Manual Entry":

    st.subheader("Enter Expenses")

    if "manual_data" not in st.session_state:
        st.session_state.manual_data = []

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Shopping",
            "Groceries",
            "Transport",
            "Recharge",
            "Healthcare",
            "Fuel",
            "Others"
        ]
    )

    amount = st.number_input(
        "Amount",
        min_value=1
    )

    if st.button("Add Expense"):

        st.session_state.manual_data.append({
            "Category": category,
            "amount": amount
        })

    if st.session_state.manual_data:

        delete_index = None

        for i,row in enumerate(
            st.session_state.manual_data
        ):

            col1,col2,col3 = st.columns([4,4,1])

            col1.write(row["Category"])

            col2.write(f"₹{row['amount']}")

            if col3.button("❌", key=i):
                delete_index = i

        if delete_index is not None:

            st.session_state.manual_data.pop(
                delete_index
            )

            st.rerun()

        df = pd.DataFrame(
            st.session_state.manual_data
        )

# =========================================================
# PROCESS DATA
# =========================================================

if df is not None and not df.empty:

    total_expense = df["amount"].sum()

    savings = income - total_expense

    risk = (
        "High"
        if total_expense > budget
        else "Low"
    )

    st.markdown(
        "<div class='section'>Current Financial Analysis</div>",
        unsafe_allow_html=True
    )

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Total Expense",
        f"₹{total_expense:,.0f}"
    )

    c2.metric(
        "Savings",
        f"₹{savings:,.0f}"
    )

    c3.metric(
        "Risk Level",
        risk
    )

    # =====================================================
    # NEXT MONTH PREDICTION
    # =====================================================

    st.markdown(
        "<div class='section'>Next Month Prediction</div>",
        unsafe_allow_html=True
    )

    category_totals = df.groupby(
        "Category"
    )["amount"].sum()

    try:

        r = requests.post(
            "http://127.0.0.1:5000/predict",
            json={
                "total_expense": float(total_expense),
                "income": float(income),
                "budget": float(budget)
            }
        )

        predicted = r.json()[
            "predicted_expense"
        ]

        st.metric(
            "Predicted Next Month Expense",
            f"₹{predicted:,.0f}"
        )

    except:

        st.warning(
            "Prediction server not running"
        )

    # =====================================================
    # ANALYTICS DASHBOARD
    # =====================================================

    st.markdown(
        "<div class='section'>Analytics Dashboard</div>",
        unsafe_allow_html=True
    )

    col1,col2,col3 = st.columns(3)

    with col1:
        pie_chart(category_totals)

    with col2:
        bar_chart(category_totals)

    if mode == "Upload Transaction File":

        with col3:
            monthly_chart(df)

    # =====================================================
    # FINANCIAL ADVICE
    # =====================================================

    st.markdown(
        "<div class='section'>Financial Advice</div>",
        unsafe_allow_html=True
    )

    if risk == "High":
        st.error(
            "⚠ Spending exceeds your budget"
        )

    else:
        st.success(
            "✅ Spending under control"
        )

    st.write(
        f"Estimated Savings: ₹{savings:,.0f}"
    )