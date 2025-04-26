import subprocess
import sys
import json
import datetime
import re

# Install required packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import google.generativeai as genai
except ImportError:
    install("google-generativeai")
    import google.generativeai as genai

try:
    import streamlit as st
except ImportError:
    install("streamlit")
    import streamlit as st

try:
    import matplotlib.pyplot as plt
except ImportError:
    install("matplotlib")
    import matplotlib.pyplot as plt

# Initialize Gemini client
genai.configure(api_key="AIzaSyATju07lbZzWjn3DGdGH5sHq7bs-MoeSes")  # <-- Apni Gemini API key lagani hai yahan

model = genai.GenerativeModel('gemini-1.5-pro')  # ya koi aur Gemini model

def generate_forecast_from_gemini(product_name, country, past_years, future_years):
    current_year = datetime.datetime.now().year

    prompt = f"""
You are an economic expert.
Generate a realistic price history and forecast for:

Product: {product_name}
Country: {country}
Past Years: {past_years}
Future Years: {future_years}
Current Year: {current_year}

Return STRICTLY a valid JSON object with exactly four keys:
- 'past_prices': dictionary of year: price.
- 'future_prices': dictionary of year: price.
- 'yearly_percentage_change': dictionary of year: percentage change compared to previous year.
- 'current_price': float (the price for the current year {current_year})

Each price must be a float (decimal number) and percentage change must be float too.
No text, no explanation, only raw JSON object.
"""

    response = model.generate_content(prompt)
    reply = response.text.strip()

    try:
        match = re.search(r'\{.*\}', reply, re.DOTALL)
        if match:
            cleaned_json = match.group(0)
            forecast = json.loads(cleaned_json)
        else:
            raise ValueError("No JSON object found in the response.")
    except Exception as e:
        raise ValueError(f"Failed to parse JSON from Gemini response: {e}")

    return forecast

# Streamlit UI
st.set_page_config(page_title="Product Price Forecaster", layout="centered")
st.title("\U0001F6D2 Product Price Forecast (AI Powered by Gemini)")

st.markdown("Enter your product details below:")

with st.form("forecast_form"):
    product_name = st.text_input("Product Name", placeholder="e.g., Coca Cola 1L")
    country = st.text_input("Country", placeholder="e.g., Pakistan")
    past_years = st.number_input("Past Years", min_value=1, max_value=10, value=3)
    future_years = st.number_input("Future Years", min_value=1, max_value=10, value=3)
    submitted = st.form_submit_button("Get Forecast")

if submitted:
    try:
        forecast = generate_forecast_from_gemini(product_name, country, past_years, future_years)

        past_prices = forecast.get("past_prices", {})
        future_prices = forecast.get("future_prices", {})
        yearly_percentage_change = forecast.get("yearly_percentage_change", {})
        current_price = forecast.get("current_price", 0)

        avg_past = sum(past_prices.values()) / len(past_prices) if past_prices else 0
        avg_future = sum(future_prices.values()) / len(future_prices) if future_prices else 0

        if avg_past != 0:
            overall_percentage_change = ((avg_future - avg_past) / avg_past) * 100
        else:
            overall_percentage_change = 0

        forecast_output = {
            "past_prices": past_prices,
            "future_prices": future_prices,
            "yearly_percentage_change": yearly_percentage_change,
            "current_price": round(current_price, 2),
            "average_past_price": round(avg_past, 2),
            "average_future_price": round(avg_future, 2),
            "overall_percentage_change": round(overall_percentage_change, 2)
        }

        st.subheader("\U0001F9FE Forecast Result (JSON)")
        st.json(forecast_output)

        if past_prices and future_prices:
            # Merge past, current, future prices
            current_year = str(datetime.datetime.now().year)
            all_prices = {**past_prices, current_year: current_price, **future_prices}

            # Sort by year
            sorted_years = sorted(all_prices.keys())
            sorted_prices = [all_prices[year] for year in sorted_years]

            # Plot
            plt.figure(figsize=(10,5))
            plt.plot(sorted_years, sorted_prices, marker='o', color='blue', linestyle='-')
            plt.scatter(current_year, current_price, color='red', label="Current Price")
            plt.title(f"Price Forecast for {product_name} in {country}")
            plt.xlabel("Year")
            plt.ylabel("Price")
            plt.grid(True)
            plt.legend()
            st.pyplot(plt)

            st.subheader("\U0001F4B8 Price Averages and Trend")
            st.markdown(f"**Current Price ({current_year}):** {current_price:.2f}")
            st.markdown(f"**Average Past Price:** {avg_past:.2f}")
            st.markdown(f"**Average Future Price:** {avg_future:.2f}")
            st.markdown(f"**Overall Expected Change:** {overall_percentage_change:+.2f}%")

        else:
            st.error("The forecast result does not contain expected 'past_prices' and 'future_prices'. Please try again.")

    except Exception as e:
        st.error(f"\u274C Error: {e}")
