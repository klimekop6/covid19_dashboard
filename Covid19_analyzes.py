import pyodbc
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
import time

from config import UID, PWD, SERVER


class DataBaseConnection:
    def __init__(self) -> None:
        self.cnxn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.cnxn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={SERVER};"
                f"DATABASE=PandemiaCov19;"
                f"UID={UID};"
                f"PWD={PWD}",
                timeout=3,
            )
            self.cursor = self.cnxn.cursor()
            return self.cursor
        except pyodbc.OperationalError:
            pass

    def __exit__(self, exc_type, exc_value, exc_tracebac):
        self.cnxn.commit()
        self.cnxn.close()


available_countries = []
with DataBaseConnection() as cursor:
    cursor.execute("""SELECT ID_Country, iso_code, location FROM Dim_country""")
    available_countries.extend(cursor.fetchall()[1:])

col_names_dim_country = []
with DataBaseConnection() as cursor:
    cursor.execute(
        f"""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Dim_country'"""
    )
    col_names_dim_country.extend(cursor.fetchall())
col_names_dim_country = sorted([ele[0] for ele in col_names_dim_country])
col_names_dim_country.remove("ID_Country")
col_names_dim_country.remove("iso_code")

available_informations = sorted(
    [
        "new_deaths",
        "new_deaths_per_milion",
        "total_deaths",
        "total_deaths_per_milion",
        "new_cases",
        "new_cases_per_million",
        "total_cases",
        "total_cases_per_million",
        "new_tests",
        "new_tests_per_thousand",
        "total_tests",
        "total_tests_per_thousand",
    ]
)
available_informations_second_component = sorted(
    [
        "total_deaths",
        "total_deaths_per_milion",
        "total_cases",
        "total_cases_per_million",
        "total_tests",
        "total_tests_per_thousand",
    ]
)

# dcc -> dash core components https://dash.plotly.com/dash-core-components
# pltotly.express -> https://plotly.com/python/


app = Dash(__name__)

# ========================================================================
# App layout
app.layout = html.Div(
    [
        html.H1(
            "Make your own analyzes and statistics for Covid19",
            style={"text-align": "center"},
        ),
        html.Br(),
        # H3 'Select countries'
        html.Div(
            [html.H3("Select countries", style={"text-align": "center"})],
            style={"display": "inline-block", "left": "0%", "width": "50%"},
        ),
        # H3 'Select information to analyze'
        html.Div(
            [
                html.H3(
                    "Select information to analyze", style={"text-align": "center"}
                ),
            ],
            style={"display": "inline-block", "left": "50%", "width": "50%"},
        ),
        html.Br(),
        # Dropdown slct_country
        html.Div(
            html.Div(
                [
                    dcc.Dropdown(
                        id="slct_country",
                        options=[
                            {"label": location, "value": id_country}
                            for id_country, _, location in available_countries
                        ],
                        multi=True,
                        value=(38, 52, 71, 158, 201),
                        clearable=False,
                        style={"width": "600px"},
                        placeholder="Select country",
                    )
                ],
                style={
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "width": "100%",
                },
            ),
            style={"display": "inline-block", "left": "0%", "width": "50%"},
        ),
        # Dropdown slct_info
        html.Div(
            html.Div(
                [
                    dcc.Dropdown(
                        id="slct_info",
                        options=[
                            {
                                "label": information.replace("_", " ").capitalize(),
                                "value": information,
                            }
                            for information in available_informations
                        ],
                        multi=True,
                        value=("new_cases_per_million", "new_deaths_per_milion"),
                        clearable=False,
                        style={"width": "600px"},
                        placeholder="Select information",
                    )
                ],
                style={
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "width": "100%",
                },
            ),
            style={"display": "inline-block", "left": "50%", "width": "50%"},
        ),
        html.Br(),
        dcc.Graph(id="first_graphs"),
        # ========================================================================
        # H3 'Select countries'
        html.Div(
            [html.H3("Select countries", style={"text-align": "center"})],
            style={"left": "0%", "width": "100%"},
        ),
        # Dropdown slct_country2
        html.Div(
            html.Div(
                [
                    dcc.Dropdown(
                        id="slct_country2",
                        options=[
                            {"label": location, "value": id_country}
                            for id_country, _, location in available_countries
                        ],
                        multi=True,
                        value=(38, 52, 71, 158, 201),
                        clearable=False,
                        style={"width": "600px"},
                        placeholder="Select country",
                    )
                ],
                style={
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "width": "100%",
                },
            ),
            style={"display": "inline-block", "left": "0%", "width": "100%"},
        ),
        # Button slct_all_countries
        dcc.Checklist(
            id="slct_all_countries",
            options=[{"label": "Select all countries", "value": "select_all"}],
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "width": "100%",
                "margin-top": "5px",
            },
        ),
        # H3 'Select information to analyze' left
        html.Div(
            [html.H3("Select information to analyze", style={"text-align": "center"})],
            style={"display": "inline-block", "left": "0%", "width": "50%"},
        ),
        # H3 'Select information to analyze' right
        html.Div(
            [
                html.H3(
                    "Select information to analyze", style={"text-align": "center"}
                ),
            ],
            style={"display": "inline-block", "left": "50%", "width": "50%"},
        ),
        # Dropdown slct_info_from_dim_country
        html.Div(
            html.Div(
                [
                    dcc.Dropdown(
                        id="slct_info_from_dim_country",
                        options=[
                            {
                                "label": info.replace("_", " ").capitalize(),
                                "value": info,
                            }
                            for info in col_names_dim_country
                        ],
                        multi=True,
                        clearable=False,
                        style={"width": "600px"},
                        placeholder="Select information",
                    )
                ],
                style={
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "width": "100%",
                },
            ),
            style={"display": "inline-block", "left": "0%", "width": "50%"},
        ),
        # Dropdown slct_info2
        html.Div(
            html.Div(
                [
                    dcc.Dropdown(
                        id="slct_info2",
                        options=[
                            {
                                "label": information.replace("_", " ").capitalize(),
                                "value": information,
                            }
                            for information in available_informations_second_component
                        ],
                        multi=True,
                        clearable=False,
                        style={"width": "600px"},
                        placeholder="Select information",
                    )
                ],
                style={
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "width": "100%",
                },
            ),
            style={"display": "inline-block", "left": "50%", "width": "50%"},
        ),
        html.Br(),
        dcc.Graph(id="second_graph"),
    ]
)

# ========================================================================
# Connect the Plotly graphs with Dash Components


@app.callback(
    [Output(component_id="first_graphs", component_property="figure")],
    [
        Input(component_id="slct_country", component_property="value"),
        Input(component_id="slct_info", component_property="value"),
    ],
)
def update_graph(option_slctd, info_slctd):

    if not all((option_slctd, info_slctd)):
        raise PreventUpdate

    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE=PandemiaCov19;"
        f"UID={UID};"
        f"PWD={PWD};"
    )

    df = pd.read_sql_query(
        f"""
        SELECT Dim_time.Date, 
        Dim_country.iso_code, Dim_country.location,
        Deaths.new_deaths, Deaths.total_deaths, Deaths.new_deaths_per_milion, Deaths.total_deaths_per_milion, 
        Cases.new_cases, Cases.total_cases, Cases.new_cases_per_million, Cases.total_cases_per_million,
        Tests.new_tests, Tests.total_tests, Tests.new_tests_per_thousand, Tests.total_tests_per_thousand,
        Dim_country.hospital_beds_per_thousand, Dim_country.population_density

        FROM Dim_time INNER JOIN Deaths ON Deaths.ID_Date=Dim_time.ID_Date
                    INNER JOIN Cases ON Cases.ID_Date=Dim_time.ID_Date
                    INNER JOIN Tests ON Tests.ID_Date=Dim_time.ID_Date
                    INNER JOIN Dim_country ON Deaths.ID_Country=Dim_country.ID_Country 
                                            AND Tests.ID_Country=Dim_country.ID_Country 
                                            AND Cases.ID_Country=Dim_country.ID_Country 

        WHERE Dim_country.ID_Country IN ({', '.join(str(id) for id in option_slctd)})
        ORDER BY Dim_time.Date, Dim_country.ID_Country
        """,
        con=conn,
        parse_dates={"Dim_time.Date": {"format": "%Y/%m/%d"}},
        index_col="Date",
    )

    # ========================================================================

    countries = []
    for id_country, iso_code, location in available_countries:
        for index, slctd_id in enumerate(option_slctd):
            if id_country == slctd_id:
                countries.append({"iso_code": iso_code, "location": location})
                option_slctd[index] = f"{location}"
    option_slctd.sort()

    # Set date
    start_date = "20200101"
    current_date = time.strftime("%Y%m%d", time.localtime())
    df = df[df.index > pd.to_datetime(start_date, format="%Y/%m/%d")]
    df = df[df.index < pd.to_datetime(current_date, format="%Y/%m/%d")]

    # Columns to proceed
    columns_names_to_use = info_slctd

    avg_30 = []
    for col_name in columns_names_to_use:
        avg_30.append(df.groupby("location").rolling(7, min_periods=0)[col_name].mean())
        df = df.drop(columns=col_name)

    df = df.reset_index()
    for ele in avg_30:
        df = pd.merge(df, ele.reset_index(), on=["location", "Date"])
    df = df.set_index("Date")

    # ========================================================================

    px_figures = []
    fig = make_subplots(
        rows=len(columns_names_to_use),
        cols=1,
        subplot_titles=tuple(
            col_name.replace("_", " ").capitalize() for col_name in columns_names_to_use
        ),
        vertical_spacing=0.2 / len(columns_names_to_use),
    )
    for idx, col_name in enumerate(columns_names_to_use, start=1):
        px_figures.append(
            px.line(
                df,
                x=df.index,
                y=col_name,
                color="location",
                title=col_name.replace("_", " ").capitalize(),
            )
        )

    for idx, px_figure in enumerate(px_figures, start=1):

        px_figure.for_each_trace(lambda t: t.update(legendgroup=idx))

        for trace in range(len(px_figure["data"])):
            fig.add_trace(trace=px_figure["data"][trace], row=idx, col=1)

        dict_yaxes = px_figure["layout"]["yaxis"]["title"]
        for key in dict_yaxes:
            if key == "standoff":
                if idx == 1:
                    fig["layout"]["yaxis"]["title"] = (
                        dict_yaxes["text"].replace("_", " ").capitalize()
                    )
                else:
                    fig["layout"][f"yaxis{idx}"]["title"] = (
                        dict_yaxes["text"].replace("_", " ").capitalize()
                    )

    fig.update_yaxes(title_font={"size": 16}, title_standoff=25)
    if len(columns_names_to_use) == 1:
        height = 500
    else:
        height = len(columns_names_to_use) * 500 - 180
    fig.update_layout(
        title_x=0.5,
        height=height,
        legend_traceorder="grouped",
        legend_tracegroupgap=round(
            height / len(columns_names_to_use)
            - 0.05 / len(columns_names_to_use) * height
            - len(countries) * 18
        ),
        legend_groupclick="toggleitem",
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return (fig,)


@app.callback(
    [
        Output(component_id="second_graph", component_property="figure"),
        Output(component_id="slct_country2", component_property="disabled"),
    ],
    [
        Input(component_id="slct_country2", component_property="value"),
        Input(component_id="slct_all_countries", component_property="value"),
        Input(component_id="slct_info_from_dim_country", component_property="value"),
        Input(component_id="slct_info2", component_property="value"),
    ],
)
def update_graph2(countries_slctd, all_countries_slctd, info_xaxes, info_yaxes):

    if not all((countries_slctd, info_xaxes, info_yaxes)):
        raise PreventUpdate

    info_xaxes = info_xaxes[0]
    info_yaxes = info_yaxes[0]

    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE=PandemiaCov19;"
        f"UID={UID};"
        f"PWD={PWD};"
    )

    if all_countries_slctd:
        countries_slctd = [id_country for id_country, _, _ in available_countries]

    df = pd.read_sql_query(
        f"""
        SELECT Dim_time.Date,
            Dim_country.iso_code,
            Deaths.total_deaths, Deaths.total_deaths_per_milion, 
            Cases.total_cases, Cases.total_cases_per_million,
            Tests.total_tests, Tests.total_tests_per_thousand

        FROM Dim_time INNER JOIN Deaths ON Deaths.ID_Date=Dim_time.ID_Date
                        INNER JOIN Cases ON Cases.ID_Date=Dim_time.ID_Date
                        INNER JOIN Tests ON Tests.ID_Date=Dim_time.ID_Date
                        INNER JOIN Dim_country ON Deaths.ID_Country=Dim_country.ID_Country 
                                                AND Tests.ID_Country=Dim_country.ID_Country 
                                                AND Cases.ID_Country=Dim_country.ID_Country 

        WHERE Dim_time.Date = convert(varchar, getdate()-2, 112) AND
                Dim_country.ID_Country IN ({', '.join(str(id) for id in countries_slctd)})
        """,
        con=conn,
        parse_dates={"Dim_time.Date": {"format": "%Y/%m/%d"}},
    )

    df_Dim_country = pd.read_sql_query(
        f"""
        SELECT * FROM Dim_country
        WHERE ID_Country IN ({', '.join(str(id) for id in countries_slctd)})
        """,
        con=conn,
    )

    df = df.merge(df_Dim_country, on="iso_code")
    df = df.drop(columns=["iso_code", "ID_Country"])

    # ========================================================================

    countries = []
    for id_country, iso_code, location in available_countries:
        for slctd_id in countries_slctd:
            if id_country == slctd_id:
                countries.append({"iso_code": iso_code, "location": location})

    xaxes_title = info_xaxes.replace("_", " ").capitalize()
    yaxes_title = info_yaxes.replace("_", " ").capitalize()
    fig = px.scatter(
        df,
        x=df[info_xaxes],
        y=df[info_yaxes],
        color="location",
        title=f"{xaxes_title} VS {yaxes_title}",
        trendline="ols",
        trendline_scope="overall",
    )
    fig.update_layout(title_x=0.5, plot_bgcolor="white", legend_title_text="Country")
    fig.update_xaxes(
        title=xaxes_title,
        title_font={"size": 16},
        title_standoff=25,
    )
    fig.update_yaxes(
        title=yaxes_title,
        title_font={"size": 16},
        title_standoff=25,
    )
    fig.update_traces(marker_size=16)

    # ========================================================================

    if all_countries_slctd:
        return fig, True

    return fig, False


# ========================================================================
if __name__ == "__main__":
    app.run_server("192.168.0.116", 55554, debug=True, use_reloader=False)
