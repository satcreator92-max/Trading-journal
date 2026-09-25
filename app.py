import streamlit as st
import pandas as pd
import os

# பேஜின் அமைப்பு
st.set_page_config(page_title="My Trading Journal", layout="wide")

# டேட்டாவை நிரந்தரமாக சேமிக்க ஒரு CSV ஃபைல் பெயர்
DATA_FILE = "trades.csv"

# CSV ஃபைல் இருந்தால் அதைப் படிக்கவும், இல்லையென்றால் புதிதாக டேபிள் உருவாக்கவும்
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Pair", "Direction", "Strategy", "Entry Price", "Exit Price", "PnL"])

# டேட்டாவை லோட் செய்தல்
df = load_data()

st.title("SMC Trading Journal Dashboard")

# இடதுபுற மெனு (Sidebar) - புதிய ட்ரேட் சேர்க்க
st.sidebar.header("Add New Trade")
trade_date = st.sidebar.date_input("Trade Date")
pair = st.sidebar.text_input("Pair (e.g., GBPCAD, EURNZD)")
direction = st.sidebar.selectbox("Direction", ["Long", "Short"])
strategy = st.sidebar.selectbox("Strategy Setup", ["4H BoS + OB", "4H BoS + FVG", "Liquidity Sweep"])
entry_price = st.sidebar.number_input("Entry Price", format="%.5f")
exit_price = st.sidebar.number_input("Exit Price", format="%.5f")
pnl = st.sidebar.number_input("Profit / Loss ($)", format="%.2f")

# ட்ரேடை சேவ் செய்வதற்கான பட்டன்
if st.sidebar.button("Save Trade"):
    if pair: # Pair பெயர் உள்ளதா என சரிபார்க்க
        new_trade = pd.DataFrame([{
            "Date": trade_date,
            "Pair": pair.upper(),
            "Direction": direction,
            "Strategy": strategy,
            "Entry Price": entry_price,
            "Exit Price": exit_price,
            "PnL": pnl
        }])
        
        # புதிய டேட்டாவை பழைய டேட்டாவுடன் இணைத்து CSV-யில் சேமிக்க
        df = pd.concat([df, new_trade], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        
        st.sidebar.success("Trade Added Successfully!")
        st.rerun() # பேஜை ரீலோட் செய்து புதிய டேட்டாவை மெயின் ஸ்க்ரீனில் காட்ட
    else:
        st.sidebar.error("Please enter a Pair name.")

# மெயின் ஸ்க்ரீன் - Analytics Overview
st.subheader("Analytics Overview")
if not df.empty:
    total_trades = len(df)
    win_rate = (len(df[df["PnL"] > 0]) / total_trades) * 100 if total_trades > 0 else 0
    net_pnl = df["PnL"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", total_trades)
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Net PnL", f"${net_pnl:.2f}")

    # Trade History Table
    st.subheader("Trade History")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No trades recorded yet. Use the left sidebar to add your first trade!")
