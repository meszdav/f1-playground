from src.chain import chain, TelemetryData
from src.visualization import plot_telemetry
import fastf1


prompt_input = input("What telemetry data do you want to plot?\n")

chain_result = chain.invoke({"query": prompt_input})

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

fig.show()
