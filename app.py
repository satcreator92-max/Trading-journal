import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="CEO Trading Journal", layout="wide")

# இமேஜ்களை சேமிக்க 'screenshots' என்ற Folder-ஐ உருவாக்குவது
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
        # Chart_Link-ஐ நீக்கிவிட்டு Screenshot_Path சேர்க்கப்பட்டுள்ளது
        return pd.DataFrame(columns=[
            "Date", "Pair", "Direction", "Session", "News_Category", 
            "Zone_Type", "Weekly_Setup", "1H_SMT", "5m_CISD", 
            "Entry_Price", "Exit_Price", "PnL", "Outcome", "Psychology", "Screenshot_Path"
        ])

df = load_data(DATA_FILE)

st.title(f"📈 CEO Dashboard: {journal_account}")

# ----------------- Add New Trade -----------------
st.sidebar.header("📝 Add New Trade")
trade_date = st.sidebar.date_input("Trade Date")
pair = st.sidebar.text_input("Pair (e.g., GBPUSD, GBPCAD)")
direction = st.sidebar.selectbox("Direction", ["Long", "Short"])
session = st.sidebar.selectbox("Session", ["Asian", "London", "New York", "Frankfurt"])

zone_type = st.sidebar.selectbox("4H Entry Zone (After BoS)", ["4H FVG", "4H Order Block (OB)"])

news_category = st.sidebar.selectbox("News Category", [
    "None (No News)", "CPI / Inflation", "NFP / Employment", "FOMC / Interest Rates", "GDP / Retail Sales", "Other High Impact"
])

st.sidebar.markdown("### ✅ Strategy Checklist")
chk_weekly = st.sidebar.checkbox("Weekly Sweep / Strong Break")
chk_smt = st.sidebar.checkbox("1H SMT Divergence Created")
chk_cisd = st.sidebar.checkbox("5m CISD Proper Close")

entry_price = st.sidebar.number_input("Entry Price", format="%.5f")
exit_price = st.sidebar.number_input("Exit Price", format="%.5f")
pnl = st.sidebar.number_input("Profit / Loss ($)", format="%.2f")

outcome = st.sidebar.selectbox("Trade Outcome", ["Hit TP (1:2)", "Hit SL", "Breakeven", "Manual Close"])
psychology = st.sidebar.selectbox("Trade Psychology", [
    "Followed Perfect Plan", 
    "FOMO Entry (Avasarappatten)", 
    "Revenge Trade", 
    "Closed Early (Payanthutten)",
    "Hesitated / Late Entry"
])

# புதிதாக சேர்க்கப்பட்ட இமேஜ் அப்லோடர் (Image Uploader)
uploaded_image = st.sidebar.file_uploader("Upload After Trade Screenshot", type=["png", "jpg", "jpeg"])

if st.sidebar.button("Save Trade"):
    if pair:
        # இமேஜ் அப்லோடு செய்யப்பட்டிருந்தால் அதை Folder-ல் Save செய்வது
        screenshot_path = ""
        if uploaded_image is not None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # ஒவ்வொரு இமேஜுக்கும் ஒரு பிரத்யேக பெயர் (உதா: GBPUSD_20261002_201530.png)
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
            "Zone_Type": zone_type,
            "Weekly_Setup": chk_weekly,
            "1H_SMT": chk_smt,
            "5m_CISD": chk_cisd,
            "Entry_Price": entry_price,
            "Exit_Price": exit_price,
            "PnL": pnl,
            "Outcome": outcome,
            "Psychology": psychology,
            "Screenshot_Path": screenshot_path
        }])
        
        df = pd.concat([df, new_trade], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success(f"Trade Added & Screenshot Saved to {journal_account}!")
        st.rerun()
    else:
        st.sidebar.error("Please enter a Pair name.")

# ----------------- Multi-Dashboards -----------------
if not df.empty:
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Main Overview", 
        "🧠 Psychology & Strategy", 
        "📅 Advanced Analytics",
        "🖼️ Trade Gallery"  # புதிய டேப்
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
        # டேபிளில் தேவையற்ற பெரிய இமேஜ் பாத் தெரிவதைத் தவிர்க்கலாம்
        display_df = df.drop(columns=["Screenshot_Path"]) if "Screenshot_Path" in df.columns else df
        st.dataframe(display_df, use_container_width=True)
        
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Trade Psychology")
            psy_count = df["Psychology"].value_counts().reset_index()
            psy_count.columns = ["Psychology", "Count"]
            st.bar_chart(psy_count.set_index("Psychology"))
            
        with col2:
            st.subheader("Zone Performance (FVG vs OB)")
            zone_pnl = df.groupby("Zone_Type")["PnL"].sum().reset_index()
            st.bar_chart(zone_pnl.set_index("Zone_Type"))
        
    with tab3:
        st.subheader("Pair vs Session Analytics")
        session_pair = df.groupby(["Session", "Pair"])["PnL"].sum().unstack().fillna(0)
        st.dataframe(session_pair, use_container_width=True)
        
    # --- புதிதாக சேர்க்கப்பட்ட Trade Gallery ---
    with tab4:
        st.subheader("🖼️ Review Trade Screenshots")
        if "Screenshot_Path" in df.columns:
            # இமேஜ் உள்ள ட்ரேடுகளை மட்டும் ஃபில்டர் செய்வது
            trades_with_images = df[df["Screenshot_Path"].notna() & (df["Screenshot_Path"] != "")]
            
            if not trades_with_images.empty:
                # Dropdown-ல் ட்ரேடுகளைக் காட்டுவதற்கான ஆப்ஷன் (Date + Pair + Outcome)
                trade_options = trades_with_images["Date"].dt.strftime('%Y-%m-%d').astype(str) + " | " + trades_with_images["Pair"] + " | " + trades_with_images["Outcome"]
                
                selected_trade_idx = st.selectbox(
                    "Select a Trade to View Details & Screenshot:", 
                    trades_with_images.index, 
                    format_func=lambda x: trade_options[x]
                )
                
                # தேர்ந்தெடுக்கப்பட்ட ட்ரேடின் இமேஜைக் காட்டுவது
                img_path = trades_with_images.loc[selected_trade_idx, "Screenshot_Path"]
                if os.path.exists(img_path):
                    st.image(img_path, caption=trade_options[selected_trade_idx], use_container_width=True)
                else:
                    st.error("Image file not found! கம்ப்யூட்டரில் இருந்து இமேஜ் அழிக்கப்பட்டிருக்கலாம்.")
            else:
                st.info("No screenshots uploaded yet. புதிய ட்ரேடுடன் இமேஜை அப்லோடு செய்து பார்க்கவும்.")
        else:
            st.info("No screenshots available.")

else:
    st.info(f"No trades recorded yet in {journal_account}. Start tracking your CEO setup!")
