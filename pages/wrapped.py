# pages/wrapped.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
import random
import spotipy
import streamlit.components.v1 as components
from spotipy.oauth2 import SpotifyClientCredentials
from streamlit_extras.add_vertical_space import add_vertical_space
from dotenv import load_dotenv
load_dotenv()

# Page config
st.set_page_config(
    page_title="Your Spotify Wrapped",
    page_icon="🎵",
    layout="centered" 
)

# Check if data exists in session state
if 'processed_data' not in st.session_state or st.session_state.processed_data is None:
    st.error("⚠️ No data found! Please upload your data first.")
    st.stop()

# Get the data
df = st.session_state.processed_data

# ---- Utility Functions ----
def setup_spotify():
    client_id = os.getenv('SPOTIPY_CLIENT_ID')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, 
        client_secret=client_secret
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_top_artists(df, n=10):
    """Get top n artists with their stats"""
    return df.groupby('master_metadata_album_artist_name').agg({
        'minutes_played': 'sum',
        'master_metadata_track_name': 'nunique'
    }).sort_values('minutes_played', ascending=False).head(n)

def get_top_songs(df, n=10):
    """Get top n songs with their stats"""
    return df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name', 'spotify_track_uri']).agg({
        'minutes_played': 'sum',
        'ts': 'count'
    }).reset_index().sort_values('minutes_played', ascending=False).head(n)

def get_spotify_image(sp, name, type='artist'):
    """Get Spotify image URL for artist or track"""
    try:
        results = sp.search(q=name, type=type, limit=1)
        if type == 'artist':
            return results['artists']['items'][0]['images'][0]['url'] if results['artists']['items'] else None
        else:
            return results['tracks']['items'][0]['album']['images'][0]['url'] if results['tracks']['items'] else None
    except:
        return None

def get_spotify_id(sp, name, type='artist'):
    """Get Spotify ID for artist or track"""
    try:
        results = sp.search(q=name, type=type, limit=1)
        if type == 'artist':
            return results['artists']['items'][0]['id'] if results['artists']['items'] else None
        else:
            return results['tracks']['items'][0]['id'] if results['tracks']['items'] else None
    except:
        return None

# ---- Visualization Functions ----
def create_daily_waveform(df):
    df['date'] = pd.to_datetime(df['ts']).dt.date
    daily_counts = df.groupby('date').size().reset_index()
    daily_counts.columns = ['date', 'count']
    daily_counts = daily_counts.sort_values('date')
    daily_counts['date'] = pd.to_datetime(daily_counts['date'])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily_counts['date'],
        y=daily_counts['count'],
        marker_color='#1DB954',
        width=1,
        hoverinfo='text',
        text=[f"{date.strftime('%B %d, %Y')} Songs played: {count}" 
              for date, count in zip(daily_counts['date'], daily_counts['count'])]
    ))
    
    fig.add_trace(go.Bar(
        x=daily_counts['date'],
        y=-daily_counts['count'],
        marker_color='#1DB954',
        width=1,
        showlegend=False,
        hoverinfo='text',
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        barmode='relative',
        bargap=0,
        bargroupgap=0,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='black',
            font_size=14,
            font_family="Arial",
            font_color='white'
        ),
        spikedistance=1000
    )
    
    fig.update_xaxes(showgrid=False, showline=False, showticklabels=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, showline=False)
    
    return fig

def create_listening_clock(df):
    df['hour'] = df['ts'].dt.hour
    hourly_stats = df.groupby('hour')['minutes_played'].sum().reset_index()
    all_hours = pd.DataFrame({'hour': range(24)})
    hourly_stats = all_hours.merge(hourly_stats, on='hour', how='left').fillna(0)
    
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=hourly_stats['minutes_played'],
        theta=hourly_stats['hour'] * 15,
        width=15,
        marker_color='#1DB954',
        opacity=0.8,
        hovertemplate="Hour: %{theta}<br>Minutes: %{r:.0f}<extra></extra>"
    ))
    
    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(showticklabels=False, ticks=''),
            angularaxis=dict(
                ticktext=['12 AM', '3 AM', '6 AM', '9 AM', 
                         '12 PM', '3 PM', '6 PM', '9 PM'],
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                direction='clockwise'
            )
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_top_artists_chart(df, sp):
    top_artists = get_top_artists(df, 10).sort_values('minutes_played', ascending=True)
    artist_images = [get_spotify_image(sp, artist) for artist in top_artists.index]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_artists['minutes_played'],
        y=top_artists.index,
        orientation='h',
        marker_color='#1DB954',
        hovertemplate="Artist: %{y}<br>Minutes: %{x:.0f}<extra></extra>"
    ))
    
    for i, img in enumerate(artist_images):
        if img:
            fig.add_layout_image(dict(
                source=img,
                xref="x",
                yref="y",
                x=0,
                y=i,
                sizex=160,
                sizey=0.8,
                xanchor="left",
                yanchor="middle"
            ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Minutes Played",
        showlegend=False,
        height=500,
        margin=dict(l=120)
    )
    
    return fig

def create_top_songs_chart(df, sp):
    top_songs = get_top_songs(df, 10).sort_values('minutes_played', ascending=True)
    song_images = [get_spotify_image(sp, song, 'track') for song in top_songs['master_metadata_track_name']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_songs['minutes_played'],
        y=top_songs['master_metadata_track_name'],
        orientation='h',
        marker_color='#1DB954',
        hovertemplate="Song: %{y}<br>Minutes: %{x:.0f}<extra></extra>"
    ))
    
    for i, img in enumerate(song_images):
        if img:
            fig.add_layout_image(dict(
                source=img,
                xref="x",
                yref="y",
                x=0,
                y=i,
                sizex=50,
                sizey=0.8,
                xanchor="left",
                yanchor="middle"
            ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Minutes Played",
        showlegend=False,
        height=500,
        margin=dict(l=120)
    )
    
    return fig

def create_features_radar(df):
    features = ['danceability', 'energy', 'valence', 
                'speechiness', 'acousticness', 'instrumentalness']
    
    avg_features = df[features].mean()
    
    colors = {
        'danceability': '#FF6B6B',
        'energy': '#4ECDFF',
        'valence': '#FFD93D',
        'speechiness': '#95E1D3',
        'acousticness': '#F5aA7B',
        'instrumentalness': '#FF8BBA'
    }
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=avg_features,
        theta=features,
        fill='toself',
        line_color='#1DB954',
        fillcolor='rgba(29, 185, 84, 0.3)',
        name='Average',
    ))
    
    for feature, value in zip(features, avg_features):
        r_values = [value if f == feature else 0 for f in features]
        rgb = tuple(int(colors[feature].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        
        fig.add_trace(go.Scatterpolar(
            r=r_values,
            theta=features,
            fill='toself',
            fillcolor=f'rgba{rgb + (0.6,)}',
            line=dict(color=colors[feature], width=2),
            name=feature.capitalize(),
            hovertemplate=feature.capitalize() + ": %{r:.2f}<extra></extra>"
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showticklabels=False,
                gridcolor='rgba(255, 255, 255, 0.1)',
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='white'),
                gridcolor='rgba(255, 255, 255, 0.1)',
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(font=dict(color='white'), bgcolor='rgba(0,0,0,0)'),
        height=500
    )
    
    return fig

# ---- Analysis Functions ----
def analyze_listening_patterns(df):
    df['hour'] = df['ts'].dt.hour
    hourly_stats = df.groupby('hour')['minutes_played'].sum()
    
    time_blocks = {
        'early_morning': (5, 8),
        'work_hours': (9, 17),
        'evening': (17, 22),
        'late_night': (22, 5)
    }
    
    total_minutes = hourly_stats.sum()
    block_percentages = {}
    
    for block, (start, end) in time_blocks.items():
        if start < end:
            block_minutes = hourly_stats[start:end].sum()
        else:
            block_minutes = hourly_stats[start:].sum() + hourly_stats[:end].sum()
        block_percentages[block] = (block_minutes / total_minutes) * 100

    peak_hour = hourly_stats.idxmax()
    insights = [f"🎧 Your music hits different at {peak_hour:02d}:00!"]
    
    pattern_insights = {
        'early_morning': [
            "You're definitely a morning person! Starting your day with music sets a great tone.",
            "Nothing like a good playlist to kick-start your morning routine, right?",
            "Early bird gets the best tracks! Your morning music game is strong."
        ],
        'work_hours': [
            "Looks like music keeps you company through the work day. Your office soundtrack game is on point!",
            "You're all about that work-time groove. Music really makes those work hours fly by, doesn't it?",
            "Your 9-to-5 definitely has a soundtrack! Nothing like some tunes to boost productivity."
        ],
        'evening': [
            "Evening is your prime time for music. Nothing better than unwinding with your favorite tracks!",
            "You're all about that after-work soundtrack. Perfect way to transition into chill time!",
            "The evening is when your playlist really comes alive. Great way to end the day!"
        ],
        'late_night': [
            "You're definitely a night owl when it comes to music! Those late-night listening sessions hit different.",
            "The night time is your time - perfect for discovering new tracks and diving deep into your favorites.",
            "Your music taste comes alive after dark. Those midnight soundtracks must be something special!"
        ]
    }
    
    max_block = max(block_percentages.items(), key=lambda x: x[1])
    insights.append(random.choice(pattern_insights[max_block[0]]))
    
    return insights, block_percentages

def analyze_music_profile(df):
    features = {
        'danceability': df['danceability'].mean(),
        'energy': df['energy'].mean(),
        'valence': df['valence'].mean(),
        'speechiness': df['speechiness'].mean(),
        'acousticness': df['acousticness'].mean(),
        'instrumentalness': df['instrumentalness'].mean()
    }
    
    if features['energy'] > 0.7 and features['danceability'] > 0.6:
        personality = "Party Starter 🎉"
    elif features['acousticness'] > 0.6 and features['instrumentalness'] > 0.4:
        personality = "Soul Searcher 🎸"
    elif features['valence'] > 0.6 and features['energy'] > 0.5:
        personality = "Mood Lifter ⚡"
    elif features['speechiness'] > 0.4:
        personality = "Lyric Lover 🎤"
    else:
        personality = "Eclectic Explorer 🌟"

    insights = [f"You're what we'd call a {personality}! "]
    
    if features['energy'] > 0.7:
        insights.append("Your playlist is packed with high-energy bangers! You really know how to keep the energy up. ⚡")
    elif features['energy'] < 0.4:
        insights.append("You tend to vibe with more laid-back tunes. Perfect for those chill moments. 😌")
    else:
        insights.append("You've got a nice balance of energetic and chill tracks in your mix. 🎵")

    if features['danceability'] > 0.65 and features['valence'] > 0.6:
        insights.append("Your music choices are perfect for getting people on their feet and spreading good vibes! 💃")
    elif features['danceability'] > 0.65 and features['valence'] < 0.4:
        insights.append("You've got moves, but with a moody twist - perfect for those dramatic dance moments! 🕺")

    if features['acousticness'] > 0.6:
        insights.append("You're all about that organic sound - acoustic instruments really speak to your soul. 🎸")
    elif features['acousticness'] < 0.3:
        insights.append("You're drawn to modern, electronic-influenced sounds. Always on the cutting edge! 🎹")

    return insights, personality, features

# ---- Display Functions ----
def display_listening_analysis(df):
    insights, percentages = analyze_listening_patterns(df)
    
    st.markdown("#### 🎵 Your Listening Style")
    
    with st.container():
        st.markdown("""
            <style>
            .insight-box {
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                background-color: rgba(29, 185, 84, 0.1);
                border-left: 4px solid #1DB954;
            }
            </style>
        """, unsafe_allow_html=True)
        
        for insight in insights:
            st.markdown(f"<div class='insight-box'>{insight}</div>", 
                       unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### 📊 Time Block Breakdown")
        cols = st.columns(4)
        
        block_emojis = {
            'early_morning': '🌅',
            'work_hours': '💼',
            'evening': '🌆',
            'late_night': '🌙'
        }
        
        for i, (block, percentage) in enumerate(percentages.items()):
            with cols[i]:
                st.markdown(f"""
                    <div style='text-align: center;'>
                        <div style='font-size: 24px;'>{block_emojis[block]}</div>
                        <div style='font-size: 20px; font-weight: bold;'>{percentage:.1f}%</div>
                        <div style='font-size: 14px;'>{block.replace('_', ' ').title()}</div>
                    </div>
                """, unsafe_allow_html=True)

def display_music_profile_analysis(df):
    if 'audio_features_added' in st.session_state and st.session_state.audio_features_added:
        insights, personality, features = analyze_music_profile(df)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"#### Your Music Personality: {personality}")
            
            st.markdown("""
                <style>
                .music-insight {
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 10px;
                    background-color: rgba(29, 185, 84, 0.1);
                    border-left: 4px solid #1DB954;
                }
                </style>
            """, unsafe_allow_html=True)
            
            for insight in insights:
                st.markdown(f"<div class='music-insight'>{insight}</div>", 
                           unsafe_allow_html=True)

        with col2:
            st.markdown("#### Your Music DNA 🧬")
            feature_emojis = {
                'danceability': '💃',
                'energy': '⚡',
                'valence': '😊',
                'speechiness': '🎤',
                'acousticness': '🎸',
                'instrumentalness': '🎹'
            }
            
            for feature, value in features.items():
                percentage = int(value * 100)
                st.markdown(f"""
                    <div style='margin: 10px 0;'>
                        <div style='font-size: 14px; margin-bottom: 5px;'>
                            {feature_emojis[feature]} {feature.title()}
                        </div>
                        <div style='
                            width: 100%;
                            height: 20px;
                            background-color: rgba(29, 185, 84, 0.2);
                            border-radius: 10px;
                            overflow: hidden;
                        '>
                            <div style='
                                width: {percentage}%;
                                height: 100%;
                                background-color: #1DB954;
                                border-radius: 10px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                                font-size: 12px;
                            '>
                                {percentage}%
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

def display_top_artist_and_song_section(df, sp):
    """Display top artist and song section with images and stats"""
    top_artists = get_top_artists(df, 1).reset_index().iloc[0]
    top_songs = get_top_songs(df, 1).iloc[0]
    
    # Get images
    artist_img = get_spotify_image(sp, top_artists['master_metadata_album_artist_name'])
    song_img = get_spotify_image(sp, top_songs['master_metadata_track_name'], 'track')

    col1, col2 = st.columns(2)
    
    # Top Artist Column
    with col1:
        st.subheader("Top Artists")
        img_info_col1, img_info_col2 = st.columns([1, 1.5])
        with img_info_col1:
            if artist_img:
                st.image(artist_img, width=200)
        with img_info_col2:
            st.markdown(f"""
                ### {top_artists['master_metadata_album_artist_name']}<br>
                **Total Minutes**: {int(top_artists['minutes_played']):,}<br>
                **Unique Songs**: {top_artists['master_metadata_track_name']}
            """, unsafe_allow_html=True)
        st.plotly_chart(create_top_artists_chart(df, sp), use_container_width=True)

    # Top Song Column
    with col2:
        st.subheader("Top Songs")
        img_info_col1, img_info_col2 = st.columns([1, 1.5])
        with img_info_col1:
            if song_img:
                st.image(song_img, width=200)
        with img_info_col2:
            st.markdown(f"""
                ### {top_songs['master_metadata_track_name']}
                **Artist**: {top_songs['master_metadata_album_artist_name']}<br>
                **Times Played**: {int(top_songs['ts'])}<br>
                **Minutes**: {int(top_songs['minutes_played'])}
            """, unsafe_allow_html=True)
        st.plotly_chart(create_top_songs_chart(df, sp), use_container_width=True)

def display_top_artists_player(df, sp):
    top_artists = get_top_artists(df, 8)
    
    if 'selected_artist_id' not in st.session_state:
        st.session_state.selected_artist_id = None

    st.markdown("### Top Artists")
    st.markdown(f"""
                <div class='sub'>ⓘ <i>Click the button bellow to change</i> <br></div>
            """, unsafe_allow_html=True)
    cols = st.columns(8)
    
    st.markdown("""
        <style>
        .circular-image {border-radius: 50%; cursor: pointer; transition: transform 0.2s;}
        .circular-image:hover {transform: scale(1.1);}
        </style>
    """, unsafe_allow_html=True)
    
    for idx, (artist, _) in enumerate(top_artists.iterrows()):
        with cols[idx]:
            artist_id = get_spotify_id(sp, artist)
            artist_image = get_spotify_image(sp, artist)
            
            if artist_image and artist_id:
                if st.button("▶", key=f"artist_{artist_id}", use_container_width=True):
                    st.session_state.selected_artist_id = artist_id
                    st.rerun()
                st.image(artist_image, width=100, use_container_width=True)
    
    if st.session_state.selected_artist_id:
        components.iframe(
            f"https://open.spotify.com/embed/artist/{st.session_state.selected_artist_id}?utm_source=generator",
            height=352
        )
    else:
        components.iframe(
            f"https://open.spotify.com/embed/artist/{artist_id}?utm_source=generator",
            height=352
        )


def main():
    st.markdown("""
        <style>
        .metric-value {font-size: 2.5rem; font-weight: 700; color: white; text-align: center;}
        .metric-label {font-size: 1rem; color: white; text-align: center;}
        .title{font-size: 3.5rem; font-weight: 700; color: white; text-align: left;}
        .sub {font-size: 0.7rem; color: white; text-align: left;}
        </style>
    """, unsafe_allow_html=True)
    
    sp = setup_spotify()
    
    with st.container():
        col1, col2 = st.columns([1,6])
        with col1:
            st.image("assets/spotify.svg", use_container_width=True)
        with col2:
            st.markdown(f"<div class='title'>Spotify Wrapped</div>", unsafe_allow_html=True)

    add_vertical_space(2)

    total_minutes = df['minutes_played'].sum()
    total_songs = len(df)
    total_artists = df['master_metadata_album_artist_name'].nunique()
    
    # Display metrics
    cols = st.columns(3)
    metrics = {
        'Minutes Listened': f"{total_minutes:,.0f}",
        'Songs Listened': f"{total_songs:,}",
        'Different Artists': f"{total_artists:,}"
    }
    
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.markdown(f"""
                <div class='metric-label'>{label}</div>
                <div class='metric-value'>{value}</div>
            """, unsafe_allow_html=True)

    add_vertical_space(2)

    st.plotly_chart(create_daily_waveform(df), use_container_width=True)
    st.markdown(f"""
                <div class='sub'>ⓘ <i>Total songs you played each day</i></div>
            """, unsafe_allow_html=True)
    add_vertical_space(2)

    # Listening patterns
    st.header("⏰ Your Listening Clock")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_listening_clock(df), use_container_width=True)
    with col2:
        display_listening_analysis(df)

    add_vertical_space(2)

    # Top Music Section
    st.header("📈 Your Top Music")
    display_top_artist_and_song_section(df, sp)
    display_top_artists_player(df, sp)

    add_vertical_space(2)

    # Audio features
    if 'audio_features_added' in st.session_state and st.session_state.audio_features_added:
        st.header("👔 Your Music Profile")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(create_features_radar(df), use_container_width=True)
        with col2:
            st.markdown("#### What This Means❓")
            st.markdown("""
            - **Danceability**: How suitable for dancing
            - **Energy**: Intensity and activity level
            - **Valence**: Musical positiveness
            - **Speechiness**: Presence of spoken words
            - **Acousticness**: Amount of acoustic sound
            - **Instrumentalness**: Lack of vocal content
            """)
    
    display_music_profile_analysis(df)

    # Navigation button
    st.markdown("<hr><div class='metric-value'>Want to try with different data❓</div> <br>", unsafe_allow_html=True)
    if st.button("🔁 Use different data", use_container_width=True):
        st.session_state.processed_data = None
        st.session_state.audio_features_added = None
        st.switch_page("pages/upload.py")

if __name__ == "__main__":
    main()