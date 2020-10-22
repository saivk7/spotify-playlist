import json

from secrets import spotify_user_id,spotify_token
import requests

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl

from exceptions import ResponseException


class createPlayList:

    def __init__(self):
        self.youtube_client = self.get_youtube_client()
        self.user_id = spotify_user_id
        self.auth_token = spotify_token
        
    #Logging into youtube
    def get_youtube_client(self):
        
        """ Log Into Youtube, Copied from Youtube Data API """
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client


    #Fetching the liked videos from youtube 
    def get_liked_videos(self):
        request = youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like"
        )
        response = request.execute()

        for item in response("items"):
            video_title = item["snipper"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])
            #using  Youtube DL to fetch the song name and artist             
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url,download=False)
            song_name = video["track"]
            artist = video["artist"]

    #Create a new playlist
    def create_new_playlist(self):
        request_body= json.dumps({
            "name":"Youtube Liked",
            "public":True,
            "description":"All Youtube Liked songs"})
        
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        
        response = requests.post(
            query,
            data=request_body,
            header = {
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(auth_token)

            }
        )
        response_json = response.json()

        return response_json["id"]

    #Search for  the song
    def  get_spotify_uri(self,song_name,artist):

        query =  	"https://api.spotify.com/v1/search?q=track%3A{}+artist%3A{}&type=track".format(song_name,artist)


        header = {
            "Content-Type":"application/json",
            "Authorization":"Bearer {}".format(auth_token)
        }
        get_response = requests.get(
            query, header)  

        response_json = get_response.json()
        songs = response_json["tracks"]["items"]

        #get first song only
        uri = songs[0]["uri"]
        
        return uri
        

    #Add this song the new playlist we created
    def add_song(self):
        pass