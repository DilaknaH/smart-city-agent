import gradio as gr
import json
import os
from agent.city_agent import CityAgent
from simulation.simulator import run_simulation
from simulation.models import PolicyInput
from utils.visualizer import (
    create_comparison_chart,
    create_delta_indicators,
    create_radar_chart
)
from dotenv import load_dotenv

load_dotenv()

# --- Global agent instance ---
agent = CityAgent()

POLICY_MAP = {
    "🚌 Reduce Bus Fare": "reduce_bus_fare",
    "☀️ Increase Renewable Energy": "increase_renewable_energy",
    "🌳 Expand Green Spaces": "expand_green_spaces",
    "🚗 Implement Congestion Tax": "implement_congestion_tax",
    "🏠 Work From Home Policy": "work_from_home_policy"
}

# --- Chat function ---
def chat_with_agent(message, history):
    if not message.strip():
        return history, ""
    response = agent.run(message)
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    return history, ""

# --- Simulation function ---
def run_quick_simulation(policy_label, intensity):
    policy_type = POLICY_MAP[policy_label]
    policy = PolicyInput(
        policy_type=policy_type,
        change_value=intensity,
        description=f"{policy_label} at {intensity}% intensity"
    )
    before, after = run_simulation(policy)
    b, a = before.dict(), after.dict()

    # Store in agent memory
    agent.memory.add_simulation(policy_type, intensity, b, a)

    bar_chart = create_comparison_chart(b, a, policy_label)
    delta_chart = create_delta_indicators(b, a)
    radar_chart = create_radar_chart(b, a)

    # Build summary table
    changes = {k: round(a[k] - b[k], 2) for k in b}
    labels = {
        "avg_congestion_percent":           ("Congestion",            "%",     "↓ better"),
        "public_transport_usage_percent":   ("Transit Use",           "%",     "↑ better"),
        "avg_commute_time_minutes":         ("Commute Time",          "min",   "↓ better"),
        "renewable_percent":                ("Renewable Energy",      "%",     "↑ better"),
        "co2_emissions_tons_per_day":       ("CO2 Emissions",         "t/day", "↓ better"),
        "air_quality_index":                ("Air Quality Index",     "AQI",   "↓ better"),
        "avg_household_bill_usd":           ("Household Energy Bill", "$",     "↓ better"),
        "unemployment_percent":             ("Unemployment",          "%",     "↓ better"),
    }
    summary_rows = []
    for key, (name, unit, direction) in labels.items():
        delta = changes[key]
        arrow = "🟢" if (delta < 0 and "↓" in direction) or (delta > 0 and "↑" in direction) else "🔴"
        summary_rows.append([
            name,
            f"{b[key]:.1f} {unit}",
            f"{a[key]:.1f} {unit}",
            f"{delta:+.2f}",
            arrow
        ])

    return bar_chart, delta_chart, radar_chart, summary_rows

def reset_agent():
    agent.reset()
    return [], "✅ Agent memory cleared. Starting fresh."

# Gradio 6.12 uses message dicts natively — no tuple conversion needed

# --- Build Gradio UI ---
css = """
    .gradio-container { background: #0f1117; }
    h1 { color: #2ecc71 !important; text-align: center; }
    h3 { color: #3498db !important; }
"""

theme = gr.themes.Base(
    primary_hue="green",
    secondary_hue="blue",
    neutral_hue="slate"
)

with gr.Blocks(title="CityMind — AI Urban Policy Simulator") as demo:

    gr.Markdown("""
    # 🏙️ CityMind — AI Urban Policy Simulation Agent
    *An autonomous AI agent for smart city policy analysis | Powered by LangChain + Groq (LLaMA 3)*
    """)

    with gr.Tabs():

        # ── TAB 1: AI AGENT CHAT ──────────────────────────────────────
        with gr.Tab("🤖 Agent Chat"):
            gr.Markdown("### Chat with CityMind\nAsk about city status, suggest policies, compare scenarios.")

            chatbot = gr.Chatbot(
                value=[],
                height=420,
                label="CityMind Agent"
            )

            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="e.g. 'What happens if we cut bus fares by 60%?'",
                    label="Your Message",
                    scale=5
                )
                send_btn = gr.Button("Send ▶", variant="primary", scale=1)

            with gr.Row():
                reset_btn = gr.Button("🔄 Reset Memory", variant="secondary")
                reset_status = gr.Textbox(label="Status", interactive=False, scale=3)

            gr.Examples(
                examples=[
                    "What is the current state of the city?",
                    "What policies can I simulate?",
                    "Simulate reducing bus fares by 50%",
                    "What if we increase renewable energy to 70%?",
                    "Compare congestion tax vs work from home policy",
                    "Which policy gives the best CO2 reduction?"
                ],
                inputs=msg_input,
                label="💡 Try these prompts"
            )

            send_btn.click(
                fn=chat_with_agent,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            msg_input.submit(
                fn=chat_with_agent,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            reset_btn.click(
                fn=reset_agent,
                outputs=[chatbot, reset_status]
            )

        # ── TAB 2: QUICK SIMULATOR ────────────────────────────────────
        with gr.Tab("🎮 Quick Simulator"):
            gr.Markdown("### Visual Policy Simulator\nSelect a policy, set intensity, and instantly see predicted outcomes.")

            with gr.Row():
                with gr.Column(scale=1):
                    policy_dropdown = gr.Dropdown(
                        choices=list(POLICY_MAP.keys()),
                        value="🚌 Reduce Bus Fare",
                        label="Select Policy"
                    )
                    intensity_slider = gr.Slider(
                        minimum=10, maximum=100, value=50, step=10,
                        label="Policy Intensity (%)",
                        info="How aggressively to implement this policy"
                    )
                    simulate_btn = gr.Button("▶ Run Simulation", variant="primary")

                    gr.Markdown("""
                    **Policy Guide:**
                    - 🚌 Reduce Bus Fare → Boosts transit, cuts traffic
                    - ☀️ Renewables → Lowers CO2, slight cost rise
                    - 🌳 Green Spaces → Improves air quality
                    - 🚗 Congestion Tax → Major traffic reduction
                    - 🏠 WFH Policy → Cuts commuting drastically
                    """)

            delta_plot   = gr.Plot(label="Key Metric Changes")
            bar_plot     = gr.Plot(label="Before vs After Comparison")
            radar_plot   = gr.Plot(label="City Health Radar")

            summary_table = gr.Dataframe(
                headers=["Metric", "Before", "After", "Change", "Impact"],
                label="📋 Full Results Table",
                interactive=False
            )

            simulate_btn.click(
                fn=run_quick_simulation,
                inputs=[policy_dropdown, intensity_slider],
                outputs=[bar_plot, delta_plot, radar_plot, summary_table]
            )

        # ── TAB 3: ABOUT ──────────────────────────────────────────────
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ### About CityMind

            **CityMind** is an autonomous AI agent built to simulate how urban policy decisions
            affect a city's traffic, energy, and environmental systems.

            #### 🏗️ Architecture
            ```
            User (Gradio UI)
                    ↓
            CityMind Agent (LangChain + LangGraph ReAct Agent)
                    ↓
            Tool Calls: [simulate_policy | get_city_status | list_policies | compare_policies]
                    ↓
            Simulation Engine (rule-based models + Pydantic data)
                    ↓
            Visualizer (Plotly charts rendered in Gradio)
            ```

            #### 🔧 Tech Stack
            | Component | Technology |
            |---|---|
            | Agent Framework | LangChain + LangGraph |
            | LLM | Groq LLaMA 3 (8B) |
            | UI | Gradio on Hugging Face Spaces |
            | Visualization | Plotly |
            | Data Validation | Pydantic |
            | Memory | Custom SimulationMemory |

            #### 📋 Available Policies
            - 🚌 Reduce Bus Fare
            - ☀️ Increase Renewable Energy
            - 🌳 Expand Green Spaces
            - 🚗 Implement Congestion Tax
            - 🏠 Work From Home Policy

            ---
            *Assignment II — Data Science Applications and AI [LB3114]*
            """)

if __name__ == "__main__":
    demo.launch(
        theme=theme,
        css=css,
        share=False
    )
    