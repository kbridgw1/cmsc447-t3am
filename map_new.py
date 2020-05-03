import folium
import os

def Map():
    m = folium.Map(location=[39.045753,-76.641273], zoom_start=8, width='65%', height='65%')
    cgeo = os.path.join('voterData/congressional_districts.json')

    folium.GeoJson(cgeo, name='precincts').add_to(m)


    m.save("templates/index.html")
    return m


