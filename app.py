# ----------------- Multi-Dashboards -----------------
if not df.empty:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Main Overview", "🧠 Strategy & Psychology", "📅 Advanced Analytics", "🖼️ Trade Gallery"])
    
    with tab1:
        st.subheader("Performance Overview")
        display_df = df.drop(columns=["Screenshot_Path", "Screenshot_2", "Screenshot_3", "Screenshot_4", "Screenshot_5", "Screenshot_6", "Screenshot_7", "Trade_Thesis"], errors='ignore')
        st.dataframe(display_df, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Trade Psychology")
            if "Psychology" in df.columns:
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
        if "Session" in df.columns and "Pair" in df.columns and "PnL" in df.columns:
            session_pair = df.groupby(["Session", "Pair"])["PnL"].sum().unstack().fillna(0)
            st.dataframe(session_pair, use_container_width=True)
        
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
