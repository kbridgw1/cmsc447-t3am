import folium
import os
import pandas as pd
import geopandas as gpd
import branca
import json
import requests

from folium.features import GeoJson, GeoJsonTooltip

def Map():
    m = folium.Map(location=[39.045753,-76.641273], zoom_start=8, width='65%', height='65%')
    cgeo = os.path.join('originalgeo.json')
    #districts = 'voterData/final_csv.csv'
    #disctrict_data = pd.read_csv(districts)
    #bins = list(dem_percent['dem'].quantile([0, 0.25, 0.5, 0.75, 1]))

    folium.GeoJson(
        cgeo,
        name='geojson'
    ).add_to(m)

    m.save("templates/index.html")
    return m


