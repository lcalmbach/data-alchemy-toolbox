import streamlit as st
import pandas as pd
import os
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from datetime import datetime, date
import locale
import sqlite3

from tools.tool_base import ToolBase

SYSTEM_PROMPT_TEMPLATE = """you are a friendly assistant returning answers to the users questions about ht eopening ours of the different units of the administration. 
You need the information of time and administration-unit. If time information is missing, assume that the user is asking about the current time. If the administration-unit is missing, 
you must ask about the administration unit. the user may speak in german, english or french, your respond in the users language. Examples (current day and time is Friday: 11:00 am):
User: "ist das statistische Amt offen?"
Assistant: "Ja, das statistische Amt ist heute von 8:00 bis 12::00 und von 13:00 bis 16:00 offen."
User: "Ist das statistische Amt morgen vormittag offen?"
Assistant: "nein, am Samstag ist das statistische Amt den ganzen Tag geschlossen."
"""

locale.setlocale(locale.LC_TIME, 'de_DE')


class OpenHourse(ToolBase):
    def __init__(self, logger):
        super().__init__(logger)
        self.title = "Assistent für die Öffnungszeiten der kantonalen Verwaltung"
        self.formats = ["Demo"]
        self.model = "gpt-4"
        self.text = ""
        self.current_date = date.today()
        self.current_time = datetime.now().time()
        self.date = self.current_date
        self.time = self.current_time
        self.current_day_name = self.current_date.strftime("%A")
        self.current_day_id = self.current_date.weekday()

        self.script_name, script_extension = os.path.splitext(__file__)
        self.intro = self.get_intro()
        functions = [
            {
                "name": "get_opening_hours",
                "description": "get the opening hourse of a administration unit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "department": {
                            "type": "string",
                            "description": "The administration unit, e.g. Statistisches Amt",
                        },
                        "time": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The administration unit, e.g. Statistisches Amt",
                        },
                    },
                    "required": ["department", "format"],
                },
            },
        ]

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(self, messages, functions=None, function_call=None, model=GPT_MODEL):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + openai.api_key,
        }
        json_data = {"model": model, "messages": messages}
        if functions is not None:
            json_data.update({"functions": functions})
        if function_call is not None:
            json_data.update({"function_call": function_call})
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=json_data,
            )
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    def show_ui(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []


        if prompt := st.chat_input(
            "Stelle eine Frage zu den Öffnungszeiten der kantonalen Verwaltung"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = self.chat_completion_request(
                st.session_state.messages, functions=self.functions
            )
            st.session_state.messages.append({"role": "assistant", "content": response})

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
