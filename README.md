# Spotify Wrapped Dashboard

A Streamlit interactive application that creates your personal Spotify Wrapped dashboard using your Spotify streaming history data.

## Project Structure
```
spotify-wrapped/
│
├── app.py                      # Main application file
├── pages/                 
│   └── upload.py               # Upload dashboard page
│   └── wrapped.py              # Wrapped dashboard page
├── assets/               
│   └── spotify.svg             # Spotify logo
├── data/
|   └── StreamingHistory.json   # Example of data
├── .env                        # Environment variables (create this)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Prerequisites

1. Python 3.8 or higher
2. Spotify Developer Account
   - Create one at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application to get Client ID and Client Secret

## Setup

1. Clone the repository:
```bash
git clone https://github.com/ariziddannugraha/spotify-wrapped-streamlit.git
cd spotify-wrapped
```

2. Create a virtual environment (optional):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Spotify API credentials:
```plaintext
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
```

## Getting Your Spotify Data

1. Go to [Spotify Account Privacy Settings](https://www.spotify.com/account/privacy/)
2. Request your extended streaming history
3. Download the data when available (usually takes a few days)
4. Extract the JSON files from the downloaded zip

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. Open your browser and go to `http://localhost:8501`
4. Upload your Spotify streaming history files when prompted

## Features

- 📊 Visualize your daily listening patterns
- ⏰ See your listening clock and patterns
- 🎵 View top artists and songs
- 🎧 Interactive Spotify player
- 📈 Audio features analysis
- 🎯 Personalized insights about your music taste

## Dependencies

- streamlit
- pandas
- plotly
- spotipy
- python-dotenv
- streamlit-extras

## Contributing

Feel free to submit issues and enhancement requests.

## License

[MIT](https://choosealicense.com/licenses/mit/)
