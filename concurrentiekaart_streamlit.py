import streamlit as st
import sys

if 'Nominatim' not in sys.modules:
    from geopy.geocoders import Nominatim
    import folium
    from folium.plugins import MarkerCluster
    import time
    from PIL import Image
    import glob

################################################################

def get_coords(geolocator, address=''):
    address = f'{address}, Nederland'
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f'Adres niet gevonden: {address}')
        # print(f'Adres niet gevonden: {address}')
        # return None, None

def create_folium_locations(inputs, icons):
    # base = {"name": "Location 1", "lat": 52.3387029, "lon": 4.9207297, "icon": icons['Albert Heijn']}
    progress_bar = st.progress(0, text='')
    percentage = 0
    increment = int(100/len(inputs))

    locations = []
    for adres, supermarkt in inputs:
        percentage += increment
        progress_bar.progress(percentage, text=f"{supermarkt} — {adres}")

        if adres:
            latitude, longitude = get_coords(geolocator, address=adres)
            locations.append(
                {"name": f"{supermarkt} {adres}",
                 "lat": latitude,
                 "lon": longitude,
                 "icon": icons[supermarkt],
                 "address": adres})

        time.sleep(1) # Minimaal 1 seconde. Geolocator loopt vast als er te veel requests te snel achter elkaar komen

    progress_bar.empty()
    return locations

def get_avg_coords(locations):
    latitudes = [loc['lat'] for loc in locations if loc['lat'] != None]
    longitudes = [loc['lon'] for loc in locations if loc['lat'] != None]

    avg_lat = sum(latitudes) / len(latitudes)
    avg_lon = sum(longitudes) / len(longitudes)

    return avg_lat, avg_lon

def add_map_markers(map_object, locations, icon_height=40):
    # MarkerCluster without chunked for prevesnting clustering
    marker_cluster = MarkerCluster(chunked=False).add_to(map_object)

    for loc in locations:
        with Image.open(loc['icon']) as img:
            orig_width, orig_height = img.size

        # Scale width to maintain aspect ratio
        aspect_ratio = orig_width / orig_height
        icon_width = int(icon_height * aspect_ratio)

        icon = folium.CustomIcon(loc["icon"], icon_size=(icon_width, icon_height))  # Larger icon size to prevent overlap

        marker = folium.Marker([loc["lat"], loc["lon"]], popup=loc["name"], icon=icon)

        marker.add_to(map_object)

################################################################

st.title("Concurrentiekaart")
placeholder_image = st.image('https://imgvisuals.com/cdn/shop/products/animated-world-map-with-pins-267288.gif?v=1698899562')

# Initialize lists to store inputs for supermarkets and addresses
supermarkten = []
adressen = []

# Supermarkticonen laden
icons = glob.glob('logo/*.png')
icons = {l.replace('.png', '').replace('logo/', '') : l for l in icons}

with st.sidebar:
    st.header('Inputs')
    base_map = "OpenStreetMap" # @param ["OpenStreetMap", "Stamen Toner", "Stamen Terrain", "Stamen Watercolor", "CartoDB Positron", "CartoDB Dark Matter", "Google", "CartoDB Positron No Labels", "CartoDB Dark Matter No Labels"]
    icon_height = st.slider('Icoongrootte (pixels)', 0, 200, 40)

    # Allow the user to select the number of input pairs
    n_inputs = st.slider('Aantal supermarkten', 1, 25, 3)

    for i in range(n_inputs):
        # Create columns for supermarket and address inputs
        c1, c2 = st.columns([2,3])
        with c1:
            supermarkt = st.selectbox(f"Supermarkt{i+1}", icons.keys(), key=f"supermarkt_{i}")
            supermarkten.append(supermarkt)

        with c2:
            adres = st.text_input(f"Adres{i+1}", placeholder='Typ adres hier', key=f"adres_{i}")
            adressen.append(adres)

    submitButton = st.button(label='Run')

if submitButton:
    placeholder_image.empty()

    with st.spinner('Bezig met kaart bouwen'):
        inputs = [(B, A) for A, B in zip(supermarkten, adressen)]

        # Create a geolocator object
        geolocator = Nominatim(user_agent="blablablabla")
        
        # Convert addresses to coordinates
        locations = create_folium_locations(inputs, icons)
        avg_lat, avg_lon = get_avg_coords(locations) # avg om het middelpunt van de kaart te berekenen

        # Initialize a map centered at a specific location
        my_map = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=15,
            tiles=base_map,
            attr="Map data &copy; OpenStreetMap contributors",
            zoom_control=True,
            options={
                'zoomSnap': 0,    # Allows fractional zoom levels
                'zoomDelta': 0.01  # Smaller zoom steps for smoother zooming
            }
        )

        # # Create a MarkerCluster
        # marker_cluster = MarkerCluster(chunked=False).add_to(my_map)

        # Add markers with manual spider behavior to prevent overlap
        add_map_markers(my_map, locations, icon_height=icon_height)

    # Show map
    map_html = my_map._repr_html_()
    st.components.v1.html(map_html, width=700, height=500)
