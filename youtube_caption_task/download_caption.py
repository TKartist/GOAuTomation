from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import time
import warnings
warnings.filterwarnings("ignore")
import openai
import os
import random


def link_to_id(link):
    '''
    Extracting video ID from any format of YouTube link.
    '''
    if "youtu.be" in link:
        return link.split("/")[-1]
    elif "youtube.com/watch?v=" in link:
        return link.split("v=")[-1].split("&")[0]
    else:
        raise ValueError("Invalid YouTube link format.")
    
def collect_captions(video_list): # takes a list of YouTube video links
    ytt_api = YouTubeTranscriptApi()

    caption_list = []
    # iterate through each video link
    for link in video_list:
        # Check if the link is valid (some links might be "offline" or invalid)
        if link == "offline":
            caption_list.append("No Video Available")
            continue
        
        # Extract video ID from the link
        video_id = link_to_id(link)
        
        # Fetch the list of captions available for the video
        try:
            transcript_list = ytt_api.list(video_id)
        except Exception as e:
            print(f"Error fetching captions for {video_id}: {e}")
            caption_list.append("No Caption Available")
            time.sleep(2)
            continue

        # rate limit handling for YouTube API
        time.sleep(2)
        transcripts = list(transcript_list)
        print(transcripts)
        if len(transcripts) == 0:
            caption_list.append("No Caption Available")
            continue

        available_languages = [t.language_code for t in transcript_list]
        
        preferred = ["en", "es", "fr"]
        cap_lang = next((p for p in preferred if p in available_languages), available_languages[0])
        print(cap_lang)
        print("===================================================================")
        try:
            caption = ytt_api.fetch(video_id, languages=[cap_lang])
            caption_list.append("".join([c.text for c in caption]))
        except Exception as e:
            print(f"Error fetching captions for {video_id}: {e}")
            caption_list.append("No Caption Available")
            time.sleep(2)
            continue
        

        time.sleep(2)

    return caption_list


if __name__ == "__main__":
    df = pd.read_csv("../gym_1_net_sol_limitless_step1.csv", index_col="project_id")
    video_list = df["project_title"].tolist()
    print(video_list[:5])  # Print first 5 video links for verification
    subset = df.sample(n=30, random_state=42)
    
    captions = collect_captions(subset["project_title"].tolist())
    subset["captions"] = captions
    subset.to_csv("../captions_collected.csv", index=False)

