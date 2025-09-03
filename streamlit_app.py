# app.py
# Unit Converter (Gradio) for Hugging Face Spaces
# Offline, no API keys required.

import os
import gradio as gr

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
    "data": {           # base: byte (binary multiples)
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
    if from_unit not in factors or to_unit not in factors:
        raise ValueError("Unsupported unit for selected category.")
    # Convert to base, then to target
    value_in_base = value * factors[from_unit]
    return value_in_base / factors[to_unit]

def temp_to_celsius(v: float, from_u: str) -> float:
    if "Celsius" in from_u:
        return v
    elif "Fahrenheit" in from_u:
        return (v - 32.0) * 5.0/9.0
    elif "Kelvin" in from_u:
        return v - 273.15
    else:
        raise ValueError("Unknown temperature unit.")

def celsius_to_target(v_c: float, to_u: str) -> float:
    if "Celsius" in to_u:
        return v_c
    elif "Fahrenheit" in to_u:
        return v_c * 9.0/5.0 + 32.0
    elif "Kelvin" in to_u:
        return v_c + 273.15
    else:
        raise ValueError("Unknown temperature unit.")

def convert(category, from_unit, to_unit, value):
    # Return string with result or error message
    try:
        value = float(value)
    except Exception:
        return "Please enter a valid numeric value."

    try:
        if category == "temperature":
            c = temp_to_celsius(value, from_unit)
            out = celsius_to_target(c, to_unit)
        else:
            out = convert_linear(category, from_unit, to_unit, value)

        # Format: show up to 6 significant digits (strip trailing zeros)
        def fmt(x):
            # use repr-like formatting but nicer
            s = f"{x:.6g}"
            return s

        return f"{fmt(value)} {from_unit} = {fmt(out)} {to_unit}"
    except Exception as e:
        return f"Error: {e}"

# ---------------------------
# UI helpers
# ---------------------------
def units_for_category(category: str):
    if category == "temperature":
        return TEMP_UNITS
    return list(LINEAR_UNITS[category].keys())

def on_category_change(category):
    units = units_for_category(category)
    default_from = units[0]
    default_to = units[1] if len(units) > 1 else units[0]
    # Return updates for two dropdowns (from_unit, to_unit)
    return (gr.update(choices=units, value=default_from),
            gr.update(choices=units, value=default_to))

# ---------------------------
# Build Gradio interface (Blocks)
# ---------------------------
with gr.Blocks(title="Unit Converter") as demo:
    gr.Markdown(
        "## 🔁 Unit Converter\n"
        "Convert between common units (length, mass, volume, time, speed, data, temperature). "
        "This app runs offline and requires no API keys."
    )

    with gr.Row():
        category = gr.Dropdown(choices=ALL_CATEGORIES, value="length", label="Category")
        from_unit = gr.Dropdown(choices=units_for_category("length"), value="meter (m)", label="From")
        to_unit = gr.Dropdown(choices=units_for_category("length"), value="kilometer (km)", label="To")

    value = gr.Number(value=1.0, label="Value", precision=6)
    with gr.Row():
        convert_btn = gr.Button("Convert", variant="primary")
        swap_btn = gr.Button("Swap ↔")

    output = gr.Textbox(label="Result", interactive=False)

    # Events
    category.change(fn=on_category_change, inputs=category, outputs=[from_unit, to_unit])

    def swap_units(from_u, to_u):
        return (gr.update(value=to_u), gr.update(value=from_u))

    swap_btn.click(fn=swap_units, inputs=[from_unit, to_unit], outputs=[from_unit, to_unit])
    convert_btn.click(fn=convert, inputs=[category, from_unit, to_unit, value], outputs=output)

    gr.Markdown(
        "### Examples\n"
        "- Length: 1 meter → kilometer\n"
        "- Mass: 2 pound → kilogram\n"
        "- Temperature: 98.6 °F → °C"
    )

# Run the app. On Hugging Face Spaces the PORT env var is provided.
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
