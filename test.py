import enum
import openai
from openai_functions import Conversation
from dataclasses import dataclass
import openai
from openai_functions import nlp
from openai_functions import FunctionWrapper
from openai_functions import BasicFunctionSet

openai.api_key = "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"

conversation = Conversation()


class Unit(enum.Enum):
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"


skill = BasicFunctionSet()


class Unit(enum.Enum):
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"


@skill.add_function
def get_current_weather(location: str, unit: Unit = Unit.FAHRENHEIT) -> dict:
    """Get the current weather in a given location.

    Args:
        location (str): The city and state, e.g., San Francisco, CA
        unit (Unit): The unit to use, e.g., fahrenheit or celsius
    """
    return {
        "location": location,
        "temperature": "72",
        "unit": unit.value,
        "forecast": ["sunny", "windy"],
    }


@skill.add_function
def set_weather(location: str, weather_description: str):
    ...


schema = skill.functions_schema
print(schema)

weather = skill(
    {"name": "get_current_weather", "arguments": '{"location": "San Francisco, CA"}'}
)
