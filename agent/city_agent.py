import os
import traceback
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from agent.tools import simulate_policy, get_city_status, list_available_policies, compare_policies
from agent.memory import SimulationMemory
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are CityMind, an intelligent urban policy simulation agent.
You help city planners explore the impact of policy changes on traffic, energy, and pollution.

You have tools to:
1. Check current city status
2. List available policies
3. Simulate a policy and see before/after metrics
4. Compare two policies side by side

When a user proposes a policy:
- Understand their goal first
- Call the right tool
- Interpret results clearly in plain language
- Reference past simulations when relevant
- Highlight trade-offs honestly

Be analytical, concise, and helpful."""


class CityAgent:
    def __init__(self):
        self.memory = SimulationMemory()
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # updated model
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.tools = [
            simulate_policy,
            get_city_status,
            list_available_policies,
            compare_policies
        ]
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=SYSTEM_PROMPT
        )
        self.chat_history = []

    def run(self, user_input: str) -> str:
        try:
            history_context = self.memory.get_history_summary()
            full_input = user_input
            if history_context != "No simulations have been run yet.":
                full_input = f"{user_input}\n\n[Past simulations: {history_context}]"

            self.chat_history.append(HumanMessage(content=full_input))

            response = self.agent.invoke({
                "messages": self.chat_history
            })

            last_message = response["messages"][-1]
            reply = last_message.content
            self.chat_history.append(last_message)

            if len(self.chat_history) > 12:
                self.chat_history = self.chat_history[-12:]

            return reply

        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}"

    def reset(self):
        self.memory.clear()
        self.chat_history = []
        