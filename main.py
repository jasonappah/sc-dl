import soundcloud
import b2sdk
import os
from dotenv import load_dotenv
load_dotenv()

client = soundcloud.Client(
    client_id=os.environ["sc_client_id"],
    client_secret=os.environ["sc_client_secret"])


def getUserLikes(userId):
    getting = False
    href = False
    final = []
    arr = []
    if isinstance(userId, int):
        userId = str(userId)
    elif isinstance(userId, str):
        tmpUsr = client.get('/resolve', url='https://soundcloud.com/'+userId)
        userId = str(tmpUsr.id)
    else:
        raise AttributeError(
            "The ID passed in is invalid. ID should be username as a string, or ID as an integer.")
    likes = client.get('/users/' + userId + '/favorites',
                       limit=100, linked_partitioning=1)
    arr.extend(likes.collection)
    while (getting == False or href == True):
        getting = True
        likes = client.get(likes.next_href, limit=100, linked_partitioning=1)
        arr.extend(likes.collection)
        try:
            likes.next_href
            href = True
        except AttributeError:
            href = False
    for i in arr:
        if (i.streamable):
            final.append({"song": i.title, "id": i.id, "artist": i.user["username"], "artist_id": i.user[
                         "id"], "streamable": i.streamable, "stream_url": i.stream_url if i.streamable else ""})
    return final


def getDlLink(trackId):
    track = client.get('/tracks/' + trackId)
    stream_url = client.get(track.stream_url, allow_redirects=False)
    return stream_url.location


yeet = getUserLikes(88656944)
#yeet = getUserLikes('jasonaa')
for i in yeet:
    print(i)
