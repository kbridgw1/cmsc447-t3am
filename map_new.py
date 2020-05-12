"""
@author: Kristina Bridgwater

This program creates the folium map of the current (democratic) distribution
"""
import geopandas as gpd
import folium
import os
import geopandas as gpd
import pandas as pd
import json
from folium.features import GeoJson, GeoJsonTooltip

# create the map
m = folium.Map(location=[39.045753,-76.641273], zoom_start=8, width='75%', height='70%')
# define the geojson data for the precincts
ogeo = os.path.join('originalgeo.json')
# define the geojson data for the districts
cgeo = os.path.join('merge.geojson')

# add the precinct layer to the map, color the precincts red or blue according to district
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

# define the tooltip function
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

# add the district layer to the map with the appropirate outlines
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

# save the map as an html
m.save("templates/originalgeo.html")




