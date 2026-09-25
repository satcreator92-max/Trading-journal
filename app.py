import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CEO Trading Journal", layout="wide")

# ----------------- Account Selection -----------------
st.sidebar.header("📁 Journal Selection")

# Puthikya 3 account-kal
journal_account = st.sidebar.selectbox("Select Account", [
    "50Cr Prop Firm Account",
    "GBPCAD Test",
    "GBPNZD Test" 
])

# Oru account-num thani thani CSV files
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
        return pd.DataFrame(columns=["Date", "Pair", "Direction", "Session", "Strategy", "News_Category", "Entry_Price", "Exit_Price", "PnL"])

df = load_data(DATA_FILE)

st.title(f"📈 CEO Dashboard: {journal_account}")

# ----------------- Add New Trade -----------------
st.sidebar.header("Add New Trade")
trade_date = st.sidebar.date_input("Trade Date")
pair = st.sidebar.text_input("Pair (e.g., GBPCAD, EURNZD)")
direction = st.sidebar.selectbox("Direction", ["Long", "Short"])
session = st.sidebar.selectbox("Session", ["Asian", "London", "New York", "Frankfurt"])
strategy = st.sidebar.selectbox("Strategy Setup", ["4H BoS + OB", "4H BoS + FVG", "Liquidity Sweep"])

news_category = st.sidebar.selectbox("News Category", [
    "None (No News)", 
    "CPI / Inflation", 
    "NFP / Employment", 
    "FOMC / Interest Rates", 
    "GDP / Retail Sales",
    "Other High Impact"
])

entry_price = st.sidebar.number_input("Entry Price", format="%.5f")
exit_price = st.sidebar.number_input("Exit Price", format="%.5f")
pnl = st.sidebar.number_input("Profit / Loss ($)", format="%.2f")

if st.sidebar.button("Save Trade"):
    if pair:
        new_trade = pd.DataFrame([{
            "Date": pd.to_datetime(trade_date),
            "Pair": pair.upper(),
            "Direction": direction,
            "Session": session,
            "Strategy": strategy,
            "News_Category": news_category,
            "Entry_Price": entry_price,
            "Exit_Price": exit_price,
            "PnL": pnl
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
        "📰 News & Strategy", 
        "📅 Seasonality", 
        "🌍 Pair & Session Mastery"
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
        st.dataframe(df, use_container_width=True)
        
    with tab2:
        st.subheader("News Impact Analysis")
        news_pnl = df.groupby("News_Category")["PnL"].sum().reset_index()
        st.bar_chart(news_pnl.set_index("News_Category"))
        
        st.subheader("Strategy Performance")
        strat_pnl = df.groupby("Strategy")["PnL"].sum().reset_index()
        st.bar_chart(strat_pnl.set_index("Strategy"))
        
    with tab3:
        st.subheader("Monthly Seasonality")
        df['Month'] = df['Date'].dt.month_name()
        month_pnl = df.groupby("Month")["PnL"].sum().reset_index()
        st.bar_chart(month_pnl.set_index("Month"))
        
    with tab4:
        st.subheader("Pair vs Session Analytics")
        session_pair = df.groupby(["Session", "Pair"])["PnL"].sum().unstack().fillna(0)
        st.dataframe(session_pair, use_container_width=True)

else:
    st.info(f"No trades recorded yet in {journal_account}. Start adding your trades!")
