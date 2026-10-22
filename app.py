import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# 1. Cấu hình trang web Streamlit
st.set_page_config(page_title="Tra cứu giá cổ phiếu", layout="centered")

st.title("📈 Tra Cứu Giá Cổ Phiếu Việt Nam")
st.write("Nhập mã cổ phiếu để xem dữ liệu giá đóng cửa từ **01/01/2020 đến hôm nay**.")

# 2. Ô nhập mã cổ phiếu từ người dùng
symbol = st.text_input("Nhập mã cổ phiếu (ví dụ: VIC, VNM, VCB, VJC):", value="VIC").strip().upper()

# Ngày bắt đầu mặc định và ngày hôm nay
start_date = "2020-01-01"
end_date = date.today().strftime("%Y-%m-%d")

# 3. Nút bấm để vẽ biểu đồ và tải dữ liệu
if st.button("Vẽ đồ thị", type="primary"):
    if not symbol:
        st.warning("Vui lòng nhập mã cổ phiếu!")
    else:
        # Tự động thêm đuôi .VN cho các mã chứng khoán Việt Nam nếu chưa có
        ticker = symbol if symbol.endswith(".VN") else f"{symbol}.VN"
        
        with st.spinner(f"Đang tải dữ liệu cho mã {symbol}..."):
            # Tải dữ liệu từ Yahoo Finance
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        # Kiểm tra xem có dữ liệu trả về không
        if df.empty:
            st.error(f"Không tìm thấy dữ liệu cho mã '{symbol}'. Vui lòng kiểm tra lại mã cổ phiếu!")
        else:
            # Xử lý chuẩn hóa cột dữ liệu (sửa lỗi MultiIndex của yfinance)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Lấy cột giá đóng cửa và xóa dòng trống
            close_price = df[['Close']].dropna()

            # Hiển thị thông số tổng quan
            st.success(f"Đã tải thành công dữ liệu cổ phiếu **{symbol}**!")
            
            # 4. Vẽ biểu đồ tương tác bằng Plotly
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=close_price.index, 
                    y=close_price['Close'], 
                    mode='lines', 
                    name='Giá đóng cửa',
                    line=dict(color='#1f77b4', width=2)
                )
            )
            fig.update_layout(
                title=f"Biểu đồ giá đóng cửa cổ phiếu {symbol} (01/01/2020 - {end_date})",
                xaxis_title="Thời gian",
                yaxis_title="Giá đóng cửa (VND)",
                hovermode="x unified",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

            # 5. Bảng dữ liệu chi tiết
            st.subheader("📊 Bảng dữ liệu chi tiết")
            st.dataframe(close_price.tail(10), use_container_width=True)

            # 6. Nút tải file CSV
            csv = close_price.to_csv().encode('utf-8')
            st.download_button(
                label=f"📥 Tải dữ liệu CSV của {symbol}",
                data=csv,
                file_name=f"{symbol}_Close_2020_Present.csv",
                mime='text/csv'
            )
