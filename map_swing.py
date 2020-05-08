"""
@author: Kristina Bridgwater

This program is the same as map_new.py but for the swing distribution map
"""
import folium
import os
from folium.features import GeoJson, GeoJsonTooltip

m = folium.Map(location=[39.045753,-76.641273], zoom_start=8, width='75%', height='70%')
ogeo = os.path.join('swinggeo.json')
cgeo = os.path.join('swingmerge.geojson')

folium.GeoJson(
    ogeo,
    name='geojson_o',
    style_function=lambda feature: {
        'fillColor': 'red' if feature['properties']['CNG02']==5 or feature['properties']['CNG02']==6 or feature['properties']['CNG02']==7 or feature['properties']['CNG02']==8 else 'blue',
        'color': 'red' if feature['properties']['CNG02']==5 or feature['properties']['CNG02']==6 or feature['properties']['CNG02']==7 or feature['properties']['CNG02']==8 else 'blue',
        'weight': 1,
        'fillOpacity': 0.4,
    }
).add_to(m)

tooltip = GeoJsonTooltip(
    fields=["cd", "dem", "rep"],
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

m.save("templates/swinggeo.html")