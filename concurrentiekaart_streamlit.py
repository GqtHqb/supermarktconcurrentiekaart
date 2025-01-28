import streamlit as st

import sys

if 'Nominatim' not in sys.modules:
    from geopy.geocoders import Nominatim
    import folium
    from folium.plugins import MarkerCluster
    import time
    from tqdm.notebook import tqdm

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

    locations = []
    pbar = tqdm(inputs)
    for adres, supermarkt in pbar:
        if adres:
            pbar.set_postfix_str(f"   {supermarkt} — {adres}")

            latitude, longitude = get_coords(geolocator, address=adres)
            locations.append(
                {"name": f"{supermarkt} {adres}",
                 "lat": latitude,
                 "lon": longitude,
                 "icon": icons[supermarkt],
                 "address": adres})

        time.sleep(1)

    return locations

def get_avg_coords(locations):
    latitudes = [loc['lat'] for loc in locations if loc['lat'] != None]
    longitudes = [loc['lon'] for loc in locations if loc['lat'] != None]

    avg_lat = sum(latitudes) / len(latitudes)
    avg_lon = sum(longitudes) / len(longitudes)

    return avg_lat, avg_lon

def add_markers_with_spider_behavior(map_object, locations):
    # MarkerCluster without chunked for prevesnting clustering
    marker_cluster = MarkerCluster(chunked=False).add_to(map_object)

    previous_marker = None
    for loc in locations:
        icon = folium.CustomIcon(loc["icon"], icon_size=(icon_size, icon_size))  # Larger icon size to prevent overlap
        marker = folium.Marker([loc["lat"], loc["lon"]], popup=loc["name"], icon=icon)

        # If there's a previous marker, adjust its position slightly to avoid overlap
        if previous_marker:
            dx = (loc["lat"] - previous_marker.location[0]) * 0.00001  # Adjust this value based on zoom level
            dy = (loc["lon"] - previous_marker.location[1]) * 0.00001
            marker = folium.Marker([loc["lat"] + dy, loc["lon"] + dx], popup=loc["name"], icon=icon)

        previous_marker = marker
        marker.add_to(map_object)


icons = {
    'Albert Heijn': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Albert_Heijn_Logo.svg/1146px-Albert_Heijn_Logo.svg.png',
    'AH to go': 'https://www.spotschiphol.nl/uploads/news/ahtogo.jpg',
    'AH XL': 'https://scontent.fgrq1-2.fna.fbcdn.net/v/t39.30808-6/472503317_1253180036259348_3998234187461474481_n.jpg?_nc_cat=104&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=7neLdFgA5vIQ7kNvgGMocV6&_nc_zt=23&_nc_ht=scontent.fgrq1-2.fna&_nc_gid=ATQPhvojBqhsHp2jPXBHswM&oh=00_AYD1y4lLV2JvvXuysaMnL5vcEzoXKs8-mgtT3LRYbhaypw&oe=6792E670',
    'Boni': 'https://www.nijkerkerveen.org/wp-content/uploads/2017/03/boni_logo-a900x525-900x500.jpg',
    "Boon's Markt": 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Boon%27s_Markt_logo_%282015%29.png',
    "Boon's Dagmarkt": 'https://www.lunchbestelling.nl/wp-content/uploads/2021/05/logo-boons-dagmarkt.png',
    "Boon's Pitstop": 'https://boonspitstop.nl/wp-content/uploads/2020/04/logo_boons_pitstop_DEF-1090x800.png',
    'Buurtsuper': 'https://buurtsuper.eu/wp-content/uploads/2021/07/buurtsuper-logo.png',
    'Coop': 'https://www.thuiswinkel.org/Images/Logo/b70a0187-8dff-48c0-868d-724d64f590d2',
    'Dagwinkel': 'https://upload.wikimedia.org/wikipedia/commons/a/aa/Dagwinkellogo.jpg',
    'Dekamarkt': 'https://www.superunie.nl/app/uploads/2019/07/Logo-DekaMarkt-520x220.jpg',
    'Dirk van den Broek': 'https://www.plein53.nl/web/images/uploads/Winkels/winkel-dirk.jpg',
    'Jan Linders': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Jan_Linders_logo.jpg/1599px-Jan_Linders_logo.jpg',
    'Jumbo Foodmarkt': 'https://upload.wikimedia.org/wikipedia/commons/1/14/Jumbo_Foodmarkt_logo.png',
    'Jumbo': 'https://cdn2.downdetector.com/static/uploads/logo/Jumbo_Logo.png',
    'Lidl': 'https://upload.wikimedia.org/wikipedia/commons/9/91/Lidl-Logo.svg',
    'PLUS': 'https://scontent.fgrq1-2.fna.fbcdn.net/v/t39.30808-6/469635361_967205828775212_6443443294096100524_n.jpg?_nc_cat=1&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=hCO0HFtKmRUQ7kNvgF3qTWM&_nc_zt=23&_nc_ht=scontent.fgrq1-2.fna&_nc_gid=AdD_ZVWN0C_ik1RI-YI0mq8&oh=00_AYDgmKSl312yxGvNQQBwnxrBMB9cos5sWeWo8etwzLDEkw&oe=67930617',
    'MCD': 'https://mcdstavenisse.nl/wp-content/uploads/2021/11/MCDsupermarkt.png',
    'Nettorama': 'https://static.wikia.nocookie.net/logopedia/images/9/91/Nettorama_2010.jpg/revision/latest?cb=20140709190822',
    'Poiesz': 'https://www.superunie.nl/app/uploads/2019/09/07-poiesz_groot-457x280.jpg',
    'SPAR express': 'https://upload.wikimedia.org/wikipedia/de/thumb/e/e9/Logo_SPAR_express.jpg/1597px-Logo_SPAR_express.jpg?20131126225751',
    'SPAR': 'https://www.spar.nl/data/uploads/media/Spar%20logo%20rond.300dpi.png',
    'Vomar': 'https://upload.wikimedia.org/wikipedia/commons/1/16/Vomar-logo.jpg'
}
st.title("Concurrentiekaart")

base_map = "OpenStreetMap" # @param ["OpenStreetMap", "Stamen Toner", "Stamen Terrain", "Stamen Watercolor", "CartoDB Positron", "CartoDB Dark Matter", "Google", "CartoDB Positron No Labels", "CartoDB Dark Matter No Labels"]
icon_size = st.slider('Icoongrootte', 0, 200, 50)

# Allow the user to select the number of input pairs
n_inputs = st.slider('Aantal supermarkten', 1, 20, 5)

# Initialize lists to store inputs for supermarkets and addresses
supermarkten = []
adressen = []

with st.form(key='columns_in_form'):
    for i in range(n_inputs):
        # Create columns for supermarket and address inputs
        c1, c2 = st.columns(2)
        with c1:
            supermarkt = st.selectbox(f"Supermarkt{i+1}", icons.keys(), key=f"supermarkt_{i}")
            supermarkten.append(supermarkt)

        with c2:
            adres = st.text_input(f"Adres{i+1}", placeholder='Typ adres hier', key=f"adres_{i}")
            adressen.append(adres)

    submitButton = st.form_submit_button(label='Run')

# # Optionally, you can display the selected values after the form is submitted
# if submitButton:
#     st.write("Selected Supermarkts:", supermarkts)
#     st.write("Selected Adresses:", adresses)

if submitButton:
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
    add_markers_with_spider_behavior(my_map, locations)

    # Show map
    # my_map 
    map_html = my_map._repr_html_()
    st.components.v1.html(map_html, width=700, height=500)


