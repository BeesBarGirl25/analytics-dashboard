import plotly.graph_objects as go
from utils.analytics_by_team import cumulative_stats
from flask import current_app

def generate_match_graph(match_data):
    match_data = match_data[['team', 'minute', 'shot_outcome', 'shot_statsbomb_xg', 'period']]

    # Separate stats for Team 1 and Team 2
    team_1 = match_data[match_data['team'] == match_data['team'].unique()[0]]
    team_2 = match_data[match_data['team'] == match_data['team'].unique()[1]]

    team_1_stats = cumulative_stats(team_1)
    team_2_stats = cumulative_stats(team_2)

    # Extract team names dynamically
    team_1_name = team_1_stats['team'].iloc[0]
    team_2_name = team_2_stats['team'].iloc[0]

    # Dynamically determine max y-axis value
    y_max = max(team_1_stats['cum_xg'].max(), team_1_stats['cum_goals'].max(),
                team_2_stats['cum_xg'].max(), team_2_stats['cum_goals'].max())

    x_max = max(team_1_stats['minute'].max(), team_2_stats['minute'].max())

    # Create the Plotly figure
    fig = go.Figure()

    # Add Team 1 traces
    fig.add_trace(go.Scatter(
        x=team_1_stats['minute'],
        y=team_1_stats['cum_xg'],
        mode='lines',
        name=f'{team_1_name} Cumulative xG',
        line=dict(color='red', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=team_1_stats['minute'],
        y=team_1_stats['cum_goals'],
        mode='lines',
        name=f'{team_1_name} Goals',
        line=dict(color='red')
    ))

    # Add Team 2 traces
    fig.add_trace(go.Scatter(
        x=team_2_stats['minute'],
        y=team_2_stats['cum_xg'],
        mode='lines',
        name=f'{team_2_name} Cumulative xG',
        line=dict(color='blue', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=team_2_stats['minute'],
        y=team_2_stats['cum_goals'],
        mode='lines',
        name=f'{team_2_name} Goals',
        line=dict(color='blue')
    ))

    unique_periods = match_data['period'].unique()

    # Check for data in extra time (90–120 mins) and add shaded box
    if not set(unique_periods).issubset({1, 2}):
        fig.add_shape(
            type="rect",
            x0=90, x1=x_max, y0=0, y1=y_max + 0.5,
            fillcolor="rgba(0, 255, 0, 0.2)",  # Semi-transparent green fill
            line=dict(color="rgba(0, 255, 0, 0)")  # No border line
        )
        fig.add_annotation(
            x=(90 + x_max)/2, y=y_max + 0.5,  # Centered text at the top of the box
            text="Extra Time",
            showarrow=False,
            font=dict(color="green", size=12)
        )

    # Check for data in penalties (120+ mins) and add shaded box
    if (match_data['period'].max() == 5):
        fig.add_shape(
            type="rect",
            x0=120, x1=match_data['minute'].max(), y0=0, y1=y_max + 0.5,
            fillcolor="rgba(255, 0, 0, 0.2)",  # Semi-transparent red fill
            line=dict(color="rgba(255, 0, 0, 0)")  # No border line
        )
        fig.add_annotation(
            x=(120 + match_data['minute'].max()) / 2, y=y_max + 0.5,
            text="Penalties",
            showarrow=False,
            font=dict(color="red", size=12)
        )

    # Customize layout
    fig.update_layout(
        title='Interactive Goals and xG Comparison',
        xaxis_title='Minutes',
        yaxis_title='Goals',
        legend_title='Legend',
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent plot area
        paper_bgcolor="rgba(0, 0, 0, 0)"  # Transparent entire graph background
    )

    return fig

