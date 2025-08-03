import streamlit as st
from streamlit_geolocation import streamlit_geolocation

st.logo("img/ghost.png")

st.title("Ghostrunner 👻")

st.write("🔽 Click to display location")

location = streamlit_geolocation()
if location and location["latitude"] and location["longitude"]:
    st.map({
        "lat": [location["latitude"]],
        "lon": [location["longitude"]]
    })
