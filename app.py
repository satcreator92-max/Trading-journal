import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CEO Trading Journal", layout="wide")

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
        # Puthiya columns add panniyachu (Checklist, Zone Type, Psychology, After Trade Chart)
        return pd.DataFrame(columns=[
            "Date", "Pair", "Direction", "Session", "News_Category", 
            "Zone_Type", "Weekly_Setup", "1H_SMT", "5m_CISD", 
            "Entry_Price", "Exit_Price", "PnL", "Outcome", "Psychology", "After_Chart_Link"
        ])

df = load_data(DATA_FILE)

st.title(f"📈 CEO Dashboard: {journal_account}")

# ----------------- Add New Trade -----------------
st.sidebar.header("📝 Add New Trade")
trade_date = st.sidebar.date_input("Trade Date")
pair = st.sidebar.text_input("Pair (e.g., GBPUSD, GBPCAD)")
direction = st.sidebar.selectbox("Direction", ["Long", "Short"])
session = st.sidebar.selectbox("Session", ["Asian", "London", "New York", "Frankfurt"])

# 4H BoS mandatory, so FVG or OB mattum select panna pothum
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

# Trade Outcome & Psychology
outcome = st.sidebar.selectbox("Trade Outcome", ["Hit TP (1:2)", "Hit SL", "Breakeven", "Manual Close"])
psychology = st.sidebar.selectbox("Trade Psychology", [
    "Followed Perfect Plan", 
    "FOMO Entry (Avasarappatten)", 
    "Revenge Trade", 
    "Closed Early (Payanthutten)",
    "Hesitated / Late Entry"
])

# After Finish Trade Screenshot
after_chart_link = st.sidebar.text_input("After Trade Screenshot (Link)")

if st.sidebar.button("Save Trade"):
    if pair:
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
            "After_Chart_Link": after_chart_link
        }])
        
        df = pd.concat([df, new_trade], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success(f"Trade Added to {journal_account}!")
        st.rerun()
    else:
        st.sidebar.error("Please enter a Pair name.")

# ----------------- Multi-Dashboards -----------------
if not df.empty:
    tab1, tab2, tab3 = st.tabs([
        "📊 Main Overview", 
        "🧠 Psychology & Strategy", 
        "📅 Advanced Analytics"
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
        # Link ah clickable ah matha
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "After_Chart_Link": st.column_config.LinkColumn("After Trade Chart")
            }
        )
        
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

else:
    st.info(f"No trades recorded yet in {journal_account}. Start tracking your CEO setup!")
