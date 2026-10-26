
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load dataset
df = pd.read_csv("spacex_launch_dash.csv")

# Create Dash application
app = Dash(__name__)
app.title = "SpaceX Falcon 9 Launch Dashboard"

# Payload range
min_payload = int(df["Payload Mass (kg)"].min())
max_payload = int(df["Payload Mass (kg)"].max())

# Launch site options
site_options = [
    {"label": "All Sites", "value": "ALL"}
] + [
    {"label": site, "value": site}
    for site in sorted(df["Launch Site"].unique())
]

# Dashboard layout
app.layout = html.Div(
    style={
        "fontFamily": "Arial",
        "backgroundColor": "#f4f7fb",
        "padding": "25px",
        "minHeight": "100vh"
    },
    children=[
        html.H1(
            "SpaceX Falcon 9 Launch Records Dashboard",
            style={
                "textAlign": "center",
                "color": "#17365d"
            }
        ),

        html.P(
            "Interactive analysis of launch site performance, "
            "payload mass, and first-stage landing outcomes.",
            style={"textAlign": "center"}
        ),

        html.H3("Select Launch Site"),

        dcc.Dropdown(
            id="site-dropdown",
            options=site_options,
            value="ALL",
            clearable=False
        ),

        dcc.Graph(id="success-pie-chart"),

        html.H3("Select Payload Mass Range (kg)"),

        dcc.RangeSlider(
            id="payload-slider",
            min=min_payload,
            max=max_payload,
            step=100,
            value=[min_payload, max_payload],
            marks={
                min_payload: str(min_payload),
                max_payload: str(max_payload)
            },
            tooltip={"placement": "bottom"}
        ),

        dcc.Graph(id="success-payload-scatter-chart")
    ]
)


# Callback 1: Landing success pie chart
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def update_pie_chart(selected_site):

    if selected_site == "ALL":
        success_counts = (
            df[df["class"] == 1]
            .groupby("Launch Site")
            .size()
            .reset_index(name="Successful Landings")
        )

        fig = px.pie(
            success_counts,
            values="Successful Landings",
            names="Launch Site",
            title="Successful Landings by Launch Site"
        )

    else:
        filtered_df = df[df["Launch Site"] == selected_site]

        counts = (
            filtered_df["class"]
            .value_counts()
            .reindex([0, 1], fill_value=0)
            .reset_index()
        )

        counts.columns = ["Outcome", "Count"]
        counts["Outcome"] = counts["Outcome"].map({
            0: "Failure",
            1: "Success"
        })

        fig = px.pie(
            counts,
            values="Count",
            names="Outcome",
            title=f"Landing Outcomes at {selected_site}",
            color="Outcome",
            color_discrete_map={
                "Success": "#2ca02c",
                "Failure": "#d62728"
            }
        )

    fig.update_layout(template="plotly_white")
    return fig


# Callback 2: Payload versus landing outcome
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value")
)
def update_scatter_chart(selected_site, payload_range):

    filtered_df = df[
        (df["Payload Mass (kg)"] >= payload_range[0]) &
        (df["Payload Mass (kg)"] <= payload_range[1])
    ].copy()

    if selected_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == selected_site
        ]

    filtered_df["Landing Outcome"] = filtered_df["class"].map({
        0: "Failure",
        1: "Success"
    })

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        symbol="Landing Outcome",
        hover_data=["Launch Site", "Flight Number"],
        title="Payload Mass vs. Landing Outcome",
        labels={
            "class": "Landing Outcome (0 = Failure, 1 = Success)"
        }
    )

    fig.update_layout(template="plotly_white")
    return fig


if __name__ == "__main__":
    app.run(debug=True, port=8050)
