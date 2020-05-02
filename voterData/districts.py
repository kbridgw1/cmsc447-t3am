import plotly.express as px
import pandas as pd


def Map():
    df = pd.read_csv('final_csv.csv')

    geojson = 'congressional_districts.json'

    fig = px.choropleth_mapbox(df, geojson=geojson, color="color",
                               locations="c_district", featureidkey="properties.id",
                               center={"lat": 39.045753, "lon": -76.641273},
                               mapbox_style="carto-positron", zoom=7)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig
