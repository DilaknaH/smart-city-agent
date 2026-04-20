# CityMind — AI Urban Policy Simulation Agent

An autonomous AI agent that simulates how urban policy decisions affect a city's traffic, energy, and environmental systems.

## Live Demo
👉 [Try it on Hugging Face Spaces](https://huggingface.co/spaces/DilaknaGodagamage/smart-city-agent)

## Features
- **AI Chat Agent** — Ask questions about city status and policy impacts
- **Policy Simulator** — Visualize before/after metrics for 5 urban policies
- **Charts & Analytics** — Bar charts, radar charts, delta indicators via Plotly

## Tech Stack
| Component | Technology |
|---|---|
| Agent Framework | LangChain + LangGraph |
| LLM | Groq LLaMA 3 (8B) |
| UI | Gradio |
| Visualization | Plotly |
| Data Validation | Pydantic |

## Policies Simulated
- 🚌 Reduce Bus Fare
- ☀️ Increase Renewable Energy
- 🌳 Expand Green Spaces
- 🚗 Implement Congestion Tax
- 🏠 Work From Home Policy

## Architecture
```
User (Gradio UI) → CityMind Agent (LangChain + LangGraph ReAct)
→ Tool Calls → Simulation Engine → Plotly Visualizer
```

## Author
 Dilakna Godagamage

Undergradute| KDU
