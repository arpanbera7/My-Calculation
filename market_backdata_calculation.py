import streamlit as st
import pandas as pd
import io

st.title("Market Sales Analyzer")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    # Detect header row dynamically
    def detect_header_row(excel_bytes):
        for header_row in range(10):
            df_try = pd.read_excel(io.BytesIO(excel_bytes), engine='openpyxl', header=header_row)
            if {'Market', 'Individual Periods', 'Value Sales (US$)'}.issubset(df_try.columns):
                return header_row
        return None

    excel_bytes = uploaded_file.read()
    header_row = detect_header_row(excel_bytes)

    if header_row is not None:
        df = pd.read_excel(io.BytesIO(excel_bytes), engine='openpyxl', header=header_row)
        df = df[['Market', 'Individual Periods', 'Value Sales (US$)']]
        df = df.dropna(subset=['Market', 'Individual Periods', 'Value Sales (US$)'])

        # Market selection
        market = st.selectbox("Select Market", sorted(df['Market'].unique()))

        # Filter periods for selected market
        filtered_df = df[df['Market'] == market]
        periods = sorted(filtered_df['Individual Periods'].unique(), reverse=True)
        period = st.selectbox("Select Period", periods)

        # Input for months back
        months_back = st.number_input("Enter number of months back", min_value=1, max_value=60, value=12)

        # Calculate total sales
        if st.button("Calculate Total Sales"):
            filtered_df = filtered_df.drop_duplicates(subset=['Individual Periods'])
            filtered_df = filtered_df.set_index('Individual Periods').sort_index(ascending=False)

            if period in filtered_df.index:
                start_index = filtered_df.index.get_loc(period)
                end_index = start_index + months_back
                selected_data = filtered_df.iloc[start_index:end_index]
                total_sales = selected_data['Value Sales (US$)'].sum()

                st.success(f"Total Value Sales for '{market}' from '{period}' back {months_back} months:")
                st.write(f"${total_sales:,.2f}")
            else:
                st.error("Selected period not found in data.")
    else:
        st.error("Could not detect header row with required columns.")
