from src.chain import TelemetryData, prompt, model_with_tools, model, parser
from src.visualization import plot_telemetry
from src.tools import get_gp_results, get_nth_driver
from langchain_core.messages import HumanMessage
import fastf1
import streamlit as st

st.set_page_config(layout="wide")
st.title("🏎️ F1 Telemetry Data Visualization")


prompt_input = st.text_input(
    "Enter your prompt here",
    value="Compare the telemetry data of Lewis Hamilton and Charles Leclerc in the 2023 Monaco GP.",
)
if st.button("Submit"):

    with st.spinner("Processing..."):
        chain_1 = prompt | model_with_tools
        ai_msg = chain_1.invoke({"query": prompt_input})

        messages = [
            HumanMessage(content=prompt_input),
        ]

        for tool_call in ai_msg.tool_calls:
            selected_tool = {
                "get_gp_results": get_gp_results,
                "get_nth_driver": get_nth_driver,
            }[tool_call["name"].lower()]
            tool_msg = selected_tool.invoke(tool_call)
            messages.append(tool_msg)

        chain_2 = prompt | model | parser
        chain_result = chain_2.invoke(messages)

        print("Chain result:", chain_result)
        result = TelemetryData(**chain_result)


        session = fastf1.get_session(result.year, result.event, result.session)
        session.load()

        fig = plot_telemetry(
            driver_1=result.driver_1,
            driver_2=result.driver_2,
            session=session,
            show_turns=True,
        )

        st.plotly_chart(fig, use_container_width=True)