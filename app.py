import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="CEO Trading Journal", layout="wide")

if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

# ----------------- Account Selection -----------------
st.sidebar.header("📁 Journal Selection")

journal_account = st.sidebar.selectbox("Select Account", [
    "50Cr Prop Firm Account",
    "GBPCAD Test",
    "GBPNZD Test" 
])

if journal_account == "50Cr Prop Firm Account":
    DATA_FILE = "trades_50cr.csv"
elif journal_account == "GBPCAD Test":
    DATA_FILE = "trades_gbpcad_test.csv"
elif journal_account == "GBPNZD Test":
    DATA_FILE = "trades_gbpnzd_test.csv"

def load_data(file_name):
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        df['Date'] = pd.to_datetime(df['Date']) 
        
        # Pazhaya data disturb aavathe puthiya columns add cheyyunnu
        for i in range(2, 8):
            col_name = f"Screenshot_{i}"
            if col_name not in df.columns:
                df[col_name] = ""
        return df
    else:
        return pd.DataFrame(columns=[
            "Date", "Pair", "Direction", "Session", "News_Category", 
            "Weekly_Bias", "Daily_Bias", "Liquidity_Swept", "Setup_Trigger", "Setup_Grade", "Trade_Thesis",
            "Entry_Price", "Exit_Price", "PnL", "Outcome", "Psychology", 
            "Screenshot_Path", "Screenshot_2", "Screenshot_3", "Screenshot_4", "Screenshot_5", "Screenshot_6", "Screenshot_7"
        ])

df = load_data(DATA_FILE)

st.title(f"📈 CEO Dashboard: {journal_account}")

# ----------------- Add New Trade -----------------
st.sidebar.header("📝 Add New Trade")

with st.sidebar.expander("📌 1. Basic Trade Info", expanded=True):
    trade_date = st.date_input("Trade Date")
    pair = st.text_input("Pair (e.g., GBPUSD, GBPCAD)")
    direction = st.selectbox("Direction", ["Long", "Short"])
    session = st.selectbox("Session", ["Asian", "London", "New York", "Frankfurt"])
    news_category = st.selectbox("News Category", ["None", "CPI / Inflation", "NFP / Employment", "FOMC", "High Impact"])

with st.sidebar.expander("🧠 2. CEO SMC Logic (Context)", expanded=True):
    weekly_bias = st.selectbox("Weekly Bias", ["Bullish", "Bearish", "Neutral / Ranging"])
    daily_bias = st.selectbox("Daily Bias", ["Bullish", "Bearish", "Neutral / Ranging"])
    liquidity_swept = st.selectbox("Liquidity Swept", ["Previous Day High / Low", "Previous Week High / Low", "Asian Session High / Low", "Trendline / Structural Liquidity", "None"])
    setup_trigger = st.selectbox("Setup Trigger", ["Sweep + 4H Zone + SMT", "Continuation / Trend Follow", "SMT at Key Level", "Other"])
    setup_grade = st.radio("Setup Grade", ["A+ Setup (All Timeframes Aligned)", "A Setup (Dynamic Liquidity + 4H Zone)", "B Setup (Lower TF Confluence Only)"])
    trade_thesis = st.text_area("Trade Thesis (Your Logic)")

with st.sidebar.expander("💰 3. Trade Results & Psychology", expanded=True):
    entry_price = st.number_input("Entry Price", format="%.5f")
    exit_price = st.number_input("Exit Price", format="%.5f")
    pnl = st.number_input("Profit / Loss ($)", format="%.2f")
    outcome = st.selectbox("Trade Outcome", ["Hit TP (1:2)", "Hit SL", "Breakeven", "Manual Close"])
    psychology = st.selectbox("Trade Psychology", ["Followed Perfect Plan", "FOMO Entry (Avasarappatten)", "Revenge Trade", "Closed Early (Payanthutten)", "Hesitated / Late Entry"])

with st.sidebar.expander("🖼️ 4. Chart Screenshots (Up to 7)", expanded=True):
    uploaded_images = st.file_uploader("Upload Screenshots", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if st.sidebar.button("💾 Save Trade", use_container_width=True):
    if pair:
        img_paths = ["", "", "", "", "", "", ""]
        if uploaded_images:
            for i, img in enumerate(uploaded_images[:7]):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                image_name = f"{pair.upper()}_{timestamp}_{i+1}.png"
                path = os.path.join("screenshots", image_name)
                with open(path, "wb") as f:
                    f.write(img.getbuffer())
                img_paths[i] = path

        new_trade_dict = {
            "Date": pd.to_datetime(trade_date), "Pair": pair.upper(), "Direction": direction,
            "Session": session, "News_Category": news_category, "Weekly_Bias": weekly_bias,
            "Daily_Bias": daily_bias, "Liquidity_Swept": liquidity_swept, "Setup_Trigger": setup_trigger,
            "Setup_Grade": setup_grade, "Trade_Thesis": trade_thesis, "Entry_Price": entry_price,
            "Exit_Price": exit_price, "PnL": pnl, "Outcome": outcome, "Psychology": psychology,
            "Screenshot_Path": img_paths[0], "Screenshot_2": img_paths[1], "Screenshot_3": img_paths[2],
            "Screenshot_4": img_paths[3], "Screenshot_5": img_paths[4], "Screenshot_6": img_paths[5], "Screenshot_7": img_paths[6]
        }
        
        new_trade = pd.DataFrame([new_trade_dict])
        df = pd.concat([df, new_trade], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success(f"Trade Added to {journal_account}!")
        st.rerun()
    else:
        st.sidebar.error("Please enter a Pair name.")

# ----------------- Multi-Dashboards -----------------
if not df.empty:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Main Overview", "🧠 Strategy & Psychology", "📅 Advanced Analytics", "🖼️ Trade Gallery"])
    
    with tab1:
        st.subheader("Performance Overview")
        display_df = df.drop(columns=["Screenshot_Path", "Screenshot_2", "Screenshot_3", "Screenshot_4", "Screenshot_5", "Screenshot_6", "Screenshot_7", "Trade_Thesis"], errors='ignore')
        st.dataframe(display_df, use_container_width=True)
        
    with tab4:
        st.subheader("🖼️ Review Trade Screenshots & Thesis")
        if "Screenshot_Path" in df.columns:
            trades_with_data = df.copy()
            trade_options = trades_with_data["Date"].dt.strftime('%Y-%m-%d').astype(str) + " | " + trades_with_data["Pair"] + " | " + trades_with_data["Outcome"]
            
            selected_idx = st.selectbox("Select a Trade to View Details:", trades_with_data.index, format_func=lambda x: trade_options[x])
            
            st.markdown(f"**🧠 Trade Thesis:** {trades_with_data.loc[selected_idx, 'Trade_Thesis']}")
            st.markdown(f"**🎯 Setup Grade:** {trades_with_data.loc[selected_idx, 'Setup_Grade']}")
            
            img_cols = ["Screenshot_Path", "Screenshot_2", "Screenshot_3", "Screenshot_4", "Screenshot_5", "Screenshot_6", "Screenshot_7"]
            for col in img_cols:
                if col in trades_with_data.columns:
                    img_path = trades_with_data.loc[selected_idx, col]
                    if pd.notna(img_path) and str(img_path).strip() != "" and os.path.exists(str(img_path)):
                        st.image(str(img_path), use_container_width=True)
