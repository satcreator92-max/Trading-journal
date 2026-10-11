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
        return df
    else:
        # Weekly மற்றும் Daily தனித்தனியாகப் பிரிக்கப்பட்டுள்ளது
        return pd.DataFrame(columns=[
            "Date", "Pair", "Direction", "Session", "News_Category", 
            "Weekly_Bias", "Daily_Bias", "Liquidity_Swept", "Setup_Trigger", "Setup_Grade", "Trade_Thesis",
            "Entry_Price", "Exit_Price", "PnL", "Outcome", "Psychology", "Screenshot_Path"
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
    # Weekly மற்றும் Daily Bias தனித்தனி Dropdown ஆக மாற்றப்பட்டுள்ளது
    weekly_bias = st.selectbox("Weekly Bias", ["Bullish", "Bearish", "Neutral / Ranging"])
    daily_bias = st.selectbox("Daily Bias", ["Bullish", "Bearish", "Neutral / Ranging"])
    
    liquidity_swept = st.selectbox("Liquidity Swept", [
        "Previous Day High / Low", 
        "Previous Week High / Low", 
        "Asian Session High / Low", 
        "Trendline / Structural Liquidity",
        "None"
    ])
    setup_trigger = st.selectbox("Setup Trigger", [
        "Sweep + 4H Zone + SMT", 
        "Continuation / Trend Follow", 
        "SMT at Key Level",
        "Other"
    ])
    setup_grade = st.radio("Setup Grade", [
        "A+ Setup (All Timeframes Aligned)", 
        "A Setup (Dynamic Liquidity + 4H Zone)", 
        "B Setup (Lower TF Confluence Only)"
    ])
    trade_thesis = st.text_area("Trade Thesis (Your Logic)", placeholder="Example: Weekly was Bearish, but Monday Daily candle was Bullish. I used Daily as liquidity for the 4H Zone...")

with st.sidebar.expander("💰 3. Trade Results & Psychology", expanded=True):
    entry_price = st.number_input("Entry Price", format="%.5f")
    exit_price = st.number_input("Exit Price", format="%.5f")
    pnl = st.number_input("Profit / Loss ($)", format="%.2f")
    outcome = st.selectbox("Trade Outcome", ["Hit TP (1:2)", "Hit SL", "Breakeven", "Manual Close"])
    psychology = st.selectbox("Trade Psychology", [
        "Followed Perfect Plan", 
        "FOMO Entry (Avasarappatten)", 
        "Revenge Trade", 
        "Closed Early (Payanthutten)",
        "Hesitated / Late Entry"
    ])

with st.sidebar.expander("🖼️ 4. Chart Screenshot", expanded=True):
    uploaded_image = st.file_uploader("Upload After Trade Screenshot", type=["png", "jpg", "jpeg"])

if st.sidebar.button("💾 Save Trade", use_container_width=True):
    if pair:
        screenshot_path = ""
        if uploaded_image is not None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = f"{pair.upper()}_{timestamp}.png"
            screenshot_path = os.path.join("screenshots", image_name)
            with open(screenshot_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

        new_trade = pd.DataFrame([{
            "Date": pd.to_datetime(trade_date),
            "Pair": pair.upper(),
            "Direction": direction,
            "Session": session,
            "News_Category": news_category,
            "Weekly_Bias": weekly_bias,
            "Daily_Bias": daily_bias,
            "Liquidity_Swept": liquidity_swept,
            "Setup_Trigger": setup_trigger,
            "Setup_Grade": setup_grade,
            "Trade_Thesis": trade_thesis,
            "Entry_Price": entry_price,
            "Exit_Price": exit_price,
            "PnL": pnl,
            "Outcome": outcome,
            "Psychology": psychology,
            "Screenshot_Path": screenshot_path
        }])
        
        df = pd.concat([df, new_trade], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success(f"Trade Added to {journal_account}!")
        st.rerun()
    else:
        st.sidebar.error("Please enter a Pair name.")

# ----------------- Multi-Dashboards -----------------
if not df.empty:
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Main Overview", 
        "🧠 Strategy & Psychology", 
        "📅 Advanced Analytics",
        "🖼️ Trade Gallery"
    ])
    
    with tab1:
        st.subheader("Performance Overview")
        total_trades = len(df)
        win_rate = (len(df[df["PnL"] > 0]) / total_trades) * 100 if total_trades > 0 else 0
        net_pnl = df["PnL"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Trades", total_trades)
        col2.metric("Win Rate", f"{win_rate:.1f}%")
        col3.metric("Net PnL", f"${net_pnl:.2f}")
        
        st.write("### Trade History")
        display_df = df.drop(columns=["Screenshot_Path", "Trade_Thesis"]) if "Screenshot_Path" in df.columns else df
        st.dataframe(display_df, use_container_width=True)
        
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Trade Psychology")
            psy_count = df["Psychology"].value_counts().reset_index()
            psy_count.columns = ["Psychology", "Count"]
            st.bar_chart(psy_count.set_index("Psychology"))
            
        with col2:
            st.subheader("Setup Grade Performance")
            if "Setup_Grade" in df.columns:
                grade_pnl = df.groupby("Setup_Grade")["PnL"].sum().reset_index()
                st.bar_chart(grade_pnl.set_index("Setup_Grade"))
        
    with tab3:
        st.subheader("Pair vs Session Analytics")
        session_pair = df.groupby(["Session", "Pair"])["PnL"].sum().unstack().fillna(0)
        st.dataframe(session_pair, use_container_width=True)
        
    with tab4:
        st.subheader("🖼️ Review Trade Screenshots & Thesis")
        if "Screenshot_Path" in df.columns:
            trades_with_images = df[df["Screenshot_Path"].notna() & (df["Screenshot_Path"] != "")]
            
            if not trades_with_images.empty:
                trade_options = trades_with_images["Date"].dt.strftime('%Y-%m-%d').astype(str) + " | " + trades_with_images["Pair"] + " | " + trades_with_images["Outcome"]
                
                selected_trade_idx = st.selectbox(
                    "Select a Trade to View Details:", 
                    trades_with_images.index, 
                    format_func=lambda x: trade_options[x]
                )
                
                # Update Trade Thesis Display
                st.markdown(f"**📅 Timeframe Bias:** Weekly ({trades_with_images.loc[selected_trade_idx, 'Weekly_Bias']}) | Daily ({trades_with_images.loc[selected_trade_idx, 'Daily_Bias']})")
                st.markdown(f"**🧠 Trade Thesis:** {trades_with_images.loc[selected_trade_idx, 'Trade_Thesis']}")
                st.markdown(f"**🎯 Setup Grade:** {trades_with_images.loc[selected_trade_idx, 'Setup_Grade']}")
                
                img_path = trades_with_images.loc[selected_trade_idx, "Screenshot_Path"]
                if os.path.exists(img_path):
                    st.image(img_path, caption=trade_options[selected_trade_idx], use_container_width=True)
                else:
                    st.error("Image file not found!")
            else:
                st.info("No screenshots uploaded yet.")
        else:
            st.info("No screenshots available.")
else:
    st.info(f"No trades recorded yet in {journal_account}. Start tracking your CEO setup!")
