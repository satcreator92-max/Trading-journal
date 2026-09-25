import streamlit as st
import pandas as pd

# Page Configuration (Dark Mode Default by Streamlit)
st.set_page_config(page_title="My Trading Journal", layout="wide")
st.title("📊 SMC Trading Journal Dashboard")

# Background data storage setup
if 'trades' not in st.session_state:
    st.session_state.trades = pd.DataFrame(columns=["Date", "Pair", "Direction", "Strategy", "Entry Price", "Exit Price", "PnL ($)"])

# ---------------- Sidebar: Trade Entry Form ----------------
st.sidebar.header("➕ Add New Trade")
date = st.sidebar.date_input("Trade Date")
pair = st.sidebar.text_input("Pair (e.g., GBPCAD, EURNZD)").upper()
direction = st.sidebar.selectbox("Direction", ["Long", "Short"])
strategy = st.sidebar.selectbox("Strategy Setup", ["4H BoS + FVG", "4H BoS + OB", "Other"])
entry = st.sidebar.number_input("Entry Price", format="%.5f")
exit_price = st.sidebar.number_input("Exit Price", format="%.5f")
pnl = st.sidebar.number_input("Profit / Loss ($)", format="%.2f")

if st.sidebar.button("Save Trade"):
    new_trade = pd.DataFrame([[date, pair, direction, strategy, entry, exit_price, pnl]],
                             columns=["Date", "Pair", "Direction", "Strategy", "Entry Price", "Exit Price", "PnL ($)"])
    st.session_state.trades = pd.concat([st.session_state.trades, new_trade], ignore_index=True)
    st.sidebar.success("Trade Added Successfully!")

# ---------------- Main Dashboard: Analytics (Like JournexFX) ----------------
st.header("📈 Analytics Overview")
df = st.session_state.trades

if not df.empty:
    # Calculations
    total_trades = len(df)
    winning_trades = len(df[df['PnL ($)'] > 0])
    win_rate = (winning_trades / total_trades) * 100
    total_pnl = df['PnL ($)'].sum()

    # Top Metric Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", total_trades)
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Net PnL", f"${total_pnl:.2f}")

    # Trade History Table
    st.subheader("📝 Trade History")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No trades recorded yet. Use the left sidebar to add your first trade!")
