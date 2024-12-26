# app.py
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

# Set page config
st.set_page_config(
    page_title="Spotify Wrapped",
    page_icon="🎵",
    layout="wide"
)

# Initialize session states
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'audio_features_added' not in st.session_state:
    st.session_state.audio_features_added = False

# Apply dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stats-card {
        background-color: #282828;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
    }
    .spotify-green {
        color: #1DB954;
    }
    </style>
""", unsafe_allow_html=True)

# Main page content
st.title("🎵 Welcome to Your Spotify Wrapped Dashboard")

st.markdown("""
### Discover Your Music Journey! 🚀

This dashboard helps you visualize and understand your Spotify listening habits. 
Get ready to explore your musical journey with detailed insights and beautiful visualizations.

#### What You'll Need:
- Your Spotify streaming history data
- A few minutes to explore your music taste

#### How to Use:
1. Head to the **Upload Data** page in the sidebar
2. Follow the instructions to upload your Spotify data
3. Let us analyze your listening habits
4. Explore your personalized Spotify Wrapped!

#### Features:
- 📊 Detailed listening statistics
- 🎵 Song and artist analysis
- ⏰ Time-based patterns
- 🎸 Audio feature insights
- 📈 Interactive visualizations

Ready to start? Click on **Upload Data** bellow!
""")

with stylable_container(
    key="green_button",
    css_styles="""
        button {
            background-color: #1DB954 !important;
            color: white !important;
            border: none !important;
        }
        button:hover {
            background-color: #1ed760 !important;
            color: white !important;
            border: none !important;
        }
    """,
):
    if st.button("Upload Data 📃"):
        st.switch_page("pages/upload.py")

# Optional: Add a sample visualization or image
st.divider()

# Footer
st.markdown("Made with ❤️ by Fore Coffee")

