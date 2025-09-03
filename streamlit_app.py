# app.py
# Unit Converter with Streamlit
# Offline, no API keys required.

import streamlit as st

# ---------------------------
# Unit definitions (linear categories map to a base unit)
# ---------------------------
LINEAR_UNITS = {
    "length": {         # base: meter
        "meter (m)": 1.0,
        "kilometer (km)": 1000.0,
        "centimeter (cm)": 0.01,
        "millimeter (mm)": 0.001,
        "mile (mi)": 1609.344,
        "yard (yd)": 0.9144,
        "foot (ft)": 0.3048,
        "inch (in)": 0.0254,
    },
    "mass": {           # base: kilogram
        "kilogram (kg)": 1.0,
        "gram (g)": 0.001,
        "milligram (mg)": 1e-6,
        "metric ton (t)": 1000.0,
        "pound (lb)": 0.45359237,
        "ounce (oz)": 0.028349523125,
    },
    "volume": {         # base: liter
        "liter (L)": 1.0,
        "milliliter (mL)": 0.001,
        "US gallon (gal)": 3.785411784,
        "US quart (qt)": 0.946352946,
        "US pint (pt)": 0.473176473,
        "cup (US)": 0.2365882365,
        "tablespoon (tbsp)": 0.01478676478,
        "teaspoon (tsp)": 0.00492892159,
    },
    "time": {           # base: second
        "second (s)": 1.0,
        "minute (min)": 60.0,
        "hour (h)": 3600.0,
        "day (d)": 86400.0,
    },
    "speed": {          # base: m/s
        "meter/second (m/s)": 1.0,
        "kilometer/hour (km/h)": 1000.0/3600.0,
        "mile/hour (mph)": 1609.344/3600.0,
        "knot (kn)": 1852.0/3600.0,
    },
    "data": {           # base: byte
        "byte (B)": 1.0,
        "kilobyte (KB, 1024)": 1024.0,
        "megabyte (MB, 1024)": 1024.0**2,
        "gigabyte (GB, 1024)": 1024.0**3,
        "terabyte (TB, 1024)": 1024.0**4,
    },
}

TEMP_UNITS = ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"]

ALL_CATEGORIES = list(LINEAR_UNITS.keys()) + ["temperature"]

# ---------------------------
# Conversion logic
# ---------------------------
def convert_linear(category: str, from_unit: str, to_unit: str, value: float) -> float:
    factors = LINEAR_UNITS[category]
    value_in_base = value * factors[from_unit]
    return value_in_base / factors[to_unit]

def temp_to_celsius(v: float, from_u: str) -> float:
    if "Celsius" in from_u:
        return v
    elif "Fahrenheit" in from_u:
        return (v - 32.0) * 5.0/9.0
    elif "Kelvin" in from_u:
        return v - 273.15

def celsius_to_target(v_c: float, to_u: str) -> float:
    if "Celsius" in to_u:
        return v_c
    elif "Fahrenheit" in to_u:
        return v_c * 9.0/5.0 + 32.0
    elif "Kelvin" in to_u:
        return v_c + 273.15

def convert(category, from_unit, to_unit, value):
    try:
        value = float(value)
    except:
        return "❌ Please enter a valid number."

    if category == "temperature":
        c = temp_to_celsius(value, from_unit)
        out = celsius_to_target(c, to_unit)
    else:
        out = convert_linear(category, from_unit, to_unit, value)

    return f"{value} {from_unit} = {out:.6g} {to_unit}"

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Unit Converter", page_icon="🔁", layout="centered")

st.title("🔁 Unit Converter")
st.write("Convert between common units (length, mass, volume, time, speed, data, temperature).")

category = st.selectbox("Select Category", ALL_CATEGORIES, index=0)

if category == "temperature":
    units = TEMP_UNITS
else:
    units = list(LINEAR_UNITS[category].keys())

col1, col2 = st.columns(2)
with col1:
    from_unit = st.selectbox("From Unit", units)
with col2:
    to_unit = st.selectbox("To Unit", units, index=1 if len(units) > 1 else 0)

value = st.number_input("Enter Value", value=1.0, step=1.0)

if st.button("Convert"):
    result = convert(category, from_unit, to_unit, value)
    st.success(result)

st.markdown("---")
st.markdown("📌 **Examples**: 1 meter → kilometer, 2 lb → kg, 98.6 °F → °C")
