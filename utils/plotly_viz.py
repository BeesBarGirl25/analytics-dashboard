import plotly.graph_objects as go

def plot_metrics_plotly(xg_data, goal_data):
    """Generate a responsive Plotly visualization with adjusted layout."""
    
    # Ensure data is fully decoded into Python-native types
    xg_data = xg_data.applymap(lambda x: x.tolist() if hasattr(x, 'tolist') else x)
    goal_data = goal_data.applymap(lambda x: x.tolist() if hasattr(x, 'tolist') else x)

    fig = go.Figure()

    # Add Cumulative xG lines
    for team in xg_data['Team'].unique():
        team_data = xg_data[xg_data['Team'] == team]
        fig.add_trace(go.Scatter(
            x=team_data['minutes'].tolist(),  # Convert to Python list
            y=team_data['Cumulative xG'].tolist(),  # Convert to Python list
            mode='lines',
            name=f"{team} - Cumulative xG",
            line=dict(width=2, dash='dot')
        ))

    # Add Goal Total lines
    for team in goal_data['Team'].unique():
        team_data = goal_data[goal_data['Team'] == team]
        fig.add_trace(go.Scatter(
            x=team_data['minutes'].tolist(),  # Convert to Python list
            y=team_data['Total Goals'].tolist(),  # Convert to Python list
            mode='lines',
            name=f"{team} - Goal Total",
            line=dict(width=2)
        ))

    # Determine the maximum minutes for the x-axis
    max_minutes = max(xg_data['minutes'].max(), goal_data['minutes'].max())

    # Add shaded regions for extra time and penalties
    shapes = []
    annotations = []
    if max_minutes > 90:
        shapes.append({
            'type': 'rect',
            'x0': 90,
            'x1': min(120, max_minutes),
            'y0': 0,
            'y1': 1,
            'xref': 'x',
            'yref': 'paper',
            'fillcolor': 'rgba(255, 223, 186, 0.4)',
            'line': {'width': 0}
        })
        annotations.append({
            'x': 105,
            'y': 0.5,
            'xref': 'x',
            'yref': 'paper',
            'text': 'Extra Time',
            'showarrow': False,
            'font': dict(size=12, color='rgb(255, 165, 0)'),
            'textangle': 270,
            'align': 'center'
        })
    if max_minutes > 120:
        shapes.append({
            'type': 'rect',
            'x0': 120,
            'x1': max_minutes,
            'y0': 0,
            'y1': 1,
            'xref': 'x',
            'yref': 'paper',
            'fillcolor': 'rgba(255, 99, 71, 0.4)',
            'line': {'width': 0}
        })
        annotations.append({
            'x': (120 + max_minutes) / 2,
            'y': 0.5,
            'xref': 'x',
            'yref': 'paper',
            'text': 'Penalties',
            'showarrow': False,
            'font': dict(size=12, color='rgb(255, 69, 0)'),
            'textangle': 270,
            'align': 'center'
        })

    # Add the shapes and annotations to the layout
    fig.update_layout(
        autosize=True,  # Enable dynamic resizing
        margin=dict(l=10, r=10, t=50, b=10),  # Add some padding around the graph
        template="plotly_white",
        xaxis=dict(title="Minutes", automargin=True),
        yaxis=dict(title="Goals", automargin=True),
        title=dict(
            text="Cumulative xG and Goal Totals Over Time",
            x=0.5,  # Center-align the title
            y=0.95,  # Ensure title fits near the top
            xanchor='center',
            yanchor='top',
            font=dict(size=18)  # Keep font size manageable
        ),
        shapes=shapes,  # Add the defined shaded regions
        annotations=annotations  # Add the annotations
    )

    return fig
