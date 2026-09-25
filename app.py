import streamlit as st
import pandas as pd
import os

# பேஜின் அமைப்பு - ப்ரோ லெவல் டேஷ்போர்டு டிசைன்
st.set_page_config(page_title="CEO Trading Journal", layout="wide")

DATA_FILE = "trades.csv"

# டேட்டாவை லோட் செய்யும் ஃபங்க்ஷன்
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # தேதியை (Date) அனாலிசிஸ் செய்வதற்கு ஏற்ற ஃபார்மெட்டிற்கு மாற்றுதல்
        df['Date'] = pd.to_datetime(df['Date']) 
        return df
    else:
        return pd.DataFrame(columns=["Date", "Pair", "Direction", "Session", "Strategy", "News_Category", "Entry_Price", "Exit_Price", "PnL"])

df = load_data()

st.title("📈 50Cr Prop Firm: CEO Dashboard")

# ----------------- இடதுபுற மெனு (Sidebar) -----------------
st.sidebar.header("Add New Trade")
trade_date = st.sidebar.date_input("Trade Date")
pair = st.sidebar.text_input("Pair (e.g., GBPCAD, EURNZD)")
direction = st.sidebar.selectbox("Direction", ["Long", "Short"])
session = st.sidebar.selectbox("Session", ["Asian", "London", "New York", "Frankfurt"])
strategy = st.sidebar.selectbox("Strategy Setup", ["4H BoS + OB", "4H BoS + FVG", "Liquidity Sweep"])

# புதிதாக சேர்க்கப்பட்ட News Category
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

# ட்ரேடை சேவ் செய்யும் பட்டன்
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
        st.sidebar.success("Trade Added Successfully!")
        st.rerun()
    else:
        st.sidebar.error("Please enter a Pair name.")

# ----------------- மல்டி-டேஷ்போர்டு (Multi-Dashboards) -----------------
if not df.empty:
    # 4 தனித்தனி டேப்களை (Tabs) உருவாக்குதல்
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Main Overview", 
        "📰 News & Strategy", 
        "📅 Seasonality", 
        "🌍 Pair & Session Mastery"
    ])
    
    # டேஷ்போர்டு 1: Main Overview
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
        
    # டேஷ்போர்டு 2: News & Strategy Analytics
    with tab2:
        st.subheader("News Impact Analysis")
        st.write("எந்த நியூஸ் நேரத்தில் மார்க்கெட் நமக்குச் சாதகமாக உள்ளது?")
        news_pnl = df.groupby("News_Category")["PnL"].sum().reset_index()
        st.bar_chart(news_pnl.set_index("News_Category"))
        
        st.subheader("Strategy Performance")
        st.write("எந்த SMC செட்-அப் அதிக லாபம் தருகிறது?")
        strat_pnl = df.groupby("Strategy")["PnL"].sum().reset_index()
        st.bar_chart(strat_pnl.set_index("Strategy"))
        
    # டேஷ்போர்டு 3: Seasonality
    with tab3:
        st.subheader("Monthly Seasonality (மாதாந்திர பகுப்பாய்வு)")
        st.write("வருடத்தின் எந்த மாதங்களில் நமது சிஸ்டம் சிறப்பாகச் செயல்படுகிறது?")
        # தேதியிலிருந்து மாதத்தை மட்டும் தனியாகப் பிரித்தெடுத்தல்
        df['Month'] = df['Date'].dt.month_name()
        month_pnl = df.groupby("Month")["PnL"].sum().reset_index()
        st.bar_chart(month_pnl.set_index("Month"))
        
    # டேஷ்போர்டு 4: Pair & Session Mastery
    with tab4:
        st.subheader("Pair vs Session Analytics")
        st.write("எந்த செஷனில் எந்த Pair நமக்கு ஏற்றது?")
        # செஷன் மற்றும் பேரை வைத்து லாபத்தைக் கணக்கிடுதல்
        session_pair = df.groupby(["Session", "Pair"])["PnL"].sum().unstack().fillna(0)
        st.dataframe(session_pair, use_container_width=True)

else:
    st.info("No trades recorded yet. Use the left sidebar to add your first trade and unlock the CEO Dashboard!")
