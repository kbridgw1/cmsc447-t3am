import geopandas as gpd
import folium
import os
import geopandas as gpd
import pandas as pd
import json
from folium.features import GeoJson, GeoJsonTooltip

m = folium.Map(location=[39.045753,-76.641273], zoom_start=8, width='75%', height='70%')
ogeo = os.path.join('originalgeo.json')
cgeo = os.path.join('merge.geojson')
#percents = pd.read_csv(r"voterData/final_csv.csv")

folium.GeoJson(
    ogeo,
    name='geojson_o',
    style_function=lambda feature: {
        'fillColor': 'red' if feature['properties']['CNG02']==2401 or feature['properties']['CNG02']==2406 else 'blue',
        'color': 'red' if feature['properties']['CNG02']==2401 or feature['properties']['CNG02']==2406 else 'blue',
        'weight': 1,
        'fillOpacity': 0.4,
    }
).add_to(m)

tooltip = GeoJsonTooltip(
    fields=["Label", "dem", "rep"],
    aliases=["Congressional District: ", "Democrat Percentage: ", "Republican Percentage"],
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,
)

folium.GeoJson(
    cgeo,
    name='geojson_c',
    style_function=lambda feature: {
        'fillColor': '#0000000',
        'color': 'white',
        'weight': 2,
    },
    tooltip=tooltip
).add_to(m)

m.save("templates/originalgeo.html")




