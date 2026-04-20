import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import time
from datetime import datetime

st.set_page_config(page_title="Stock Dashboard", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

toggle = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = toggle

if st.session_state.dark_mode:
    bg_color = "#0f172a"
    text_color = "white"
    card_bg = "rgba(255,255,255,0.05)"
    glow = "0 0 20px #00f2ff"
else:
    bg_color = "#f5f5f5"
    text_color = "black"
    card_bg = "rgba(0,0,0,0.05)"
    glow = "none"

st.markdown(f"""
<style>
.stApp {{
    background: {bg_color};
    color: {text_color};
}}
.glass {{
    background: {card_bg};
    backdrop-filter: blur(12px);
    border-radius: 15px;
    padding: 20px;
    box-shadow: {glow};
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
}}
.neon {{
    color: #00f2ff;
    text-shadow: 0 0 10px #00f2ff, 0 0 20px #00f2ff;
    text-align: center;
}}
</style>
""", unsafe_allow_html=True)

st.sidebar.header("📊 Settings")

stock = st.sidebar.text_input("Primary Stock", "AAPL")

compare_stocks = st.sidebar.multiselect(
    "Compare Stocks",
    ["AAPL", "MSFT", "GOOG", "META", "TSLA"]
)

interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m"])
period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo"])

chart_type = st.sidebar.radio("Chart Type", ["Line", "Candlestick"])

refresh_rate = st.sidebar.slider("Auto Refresh (sec)", 5, 60, 10)

st.markdown('<h1 class="neon">📊 Real-Time Stock Dashboard</h1>', unsafe_allow_html=True)

try:
    data = yf.download(stock, period=period, interval=interval)

    if data.empty:
        st.warning("⚠️ No data found. Try another stock.")
        st.stop()

    data.columns = data.columns.get_level_values(0)

except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

data['MA20'] = data['Close'].rolling(20).mean()

latest_price = data['Close'].iloc[-1]
prev_price = data['Close'].iloc[-2]

change = latest_price - prev_price
percent = (change / prev_price) * 100

st.markdown('<div class="glass">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

col1.metric("💰 Price", f"${latest_price:.2f}")
col2.metric("📈 Change", f"{change:.2f}", f"{percent:.2f}%")
col3.metric("📊 Volume", int(data['Volume'].iloc[-1]))

st.markdown('</div>', unsafe_allow_html=True)

fig = go.Figure()

if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=stock
    ))
else:
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=stock
    ))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data['MA20'],
    mode='lines',
    name='MA20',
    line=dict(dash='dash')
))

for s in compare_stocks:
    try:
        comp = yf.download(s, period=period, interval=interval)
        if not comp.empty:
            comp.columns = comp.columns.get_level_values(0)
            fig.add_trace(go.Scatter(
                x=comp.index,
                y=comp['Close'],
                mode='lines',
                name=s
            ))
    except:
        pass

fig.update_layout(
    template="plotly_dark" if st.session_state.dark_mode else "plotly",
    height=600,
    title=f"{stock} Chart"
)

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

time.sleep(refresh_rate)
st.rerun()

with st.expander("📄 Show Raw Data"):
    st.dataframe(data.tail(50))

st.markdown("""
<hr>
<div style='text-align: center;'>

<p style="font-size:18px;">Made with ❤️ by <b>DWKR</b></p>

<a href="https://www.linkedin.com/in/diwakar-jha-064130229/" target="_blank">
    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="35" style="margin:10px;">
</a>

<a href="https://github.com/Stfu-diwakar" target="_blank">
    <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="35" style="margin:10px;">
</a>

</div>
""", unsafe_allow_html=True)
