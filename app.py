import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.figure_factory as figure_factory
import pandas as pd
import pandas_datareader as pdr
import plotly.graph_objs as go

# Load data
total_vehicle_sales = pdr.get_data_fred('TOTALSA').loc['20190101':].reset_index().\
    rename(columns={'DATE': 'date', 'TOTALSA': 'total_vehicle_sales'})
retail_employees = pdr.get_data_fred('USTRADE').loc['20190101':].reset_index().\
    rename(columns={'DATE': 'date', 'USTRADE': 'retail_employees'})
crude_oil = pdr.get_data_yahoo('CL=F').loc['20190101':].reset_index().\
    rename(columns={'Date': 'date', 'Close': 'crude_oil'})
natural_gas = pdr.get_data_yahoo('NG=F').loc['20190101':].reset_index().\
    rename(columns={'Date': 'date', 'Close': 'natural_gas'})
covid_cases_world = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv") # Source: ourworldindata.org
covid_cases_US = covid_cases_world.loc[covid_cases_world['iso_code'] == 'USA']
consumer_confidence_level_US = pd.read_csv("CCL_USA.csv").\
    rename(columns={'TIME': 'date', 'Value': 'consumer_confidence_level'}) # Source: oecd.org
business_confidence_level = pd.read_csv("business_confidence_index.csv").\
    rename(columns={'TIME': 'date', 'Value': 'business_confidence_level'}) # Source: oecd.org
consumer_confidence_level_US['date'] = consumer_confidence_level_US['date'].astype('datetime64[ns]')
business_confidence_level['date'] = business_confidence_level['date'].astype('datetime64[ns]')
# Figures
# Daily crude oil and natural gas prices
trace_crude_oil = go.Scatter(
    x=crude_oil["date"],
    y=crude_oil["crude_oil"],
    name='Daily Crude Oil Price in $'
)
trace_natural_gas = go.Scatter(
    x=natural_gas["date"],
    y=natural_gas["natural_gas"],
    name='Daily Natural Gas Price in $',
    yaxis='y2'
)
fig_crude_oil_natural_gas = {
    'data': [
        trace_crude_oil, trace_natural_gas
    ],
    'layout': go.Layout(
        title='Daily crude oil and natural gas prices',
        yaxis=dict(
            title='Crude oil',
            titlefont=dict(color='#1f77b4'),
        ),
        yaxis2=dict(
            title='Natural gas',
            titlefont=dict(color='#ff7f0e'),
            overlaying='y',
            side='right'
        )
    )
}
# Consumer confidence level and vehicle sales and retail employees
trace_consumer_confidence = go.Scatter(
    x=consumer_confidence_level_US["date"][60::],
    y=consumer_confidence_level_US["consumer_confidence_level"][60::],
    name='Consumer Confidence Level USA'
)
trace_vehicle_sales = go.Scatter(
    x=total_vehicle_sales["date"],
    y=total_vehicle_sales["total_vehicle_sales"],
    name='Total Vehicle Sales',
    yaxis='y2'
)
trace_retail_employees = go.Scatter(
    x=retail_employees["date"],
    y=retail_employees["retail_employees"],
    name='Daily Retail Employees',
    yaxis='y3'
)
fig_consumer_confidence_vehicle_sales = {
    'data': [
        trace_consumer_confidence, trace_vehicle_sales, trace_retail_employees
    ],
    'layout': go.Layout(
        title='Vehicle sales and consumer confidence',
        yaxis=dict(
            title='Consumer confidence level',
            titlefont=dict(color='#1f77b4'),
        ),
        yaxis2=dict(
            title='Total Vehicle Sales',
            titlefont=dict(color='#ff7f0e'),
            overlaying='y',
            side='right'
        ),
        yaxis3=dict(
            title='Daily Retail Employees',
            # titlefont=dict(color='#ff7f0e'),
            overlaying='y',
            side='right'
        )
    ),
}
merged_vehicles_employees = pd.merge(total_vehicle_sales, retail_employees, on='date')[['date','total_vehicle_sales', 'retail_employees',]]
merged_confidence_levels = pd.merge(consumer_confidence_level_US, business_confidence_level, on='date')[['date','consumer_confidence_level', 'business_confidence_level',]]
merged_confidence_vehicle_employee = pd.merge(pd.merge(pd.merge(consumer_confidence_level_US, business_confidence_level, on='date'),total_vehicle_sales, how='right', on='date'), retail_employees, how='right', on='date')[['date','consumer_confidence_level', 'business_confidence_level','total_vehicle_sales', 'retail_employees',]]
corr_vehicles_employees = merged_confidence_vehicle_employee.corr()
fig_heatmap_vehicles_employees = figure_factory.create_annotated_heatmap(
    corr_vehicles_employees.values,
    x=corr_vehicles_employees.index.tolist(),
    y=corr_vehicles_employees.index.tolist(),
    annotation_text=corr_vehicles_employees.values.tolist(),
    colorscale='tealgrn_r'
)
# Business confidence level and covid-19 cases
trace_business_confidence = go.Scatter(
    x=business_confidence_level["date"][144::],
    y=business_confidence_level["business_confidence_level"][144::],
    name='Business Confidence Level USA'
)
trace_covid19_cases = go.Scatter(
    x=covid_cases_US["date"],
    y=covid_cases_US["new_cases"],
    name='Covid-19 cases USA',
    yaxis='y2'
)
fig_business_confidence_covid19 = {
    'data': [
        trace_business_confidence, trace_covid19_cases
    ],
    'layout': go.Layout(
        title='Business confidence and covid19',
        yaxis=dict(
            title='Business confidence level',
            titlefont=dict(color='#1f77b4'),
        ),
        yaxis2=dict(
            title='Covid',
            titlefont=dict(color='#ff7f0e'),
            overlaying='y',
            side='right'
        )
    ),
}
# Heatmap
merged = pd.merge(pd.merge(pd.merge(crude_oil, retail_employees, on='date'), total_vehicle_sales, on='date'),
                  natural_gas, on='date')[['date','crude_oil', 'natural_gas', 'total_vehicle_sales', 'retail_employees',]]
corr = merged.corr()
fig_heatmap = figure_factory.create_annotated_heatmap(corr.values, x=corr.index.tolist(), y=corr.index.tolist(),
                                              annotation_text=corr.values.tolist(),  colorscale='tealgrn_r')
# Covid Cases US
fig_covid_cases_US = {
    "data": [
        {
            "x": covid_cases_US["date"],
            "y": covid_cases_US["new_cases"],
            "type": "lines",
        },
    ],
    "layout": {"title": "Daily New Covid-19 Cases USA"},
}

# Build visualisaton
app = dash.Dash(__name__)
# Colors
colors = {
    'background': '#e04848',
    'text': '#1f77b4'
}
# App layout
app.layout = html.Div(
    children=[
        # Heading
        html.H1(
            "US indicators Dashboard",
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        # Subheading
        html.Div(
            "How did the economy react to the covid-19 pandemic",
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        # Graphs
        dcc.Graph(
            figure=fig_crude_oil_natural_gas
        ),
        dcc.Graph(
            figure=fig_consumer_confidence_vehicle_sales
        ),
        dcc.Graph(
            figure=fig_heatmap_vehicles_employees
        ),
        dcc.Graph(
            figure=fig_business_confidence_covid19
        ),
        dcc.Graph(
            figure=fig_heatmap
        ),
        dcc.Graph(
            figure=fig_covid_cases_US
        ),
        # Table
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in retail_employees.columns],
            data=retail_employees.to_dict('records'),
            style_cell={'textAlign': 'left'},
            style_data=dict(backgroundColor="AntiqueWhite")
        )
    ]
)

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8080, debug=True)
