import soundcloud
import os
import requests
import click
from dotenv import load_dotenv
load_dotenv()

def resolveUid(userId):
    if isinstance(userId, int):
        userId = str(userId)
    elif isinstance(userId, str):
        tmpUsr = client.get('/resolve', url='https://soundcloud.com/'+userId)
        userId = str(tmpUsr.id)
    else:
        raise AttributeError(
            "The ID passed in is invalid. ID should be username as a string, or ID as an integer.")
    return userId

def getLikes(url):
    print('Fetching a new page of likes...')
    res = []
    likes = client.get(url, linked_partitioning=1)
    if (likes.reason != 'OK'):
        raise Exception("An unexpected message was encountered when fetching liked tracks.", )
    for track in likes.collection:
        if (track.streamable):
            res.append({"song": track.title, "id": track.id, "artist": track.user["username"], "artist_id": track.user[
                         "id"], "streamable": track.streamable, "stream_url": track.stream_url if track.streamable else "",
                         "download_url": track.download_url if track.streamable else ""})
    if (likes.next_href):
        return res+recursive(likes.next_href)
    else:
        print('Done fetching likes.')
        return res
        
def dlSong(obj, path):
    file = requests.get(obj["stream_url"], params={'client_id': os.environ['sc_client_id']})
    f = open(path, "wb")
    f.write(file.content)
    f.close()

def dlSongs(songs, path):
    print("Beginning download...")
    if (os.path.exists(path) and os.path.isdir(path) == False):
        raise Exception("The path passed in is either not a directory or nonexistent.")
    for song in songs:
        fname = f"{song['artist']} - {song['song']}.mp3".replace("/","_").replace("\\","_").replace(":","_")
        fpath = os.path.join(path,fname)
        print("Downloading...", fpath)
        dlSong(song,fpath)

@click.command()
@click.option('--user', help='The username, or user id of the user whose likes you want to download.', required=True)
@click.option('--path', help='The directory to download songs to.', required=True)
@click.option('--client_id', default=os.environ["sc_client_id"], help='SoundCloud client ID used to authenticate with SoundCloud API. Defaults to the environment variable `sc_client_id` if not specified.')
@click.option('--client_secret', default=os.environ["sc_client_secret"], help='SoundCloud client secret used to authenticate with SoundCloud API. Defaults to the environment variable `sc_client_secret` if not specified.')
def go(user, path, client_id, client_secret):
    """Download all of a SoundCloud user's liked tracks to a directory."""
    print("Initializing SoundCloud client...")
    global client
    client = soundcloud.Client(
        client_id=client_id,
        client_secret=client_secret)
    print("Client initialization successful. Getting a listing of tracks from SoundCloud.")
    dlSongs(getLikes('/users/' + resolveUid(user) + '/likes/tracks'), path)

if __name__ == '__main__':
    go()
