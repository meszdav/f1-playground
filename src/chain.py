from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_ollama.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from src.visualization import plot_telemetry
import fastf1
from dotenv import load_dotenv
from src.tools import get_most_recent_gp, get_results

load_dotenv()


class TelemetryData(BaseModel):
    driver_1: str = Field(description="The first driver's name.")
    driver_2: str = Field(description="The second driver's name.")
    event: str = Field(
        description="The name of the grand prix event, like 'Australian GP'."
    )
    year: int = Field(description="The year of the grand prix event.")
    session: str = Field(
        description="The session type, like 'Qualifying', 'Race', etc."
    )


with open("src/template.txt", "r") as file:
    template = file.read()

model = ChatOpenAI(model="gpt-4o")

parser = JsonOutputParser(pydantic_object=TelemetryData)


prompt = PromptTemplate(
    input_variables=["query"],
    template=template,
    partial_variables={
        "telemetry_data": parser.get_format_instructions(),
        "most_recent_gp": get_most_recent_gp(),
    },
)


chain = prompt | model | parser

