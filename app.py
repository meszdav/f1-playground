from src.chain import TelemetryData, prompt, model_with_tools, model, parser
from src.visualization import plot_telemetry
from src.tools import get_gp_results, get_nth_driver
from langchain_core.messages import HumanMessage
import fastf1
import streamlit as st

st.set_page_config(layout="wide")
st.title("🏎️ F1 Telemetry Data Visualization")


def process_query(prompt_input):
    """Process a natural language query about F1 telemetry data.

    This function handles the two-step chain process:
    1. First, it sends the query to an LLM with tool-calling capabilities
    2. Then it executes any tool calls and sends the results back to a second LLM
       to generate structured telemetry data

    Args:
        prompt_input (str): The natural language query about F1 telemetry data

    Returns:
        dict: Structured data containing telemetry information that can be parsed
              into the TelemetryData class
    """
    chain_1 = prompt | model_with_tools
    ai_msg = chain_1.invoke({"query": prompt_input})

    messages = [HumanMessage(content=prompt_input)]

    for tool_call in ai_msg.tool_calls:
        selected_tool = {
            "get_gp_results": get_gp_results,
            "get_nth_driver": get_nth_driver,
        }[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)

    chain_2 = prompt | model | parser
    return chain_2.invoke(messages)


def display_telemetry(result):
    """
    Display telemetry data for a given Formula 1 session and drivers.
    This function retrieves telemetry data for a specified Formula 1 session
    and compares the performance of two drivers. The telemetry data is visualized
    using a Plotly chart embedded in a Streamlit application.
    Args:
        result (object): An object containing the following attributes:
            - year (int): The year of the Formula 1 season.
            - event (str): The name of the event (e.g., Grand Prix).
            - session (str): The session type (e.g., 'FP1', 'Qualifying', 'Race').
            - driver_1 (str): The code or name of the first driver.
            - driver_2 (str): The code or name of the second driver.
    Returns:
        None: The function renders the telemetry chart directly in the Streamlit app.
    """

    session = fastf1.get_session(result.year, result.event, result.session)
    session.load()

    fig = plot_telemetry(
        driver_1=result.driver_1,
        driver_2=result.driver_2,
        session=session,
        show_turns=True,
    )

    st.plotly_chart(fig, use_container_width=True)


prompt_input = st.text_input(
    "Enter your prompt here",
    value="Compare the telemetry data of Lewis Hamilton and Charles Leclerc in the 2023 Monaco GP.",
)

if st.button("Submit"):
    with st.spinner("Processing query..."):
        try:
            chain_result = process_query(prompt_input)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    with st.spinner("Analyzing telemetry data..."):
        try:
            result = TelemetryData(**chain_result)
            st.write(result)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    with st.spinner("Generating visualization..."):
        try:
            display_telemetry(result)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    st.success("Analysis complete!")
