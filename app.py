import streamlit as st
import requests
from datetime import datetime


'''
# TaxiFareModel front Javier
'''

st.markdown('''
Remember that there are several ways to output content into your web page...

Either as with the title by just creating a string (or an f-string). Or as with this paragraph using the `st.` functions
''')

'''
## Here we would like to add some controllers in order to ask the user to select the parameters of the ride

1. Let's ask for:
- date and time
- pickup longitude
- pickup latitude
- dropoff longitude
- dropoff latitude
- passenger count
'''

'''
## Once we have these, let's call our API in order to retrieve a prediction




See ? No need to load a `model.joblib` file in this app, we do not even need to know anything about Data Science in order to retrieve a prediction...

🤔 How could we call our API ? Off course... The `requests` package 💡
'''




# 1. Inputs
pickup_date = st.date_input("Pickup date", value=datetime.today())
pickup_time = st.time_input("Pickup time", value=datetime.now().time())
pickup_datetime = f"{pickup_date} {pickup_time}"

col1, col2 = st.columns(2)

with col1:
    pickup_longitude = st.number_input("Pickup longitude", value=-73.950655)
    pickup_latitude = st.number_input("Pickup latitude", value=40.783282)

with col2:
    dropoff_longitude = st.number_input("Dropoff longitude", value=-73.984365)
    dropoff_latitude = st.number_input("Dropoff latitude", value=40.769802)

passenger_count = st.number_input("Passenger count", min_value=1, max_value=8, value=1)

# 2. Map
import pandas as pd

map_data = pd.DataFrame({
    "lat": [pickup_latitude, dropoff_latitude],
    "lon": [pickup_longitude, dropoff_longitude]
})
st.map(map_data)

# 3. API call
url = 'https://taxifare.lewagon.ai/predict'

params = {
    "pickup_datetime": pickup_datetime,
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}

if st.button("Get fare prediction 🚀"):
    response = requests.get(url, params=params)
    st.write("Request URL:", response.url)  # debug
    prediction = response.json()["fare"]
    st.markdown(f"## Predicted fare: **${prediction:.2f}**")



'''

2. Let's build a dictionary containing the parameters for our API...

3. Let's call our API using the `requests` package...

4. Let's retrieve the prediction from the **JSON** returned by the API...

## Finally, we can display the prediction to the user
'''
