import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_comparison_chart(before: dict, after: dict, policy_name: str):
    metrics_config = [
        ("Congestion (%)", "avg_congestion_percent", "lower"),
        ("Transit Use (%)", "public_transport_usage_percent", "higher"),
        ("Renewables (%)", "renewable_percent", "higher"),
        ("CO2 (×100 t/day)", "co2_emissions_tons_per_day", "lower"),
        ("Air Quality Index", "air_quality_index", "lower"),
        ("Energy Bill ($)", "avg_household_bill_usd", "lower"),
    ]

    labels, before_vals, after_vals, bar_colors = [], [], [], []

    for label, key, direction in metrics_config:
        b = before.get(key, 0)
        a = after.get(key, 0)
        if key == "co2_emissions_tons_per_day":
            b, a = b / 100, a / 100
        labels.append(label)
        before_vals.append(round(b, 1))
        after_vals.append(round(a, 1))
        improved = (a < b) if direction == "lower" else (a > b)
        bar_colors.append("#2ecc71" if improved else "#e74c3c")

    fig = go.Figure(data=[
        go.Bar(name="Before", x=labels, y=before_vals,
               marker_color="#3498db", opacity=0.85),
        go.Bar(name="After", x=labels, y=after_vals,
               marker_color=bar_colors, opacity=0.9)
    ])
    fig.update_layout(
        title=f"📊 Impact of: {policy_name}",
        barmode="group",
        plot_bgcolor="#0f1117",
        paper_bgcolor="#161b22",
        font=dict(color="white", size=13),
        legend=dict(bgcolor="#1a1a2e", font=dict(color="white")),
        height=420,
        margin=dict(t=50, b=40)
    )
    return fig

def create_delta_indicators(before: dict, after: dict):
    fig = make_subplots(
        rows=1, cols=4,
        specs=[[{"type": "indicator"}] * 4]
    )
    indicators = [
        ("CO2 Emissions", "co2_emissions_tons_per_day", "tons/day", "lower"),
        ("Air Quality", "air_quality_index", "AQI", "lower"),
        ("Congestion", "avg_congestion_percent", "%", "lower"),
        ("Transit Use", "public_transport_usage_percent", "%", "higher"),
    ]
    for i, (title, key, unit, direction) in enumerate(indicators, 1):
        b, a = before[key], after[key]
        improved = (a < b) if direction == "lower" else (a > b)
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=a,
            delta={"reference": b, "valueformat": ".1f",
                   "increasing": {"color": "#e74c3c" if direction == "lower" else "#2ecc71"},
                   "decreasing": {"color": "#2ecc71" if direction == "lower" else "#e74c3c"}},
            title={"text": f"{title}<br><span style='font-size:0.8em'>({unit})</span>",
                   "font": {"color": "white", "size": 14}},
            number={"font": {"color": "#2ecc71" if improved else "#e74c3c", "size": 28}}
        ), row=1, col=i)

    fig.update_layout(
        paper_bgcolor="#161b22",
        height=180,
        margin=dict(t=30, b=10)
    )
    return fig

def create_radar_chart(before: dict, after: dict):
    """Radar chart for overall city health comparison"""
    categories = ["Transit Use", "Renewables", "Air Quality\n(inverted)",
                  "Low Congestion", "Low CO2"]

    def normalize(val, min_v, max_v):
        return (val - min_v) / (max_v - min_v) * 100

    before_scores = [
        before["public_transport_usage_percent"],
        before["renewable_percent"],
        100 - normalize(before["air_quality_index"], 10, 200),
        100 - before["avg_congestion_percent"],
        100 - normalize(before["co2_emissions_tons_per_day"], 500, 10000),
    ]
    after_scores = [
        after["public_transport_usage_percent"],
        after["renewable_percent"],
        100 - normalize(after["air_quality_index"], 10, 200),
        100 - after["avg_congestion_percent"],
        100 - normalize(after["co2_emissions_tons_per_day"], 500, 10000),
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=before_scores + [before_scores[0]],
        theta=categories + [categories[0]],
        fill="toself", name="Before",
        line_color="#3498db", fillcolor="rgba(52,152,219,0.2)"
    ))
    fig.add_trace(go.Scatterpolar(
        r=after_scores + [after_scores[0]],
        theta=categories + [categories[0]],
        fill="toself", name="After",
        line_color="#2ecc71", fillcolor="rgba(46,204,113,0.2)"
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#0f1117",
            radialaxis=dict(visible=True, range=[0, 100], color="white"),
            angularaxis=dict(color="white")
        ),
        paper_bgcolor="#161b22",
        font=dict(color="white"),
        legend=dict(bgcolor="#1a1a2e"),
        height=350,
        title=dict(text="🕸️ City Health Radar", font=dict(color="white"))
    )
    return fig
    