import dash_core_components as dcc
import dash
import dash_html_components as html
import pandas as pd
import time
import plotly.express as px

app = dash.Dash(__name__)
server = app.server

daterange = pd.date_range(start='2020-01-01',end='2021-12-31',freq='D')
df = pd.read_csv("bike_sharing_daily_data.csv")
df['date'] = pd.to_datetime(df['date'],format="%Y-%m-%d")

def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')

def getMarks(start, end, Nth=40):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''

    result = {}
    for i, date in enumerate(daterange):
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result

app.layout = html.Div([
    dcc.RangeSlider(
                id='my-range-slider',
                min = unixTimeMillis(daterange.min()),
                max = unixTimeMillis(daterange.max()),
                value = [unixTimeMillis(daterange.min()),
                         unixTimeMillis(daterange.max())],
                marks=getMarks(daterange.min(),
                            daterange.max())
            ),
    html.H3(id='output-container-range-slider'),
    dcc.Graph(id='bikeshare-trends-overall'),
    dcc.Graph(id='bikeshare-trends-weather'),
    dcc.Graph(id='bikeshare-trends-weekday-user')
])


@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('my-range-slider', 'value')])
def update_output(value):
    left_date = unixToDatetime(value[0])
    right_date = unixToDatetime(value[1])
    left_date = f"{left_date.date().year} - {left_date.date().month} - {left_date.date().day}"
    right_date = f"{right_date.date().year} - {right_date.date().month} - {right_date.date().day}"
    return f"BikeshareBetween : {left_date} and {right_date}"


@app.callback(
    dash.dependencies.Output('bikeshare-trends-overall','figure'),
    dash.dependencies.Input('my-range-slider', 'value')
)
def update_bikeshare_overall(value):
    left_range = unixToDatetime(value[0])
    right_range = unixToDatetime(value[1])
    filtered_df = df[df['date'] >= left_range]
    filtered_df = filtered_df[filtered_df['date'] <= right_range]
    return px.line(filtered_df,x='date',y='trips',title="Bikeshare trends overall")

@app.callback(
    dash.dependencies.Output('bikeshare-trends-weather','figure'),
    dash.dependencies.Input('my-range-slider', 'value')
)
def update_bikeshare_weather(value):
    left_range = unixToDatetime(value[0])
    right_range = unixToDatetime(value[1])
    filtered_df = df[df['date'] >= left_range]
    filtered_df = filtered_df[filtered_df['date'] <= right_range]
    filtered_df = filtered_df.groupby('weather').sum()['trips'].reset_index()
    return px.bar(filtered_df,x='weather',y='trips',title="Weather impact on bikeshare")

@app.callback(
    dash.dependencies.Output('bikeshare-trends-weekday-user','figure'),
    dash.dependencies.Input('my-range-slider', 'value')
)
def update_bikeshare_weekday_user(value):
    left_range = unixToDatetime(value[0])
    right_range = unixToDatetime(value[1])
    filtered_df = df[df['date'] >= left_range]
    filtered_df = filtered_df[filtered_df['date'] <= right_range]
    filtered_df = filtered_df.groupby('weekday').sum()[['casual','registered']].reset_index()
    return px.bar(filtered_df,x='weekday',y=['casual','registered'],title="Bikeshare user type per weekday")

    

if __name__ == '__main__':
    app.run_server(debug=True)