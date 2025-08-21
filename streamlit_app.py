import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from stravalib import Client
from numbers import Number

st.logo("img/ghost.png")

st.title("Ghostrunner 👻")

# ————— Helpers —————
def get_seconds(dur):
    """Return total seconds from timedelta, numeric, or digit-string."""
    # 1) real timedelta
    if hasattr(dur, "total_seconds"):
        return int(dur.total_seconds())
    # 2) numeric (int or float)
    if isinstance(dur, Number):
        return int(dur)
    # 3) string of digits
    s = str(dur)
    if s.isdigit():
        return int(s)
    # Unexpected type
    raise ValueError(f"Can't parse duration: {dur!r}")

def format_duration(secs: int) -> str:
    hrs, rem = divmod(secs, 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs}:{mins:02d}:{secs:02d}"

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
    st.query_params.clear()
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
activities = client.get_activities(limit=5)
st.header("Your Recent Activities 🏃‍♂️")

for activity in activities:
    dist_km    = activity.distance    / 1000
    secs       = get_seconds(activity.moving_time)
    moving     = format_duration(secs)
    start_loc  = activity.start_date.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    speed_kmh  = activity.average_speed * 3.6
    elev_gain  = activity.total_elevation_gain

    st.subheader(f"{activity.name} ({activity.type.root})")
    c1, c2, c3 = st.columns(3)
    c1.metric("Distance",    f"{dist_km:.2f} km")
    c2.metric("Moving Time", moving)
    c3.metric("Avg Speed",   f"{speed_kmh:.2f} km/h")

    date_str, time_str = start_loc.split(" ")
    c4, c5, c6 = st.columns(3)
    c4.metric("Elevation Gain", f"{elev_gain:.1f} m")
    c5.metric("Date", date_str)
    c6.metric("Time", time_str)

    st.markdown("---")
