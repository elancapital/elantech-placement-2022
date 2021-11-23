import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.figure_factory as figure_factory
import pandas as pd
import pandas_datareader as pdr

# Load some data
total_vehicle_sales = pdr.get_data_fred('TOTALSA').loc['20190101':].reset_index().\
    rename(columns={'DATE': 'date', 'TOTALSA': 'total_vehicle_sales'})
retail_employees = pdr.get_data_fred('USTRADE').loc['20190101':].reset_index().\
    rename(columns={'DATE': 'date', 'USTRADE': 'retail_employees'})
crude_oil = pdr.get_data_yahoo('CL=F').loc['20190101':].reset_index().\
    rename(columns={'Date': 'date', 'Close': 'crude_oil'})
natural_gas = pdr.get_data_yahoo('NG=F').loc['20190101':].reset_index().\
    rename(columns={'Date': 'date', 'Close': 'natural_gas'})

# Correlate
merged = pd.merge(pd.merge(pd.merge(crude_oil, retail_employees, on='date'), total_vehicle_sales, on='date'),
                  natural_gas, on='date')[['date', 'crude_oil', 'natural_gas', 'total_vehicle_sales', 'retail_employees']]
corr = merged.corr()
fig = figure_factory.create_annotated_heatmap(corr.values, x=corr.index.tolist(), y=corr.index.tolist(),
                                              annotation_text=corr.values.tolist(),  colorscale='Viridis')

# Build visualisaton
app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(
            children="US Economy Dashboard",
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": total_vehicle_sales["date"],
                        "y": total_vehicle_sales["total_vehicle_sales"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Total Vehicle Sales"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": retail_employees["date"],
                        "y": retail_employees["retail_employees"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Retail Employees"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": crude_oil["date"],
                        "y": crude_oil["crude_oil"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Crude Oil"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": natural_gas["date"],
                        "y": natural_gas["natural_gas"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Natural Gas"},
            },
        ),
        dcc.Graph(
            figure=fig
        ),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in retail_employees.columns],
            data=retail_employees.to_dict('records'),
        )
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
