import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re

def extract_video_id(url):
    video_id = ''
    patterns = [
        r'youtu\.be\/([^\?\/]+)',
        r'youtube\.com\/watch\?v=([^\&\/]+)',
        r'youtube\.com\/embed\/([^\?\/]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    return video_id

def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([d['text'] for d in transcript_list])
        return transcript
    except Exception as e:
        st.error("Transcript not available for this video.")
        return ''

def find_tokens(transcript, coins):
    tokens_found = []
    transcript_lower = transcript.lower()
    for coin in coins:
        if coin['name'].lower() in transcript_lower or coin['symbol'].lower() in transcript_lower:
            tokens_found.append(coin)
    return tokens_found

st.title("4tune: Crypto Token Extractor")

youtube_url = st.text_input("Enter YouTube Video URL:")
if st.button("Extract Tokens"):
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            transcript = fetch_transcript(video_id)
            if transcript:
                response = requests.get('https://api.coingecko.com/api/v3/coins/list')
                coins = response.json()
                tokens_found = find_tokens(transcript, coins)
                if tokens_found:
                    st.subheader("Tokens Mentioned:")
                    for coin in tokens_found[:10]:
                        st.markdown(f"- [{coin['name']} ({coin['symbol'].upper()})](https://www.coingecko.com/en/coins/{coin['id']})")
                else:
                    st.info("No crypto tokens mentioned in the transcript.")
        else:
            st.warning("Could not extract video ID from the URL. Please check the URL and try again.")
    else:
        st.warning("Please enter a valid YouTube URL.")
