import folium
import os


from folium.features import GeoJson, GeoJsonTooltip


m = folium.Map(location=[39.045753,-76.641273], zoom_start=8, width='65%', height='65%')
ogeo = os.path.join('originalgeo.json')
cgeo = os.path.join('voterData/congressional_districts.json')

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

folium.GeoJson(
    cgeo,
    name='geojson_c',
    style_function=lambda feature: {
        'fillColor': '#0000000',
        'color': 'white',
        'weight': 2,
    }
).add_to(m)

m.save("templates/originalgeo.html")




