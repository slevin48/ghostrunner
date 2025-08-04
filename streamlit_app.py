import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from stravalib import Client

st.logo("img/ghost.png")

st.title("Ghostrunner 👻")

#
# 1) Load your secrets
#
CLIENT_ID     = st.secrets["strava"]["client_id"]
CLIENT_SECRET = st.secrets["strava"]["client_secret"]
REDIRECT_URI  = st.secrets["strava"]["redirect_uri"].rstrip("/")
SCOPES = ["read", "activity:read"]

#
# 2) Instantiate Stravalib client
#
client = Client()

#
# 3) If we already did the dance, reuse the token
#
if "strava_token" in st.session_state:
    client.access_token = st.session_state.strava_token

else:
    # 4a) Step 1: send the user off to Strava for approval
    if "code" not in st.query_params:
        auth_url = client.authorization_url(
            client_id=CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            approval_prompt="auto",
            scope=SCOPES
        )
        st.link_button("🔗 Connect your Strava account 👟", auth_url, type="primary")
        st.stop()

    # 4b) Step 2: Strava redirected back with ?code=… → exchange for token
    code = st.query_params["code"]
    token_response = client.exchange_code_for_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=code
    )
    # token_response is a dict with access_token, refresh_token, expires_at, etc.
    access_token = token_response["access_token"]
    client.access_token = access_token
    st.session_state.strava_token = access_token
    st.toast("🎉 Connected to Strava!")

#
# 5) Now you can call any Strava endpoint via client
#
athlete = client.get_athlete()
# st.json(athlete)
with st.sidebar:
    st.header("Your Strava Profile 👤")
    st.write(f"Welcome, {athlete.firstname}! 👋")
    st.image(athlete.profile, width=50)
st.write("🔽 Click to display location")
location = streamlit_geolocation()
if location and location["latitude"] and location["longitude"]:
    st.map({
        "lat": [location["latitude"]],
        "lon": [location["longitude"]]
    })
