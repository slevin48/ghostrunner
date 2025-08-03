import streamlit as st
from streamlit_geolocation import streamlit_geolocation

st.logo("img/ghost.png")

location = streamlit_geolocation()
st.write(location)
