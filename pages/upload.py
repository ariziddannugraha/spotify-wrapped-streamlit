# pages/1_Upload_Data.py
import streamlit as st
import pandas as pd
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import numpy as np
from dotenv import load_dotenv
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.add_vertical_space import add_vertical_space

load_dotenv()

# Set your Spotify API credentials
os.environ['SPOTIPY_CLIENT_ID'] = os.getenv('SPOTIPY_CLIENT_ID')
os.environ['SPOTIPY_CLIENT_SECRET'] = os.getenv('SPOTIPY_CLIENT_SECRET')

# Initialize Spotify client
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# Set page config
st.set_page_config(
    page_title="Spotify Data Upload",
    page_icon="📂",
    layout="wide"
)

def process_files(uploaded_files):
    """Process uploaded JSON files"""
    all_data = []
    
    for file in uploaded_files:
        try:
            data = json.load(file)
            all_data.extend(data)
        except json.JSONDecodeError:
            st.error(f"Error reading {file.name}. Please make sure it's a valid JSON file.")
            return None
    
    if not all_data:
        st.error("No valid data found in uploaded files.")
        return None
    
    df = pd.DataFrame(all_data)
    
    # Basic data processing
    df['ts'] = pd.to_datetime(df['ts'])
    df['minutes_played'] = df['ms_played'] / (1000 * 60)
    
    return df

def add_audio_features(df):
    if 'spotify_track_uri' not in df.columns:
        st.error("No track URIs found in the data. Cannot generate audio features.")
        return df
    
    unique_tracks = df['spotify_track_uri'].unique()
    total_tracks = len(unique_tracks)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    audio_features = []
    
    for i, uri in enumerate(unique_tracks):
        try:
            if uri and isinstance(uri, str):
                # Use track URI as seed for reproducibility
                # Convert URI to a numeric seed
                seed = int.from_bytes(uri.encode(), 'big') % (2**32)
                np.random.seed(seed)
                
                # Generate random features within reasonable ranges
                feature = {
                    'uri': uri,
                    'danceability': np.random.uniform(0.2, 0.9),
                    'energy': np.random.uniform(0.1, 1.0),
                    'valence': np.random.uniform(0.1, 0.9),
                    'tempo': np.random.uniform(70, 180),
                    'speechiness': np.random.uniform(0.02, 0.2),
                    'acousticness': np.random.uniform(0.0, 1.0),
                    'instrumentalness': np.random.uniform(0.0, 0.8)
                }
                audio_features.append(feature)
            
            # Update progress
            progress = (i + 1) / total_tracks
            progress_bar.progress(progress)
            status_text.text(f'Generating features for track {i + 1} of {total_tracks}')
            
        except Exception as e:
            st.warning(f"Error processing track: {str(e)}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if audio_features:
        features_df = pd.DataFrame(audio_features)
        # Merge features with original DataFrame
        df = df.merge(
            features_df[['uri', 'danceability', 'energy', 'valence', 'tempo', 'speechiness', 'acousticness', 'instrumentalness']],
            left_on='spotify_track_uri',
            right_on='uri',
            how='left'
        )
        st.success("✅ Audio features generated successfully!")
        st.session_state['audio_features_added'] = True
    
    return df

def load_example_data():
    with open('data/StreamingHistory.json', 'r', encoding='utf-8') as file:
        example_data = json.load(file)
    
    # Convert to DataFrame
    df = pd.DataFrame(example_data)
    df['ts'] = pd.to_datetime(df['ts'])
    df['minutes_played'] = df['ms_played'] / (1000 * 60)
    
    return df

def main():
    st.title("🎵 Spotify Wrapped Data Upload")
    
    # Show tutorial
    with st.expander("❓ How to Get Your Data", expanded=True):
        st.header("📚 How to Get Your Spotify Data")
        
        st.markdown("""
        Follow these steps to download your Spotify listening history:
        
        1. Go to your **[Spotify Account](https://www.spotify.com/account)** page
        2. Click on **Privacy Settings**
        3. Scroll down to **Download your data**
        4. Request your data by clicking **Request**
        5. Wait for an email from Spotify (can take up to 30 days)
        6. Download your data when you receive the email
        7. Extract the ZIP file
        8. Look for files named:
        - `Streaming_History*.json`
        - Usually there are multiple files like Streaming_History_Audio_2023-2024_3.json, Streaming_History_Audio_2023.json, etc.
        
        Upload these JSON files below to start analyzing your listening history! 🎵
        """)
    
    # File upload section
    st.header("🎵 Choose Your Data Source")    
    col1, col2 = st.columns([5,1])

    with col1:            
            uploaded_files = st.file_uploader(
                "Upload your StreamingHistory*.json files or use example data",
                type=['json'],
                accept_multiple_files=True
            )
    
    with col2:
            add_vertical_space(3)
            with stylable_container(
                key="green_button",
                css_styles="""                
                    button {
                        background-color: #1DB954 !important;
                        color: white !important;
                        border: none !important;
                        align-content: center !important;
                    }
                    button:hover {
                        background-color: #1ed760 !important;
                        color: white !important;
                        border: none !important;
                    }
                """,
            ):
                use_example = st.button("Use Example Data", use_container_width=True,
                                help="Click to use sample Spotify listening history")
            if use_example:
                with st.spinner("Loading example data..."):
                    df = load_example_data()
                    if df is not None:
                        st.session_state.processed_data = df
                        uploaded_files = None  # Clear any uploaded files
    
    if uploaded_files:
        df = process_files(uploaded_files)
    elif st.session_state.processed_data is not None:
        df = st.session_state.processed_data
    else:
        df = None
        
    if df is not None:
        # Display basic stats
        st.success(f"✅ Successfully loaded {len(df):,} listening records!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Songs", f"{df['master_metadata_track_name'].nunique():,}")
        with col2:
            st.metric("Total Artists", f"{df['master_metadata_album_artist_name'].nunique():,}")
        with col3:
            st.metric("Total Minutes", f"{df['minutes_played'].sum():,.0f}")
        
        # Audio features section
        st.header("🎸 Audio Features")
        if not st.session_state.audio_features_added:
            if st.button("Add Audio Features"):
                st.session_state.processed_data = add_audio_features(df)
        else:
            st.success("✅ Audio features are ready!")
        
        # Navigation button
        if st.session_state.audio_features_added:
            if st.button("🚀 Proceed to Spotify Wrapped", type="primary"):
                st.switch_page("pages/wrapped.py")

if __name__ == "__main__":
    main()