import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from fastf1.core import Session
import plotly.graph_objects as go
import fastf1.plotting
from fastf1 import utils
import pandas as pd

pio.templates.default = "plotly_dark"


def get_fastest_lap(driver: str, session: Session) -> pd.DataFrame:
    """Retrieves telemetry data for a specific driver during a session.

    Args:
        driver: The driver's name.
        session: The session object containing telemetry data.

    Returns:
        A DataFrame containing the driver's telemetry data.
    """

    fastest_lap = session.laps.pick_drivers(driver).pick_fastest()
    telemetry_data = fastest_lap.get_car_data().add_distance()
    return telemetry_data


def get_team_color(driver: str, session: Session) -> str:
    """Retrieves the team color for a specific driver during a session.

    Args:
        driver: The driver's name.
        session: The session object containing telemetry data.

    Returns:
        The team's color in RGB format.
    """

    driver = session.get_driver(driver)
    team = driver["TeamName"]
    return fastf1.plotting.get_team_color(team, session=session)


def _invert_hex_color(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    inverted = "".join(f"{255 - int(hex_color[i:i+2], 16):02X}" for i in (0, 2, 4))
    return f"#{inverted}"


def _get_available_turns(telemetry_data: pd.DataFrame, session: Session) -> list[int]:
    """Retrieves the available turns for a specific telemetry data during a session.

    Args:
        telemetry_data: The telemetry data DataFrame.
        session: The session object containing telemetry data.

    Returns:
        A list of available turns.
    """

    circuit = session.get_circuit_info().corners
    turns = circuit.query(
        f"Distance >= {telemetry_data['Distance'].min()} and Distance <= {telemetry_data['Distance'].max()}"
    )
    return turns["Number"].tolist()


def plot_telemetry(
    driver_1: str,
    driver_2: str,
    session: Session,
    show_turns: bool = False,
    start_dist: int = None,
    end_dist: int = None,
) -> go.Figure:
    """Plots telemetry data for two drivers during a session.

    Args:
        driver_1: The first driver's name.
        driver_2: The second driver's name.
        session: The session object containing telemetry data.
        show_turns: Whether to display turn markers on the plot.
        start_dist: Starting distance for the plot in meters.
        end_dist: Ending distance for the plot in meters.

    Returns:
        A plotly figure object with the telemetry data.
    """

    fig = make_subplots(
        rows=3,
        cols=1,
        vertical_spacing=0.02,
        shared_xaxes=True,
    )

    driver_1_full_name = session.get_driver(driver_1)["FullName"]
    driver_2_full_name = session.get_driver(driver_2)["FullName"]

    physical_values = ["Speed", "Throttle", "Brake"]

    driver_1_color = get_team_color(driver_1, session)
    driver_2_color = get_team_color(driver_2, session)

    if driver_1_color == driver_2_color:
        driver_2_color = _invert_hex_color(driver_2_color)

    traces = []

    telemetry_data_1 = get_fastest_lap(driver_1, session)
    telemetry_data_2 = get_fastest_lap(driver_2, session)

    if all([start_dist, end_dist]):
        telemetry_data_1 = telemetry_data_1.query(
            f"Distance.between({start_dist}, {end_dist})"
        ).copy()
        telemetry_data_2 = telemetry_data_2.query(
            f"Distance.between({start_dist}, {end_dist})"
        ).copy()

    for i, value in enumerate(physical_values):

        traces.append(
            go.Scatter(
                x=telemetry_data_1["Distance"],
                y=telemetry_data_1[value],
                mode="lines",
                name=driver_1,
                line=dict(color=driver_1_color),
                showlegend=False,
            )
        )

        traces.append(
            go.Scatter(
                x=telemetry_data_2["Distance"],
                y=telemetry_data_2[value],
                mode="lines",
                name=driver_2,
                line=dict(color=driver_2_color),
                showlegend=False,
            )
        )

    fig.add_traces(traces, rows=[1, 1, 2, 2, 3, 3], cols=[1, 1, 1, 1, 1, 1])

    fig.update_xaxes(title_text="Distance (m)", row=3, col=1)
    fig.update_yaxes(title_text="Speed (km/h)", row=1, col=1)
    fig.update_yaxes(title_text="Throttle (%)", row=2, col=1)
    fig.update_yaxes(title_text="Brake (on/off)", row=3, col=1)

    event_date = session.event["EventDate"].date().strftime("%Y-%m-%d")
    event_name = session.event["EventName"]
    event_type = session.session_info["Type"]

    title = (
        f"{event_date} | {event_name} - {event_type}<br>"
        f"{driver_1_full_name} vs {driver_2_full_name} Telemetry"
        "\n\n"
    )

    fig.update_layout(title=title, height=800)

    if show_turns:
        available_turns = _get_available_turns(telemetry_data_1, session)
        fig = add_turns(fig, session, available_turns=available_turns)

    return fig


def add_turns(
    fig: go.Figure, session: Session, available_turns: list[int] = None
) -> go.Figure:
    """Adds turn markers to the telemetry plot.

    Args:
        fig: The Plotly figure object.
        session: The session object containing telemetry data.
        available_turns: A list of turn numbers to plot.

    Returns:
        The updated Plotly figure with turn markers added.
    """

    turns = session.get_circuit_info().corners

    rows, cols = fig._get_subplot_rows_columns()
    for row in rows:
        for col in cols:
            for _, turn in turns.iterrows():
                turn_number = turn["Number"]
                if turn_number in available_turns:
                    fig.add_vline(
                        x=turn["Distance"],
                        line=dict(color="gray", width=1, dash="dash"),
                        row=row,
                        col=col,
                        annotation=dict(
                            text=f"Turn {turn_number}",
                            font=dict(color="#CDCDCD"),
                            showarrow=True,
                            ax=0,
                            ay=-30,
                        ),
                    )
    return fig


def plot_turn(
    driver_1: str,
    driver_2: str,
    turn_number: int,
    session: Session,
    show_turns: bool = False,
) -> go.Figure:
    """Plots telemetry data for a specific turn during a session.

    Args:
        driver_1: The first driver's name.
        driver_2: The second driver's name.
        turn_number: The turn number to plot.
        session: The session object containing telemetry data.
        show_turns: Whether to display turn markers on the plot.

    Returns:
        A plotly figure object focusing on the specified turn.
    """

    circuit = session.get_circuit_info().corners

    turn = circuit.query(f"Number == {turn_number}").iloc[0]["Distance"]

    start_distance = turn - 500
    end_distance = turn + 500

    fig = plot_telemetry(
        driver_1,
        driver_2,
        session,
        show_turns=show_turns,
        start_dist=start_distance,
        end_dist=end_distance,
    )

    return fig
