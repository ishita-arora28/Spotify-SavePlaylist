import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask,session,request, url_for,redirect

# initializing flask app 

app=Flask(__name__)

#We use flask because it supports good oauth 

# We will get a token value which will keep the user signed in like a session ID , 
# to save the value we will use the variable spotify cookie

app.config['SESSION_COOKIE_NAME']='Spotify Cookie'
app.secret_key='funandgames2011' #to be prevent unauthorised access to cookie by creating a secure digital sign
TOKEN_INFO='token_info'

#Routes for the application
@app.route('/')
def login():
    #get_authorize_url will generate an authorization for the url
    auth_url=create_spotify_oauth().get_authorize_url() #get the value of url 
    return redirect(auth_url) #redirect to the url


@app.route('/redirect')
def redirect_page():
    session.clear()
    code=request.args.get('code') #get the code field from the request parameters 
    token_info=create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO]=token_info
    return redirect(url_for('top_favs_2021', external=True))

def get_token():
    token_info=session.get(TOKEN_INFO)
    if not token_info:
        redirect(url_for('login'),external=False)
    now=int(time.time())
    is_expired=token_info['expires_at']-now<60
    if(is_expired):
        spotify_auth=create_spotify_oauth()
        token_info=spotify_auth.refresh_access_token(token_info['refresh_token'])
    return token_info


@app.route('/topFavs')
def save_discover_weekly():
    try:
        token_info=get_token()
    except:
        print('User not logged in')
        return redirect('/')
     # First Milestone would be to set up the oauth
     # return("OAUTH SUCCESSFUL")
    sp=spotipy.Spotify(auth=token_info['access_token'])
    current_playlist=sp.current_user_playlists()['items']
    
    
    curr_userid=sp.current_user()['id']

    top_favs_id=None
    saved_top_favs_id=None


    for playlist in current_playlist:
        if(playlist['name']=='Your Top Songs 2021'):
            top_favs_id=playlist['id']
        if(playlist['name']=='Saved 2021'):
            saved_top_favs_id=playlist['id']

    if not top_favs_id:
        return 'Your Top Songs of 2021 playlist doesn\'t exist'
    top_favs_2021=sp.playlist_items(playlist_id=top_favs_id)

    if not saved_top_favs_id:
        new_playlist=sp.user_playlist_create(curr_userid,'Saved 2021',True)
        saved_top_favs_id=new_playlist['id']

    song_uris=[]
    for song in top_favs_2021['items']:
        song_uri=song['track']['uri']
        song_uris.append(song_uri)
    
    saved_weekly_result=sp.user_playlist_add_tracks(curr_userid,saved_top_favs_id,song_uris)
    if saved_weekly_result:
        return "SUCCESS!"
    return "Failure!"

    


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="586ee77a6e9840ccb919c3080ac90284",
        client_secret="660eac3bc2494c7b9d939d7b4fd4fb3c",
        redirect_uri=url_for('redirect_page',_external=True),
        scope='user-library-read playlist-modify-public playlist-read-private playlist-modify-private',
        ) #scope = user-library-read allows developers to read playlist info,songs etc., check the docs for more scope info

app.run(debug=True) #By default flask app runs on localhost at port 5000

