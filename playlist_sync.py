#!/usr/bin/env python

import os
import sys
import re
import string
import eyed3
from unidecode import unidecode
from configparser import ConfigParser


# API to interface with Youtube Music API
from ytmusicapi.ytmusic import YTMusic

# API to parse MP3 tags in local files
from mutagen.easyid3 import EasyID3
# https://code.google.com/archive/p/mutagen/wikis/Tutorial.wiki


###################

def config(filename, section):
        filename = os.getcwd() + '/' + filename
        parser = ConfigParser()
        parser.read(filename)

        conf = {}
        if parser.has_section(section):
                params = parser.items(section)
                for param in params:
                        conf[param[0]] = param[1]
        else:
                raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        return conf

###


def normalizeUnicode(s):
    s = unidecode(s)
    printable = set(string.printable)
    s = ''.join(filter(lambda x: x in printable, s))
    return s

###

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

###

def getPlayListFiles(plFile):

    local_pls_file = [0] * 1000
    local_pls_name = [0] * 1000
    need_to_read_file = [0] * 1000
    need_to_create_name = [0] * 1000

    if plFile == 'all':
        ### find all local playlists
        i = 0
        for pl_file in os.listdir(playlist_dir):
            if pl_file.endswith(".m3u"):
                local_pls_name[i] = pl_file
                local_pls_file[i] = os.path.join(playlist_dir, pl_file)
                i += 1
    else:
        local_pls_name[0] = playlist_file
        local_pls_file[0] = os.path.join(playlist_dir, playlist_file)

    ### find all cloud playlists
    all_pls = ytm.get_library_playlists(1000)

    found_count = 0
    cnt = 0
    while (cnt <= (len(local_pls_name))) and (local_pls_name[cnt] != 0):
        found = 0
        # replace underscores with spaces for title of playlist comparison
        # this is a personal convention for how playlist files are named - you may not need to do this
        test_local = re.sub(r'_', ' ', str(local_pls_name[cnt]))
        test_local = re.sub(r'.m3u', '', test_local)
        file_local = str(local_pls_file[cnt])
        for p in all_pls:
            if str(p['title']) == test_local:
                found = 1
                break
        if found == 0:
            print("Playlist " + test_local + " does not exist in Youtube Music")
            need_to_create_name[found_count] = test_local
            need_to_read_file[found_count] = file_local
            found_count += 1
        else:
            print("Skipping playlist '" + test_local + "'  - found it in Youtube Music")
        cnt += 1

    return(need_to_create_name, need_to_read_file)

###

def mp3tags(songFile):
    songDict = dict()
    audiofile = None
    # get all MP3 tags for this file
    try:
        audiofile = eyed3.load(songFile)
    except:
        return None
    songDict['title'] = audiofile.tag.title if audiofile else None
    if not songDict['title']:
        return None
    else:
        songDict['title'] = normalizeUnicode(songDict['title'])
    songDict['artist'] = audiofile.tag.artist
    if not songDict['artist']:
        return None
    else:
        songDict['artist'] = normalizeUnicode(songDict['artist'])

    songDict['genre'] = str(audiofile.tag.genre)

    if audiofile.tag.track_num and str(audiofile.tag.track_num[0]) != 'None':
        songDict['track_number'] = int(str(audiofile.tag.track_num[0]))
    if audiofile.info:
        songDict['secs'] = audiofile.info.time_secs
        if songDict['secs']:
            songDict['secs'] = int(float(songDict['secs']))
            if str(audiofile.info.bit_rate[1]) != 'None':
                songDict['bit_rate'] = str(audiofile.info.bit_rate[1])
    if audiofile.tag.comments:
        try:
            songDict['comment'] = str(audiofile.tag.comments[1].text)
        except IndexError:
            songDict['comment'] = str(audiofile.tag.comments[0].text)
            songDict['comment'] = normalizeUnicode(songDict['comment'])
    year = str(audiofile.tag.getBestDate())
    songDict['year'] = year[0:4]
    songDict['year'] = safe_cast(songDict['year'], int, '')
    if audiofile.tag.album:
        songDict['album'] = str(audiofile.tag.album)
        songDict['album'] = normalizeUnicode(songDict['album'])
    songDict['filename'] = normalizeUnicode(songFile)

    return songDict

###


###################


### Main ###
playlist_file = None
if len(sys.argv) > 1:
    playlist_file =  sys.argv[1]
else:
    print("Usage: python playlist_sync.py [playlist_file_name.m3u]")
    exit()

# the directory where your .m3u playlists live
params = config('music.ini', 'music')
playlist_dir = params['dir']

# authenticate w Youtube Music
ytm = YTMusic('headers_auth.json')

# figure out which playlist files we need to create 
(need_to_create_name, need_to_read_file) = getPlayListFiles(playlist_file)

### find each song in each new playlist, lookup song_ids in Youtube Music, add them to list, create new playlist
cnt = 0
while (cnt <= len(need_to_read_file)) and (need_to_read_file[cnt] != 0 and os.path.isfile(need_to_read_file[cnt])):
    songCount = 0
    pl_songs = []
    # read local playlist
    print("reading playlist : " + str(need_to_read_file[cnt]))
    with open(need_to_read_file[cnt], 'r', errors='replace') as f:
        line = f.readline()
        while line:
            # grab each relevant line
            if not (line.startswith('#') or ('.mp4' in line or '.m4a' in line)):
                # extract title from MP3 tag
                file_lookup = playlist_dir + line
                # convert m3u file naming conventions to standard Unix
                file_lookup = re.sub(r'\\', '/', file_lookup)
                file_lookup = re.sub(r'\r', '', file_lookup)
                file_lookup = re.sub(r'\n', '', file_lookup)
                # my personal issue
                #file_lookup = re.sub(playlist_dir, '', file_lookup)
                # get all mp3 tag data
                mp3 = []
                mp3 = mp3tags(file_lookup)
                if not mp3:
                    try:
                        mp3 = EasyID3(songFile)
                    except:
                        mp3 = None 
                if not mp3: 
                    print('Cannot extract mp3 tags from ' + file_lookup)
                    line = f.readline()
                    continue
                songCount += 1
                check_title = ''
                check_artist = ''
                check_album = ''
                if 'title' in mp3 and 'artist' in mp3:
                    if type(mp3["title"]) == 'list':
                       check_title = mp3["title"].pop()
                    elif type(mp3["title"] == 'string'):
                       check_title = mp3["title"]
                    else:
                       check_title = ''
                    try :
                        check_title = check_title.encode('ascii', 'ignore').decode('ascii')
                    except:
                        check_title = ''
                    if type(check_title) == 'unicode':
                        check_title = ''
                    if type(mp3["artist"]) == 'list':
                       check_artist = mp3["artist"].pop()
                    elif type(mp3["artist"] == 'string'): 
                        check_artist = mp3["artist"]
                    else:
                        check_artist = ''
                    try:
                        check_artist = check_artist.encode('ascii', 'ignore').decode('ascii')
                    except:
                        check_artist = ''
                    if 'album' in mp3:
                        if type(mp3["album"]) == 'list':
                            check_album = mp3["album"].pop()
                        elif type(mp3["album"] == 'string'):
                            check_album = mp3["album"]
                        else:
                            check_album = ''
                        try:
                            check_album = check_album.encode('ascii', 'ignore').decode('ascii')
                        except:
                            check_album = ''

                # search for song in Youtube Music
                # trying multiple combinations of song, artist, album. filename
                # still cannot get every song in a playlist to successufully return from YTM uploads search

                songDict = songDict1 = songDict2 = songDict3 = list()
                searchFor1 = check_artist + " - " 
                if check_album:
                    searchFor1 += check_album + " - "
                    searchFor1 += check_title
                    #songDict1 = ytm.search(searchFor1, scope='uploads', limit=40)

                searchFor2 = check_artist + " - " + check_title
                songDict2 = ytm.search(searchFor2, scope='uploads', limit=40)

                searchFor3 = check_title
                songDict3 = ytm.search(searchFor3, scope='uploads', limit=40)

                songDict.extend(songDict1)
                songDict.extend(songDict2)
                songDict.extend(songDict3)


                # scan songDict to find song's id (videoID in YTM)
                sd_find = 0
                for sd in songDict:
                    if sd['resultType'] == 'song' and sd['title'] == check_title and sd['artists']:
                        if sd['artists'][0]['name'] == check_artist:
                            if 'album' in sd.keys():
                                if check_album and sd['album']:
                                    if sd['album']['name'] == check_album:
                                        # try to use album match
                                        if(sd['videoId']):
                                            pl_songs.append(str(sd['videoId']))
                                            sd_find = 1
                                            break
                            else:
                                # the title and artist match and album is blank 
                                if(sd['videoId']):
                                    pl_songs.append(str(sd['videoId']))
                                    sd_find = 1
                                    break
                if not sd_find:
                    print("Could not find " + check_title + " by " + check_artist)
            line = f.readline()
    f.close()
        
    # create new playlist
    print('creating playlist ' + str(need_to_create_name[cnt]))
    playlist_id = ytm.create_playlist(title=str(need_to_create_name[cnt]),
                                      description=str(need_to_create_name[cnt]),
                                      privacy_status="PUBLIC",
                                      video_ids=pl_songs)
    print("Created playlist ID : " + str(playlist_id))
    print(str(len(pl_songs)) + " songs added, out of " + str(songCount) + " we got MP3 tags for ...")

    cnt += 1


print(str(cnt) + " new playlists added ...")

###################
