#!/usr/bin/env python

import os
import sys
import re

# API to interface with Youtube Music API
from ytmusicapi.ytmusic import YTMusic

# API to parse MP3 tags in local files
from mutagen.easyid3 import EasyID3
# https://code.google.com/archive/p/mutagen/wikis/Tutorial.wiki

# the directory where your .m3u playlists live
playlist_dir = '/media/jskills/Toshiba-2TB/'

###################


### find all local playlists
local_pls_file = [0] * 1000
local_pls_name = [0] * 1000


playlist_file =  sys.argv[1]

if playlist_file == 'all':
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
    

###################


### authenticate w Youtube Music

ytm = YTMusic('headers_auth.json')

   
### get all songs in the cloud
# long wait time for this :(
#libraryDict = ytm.get_library_upload_songs(100000)

### find all cloud playlists
all_pls = ytm.get_library_playlists(1000)

### compare and find playlists we need to create
need_to_create_name = [0] * 1000
need_to_read_file = [0] * 1000

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
    cnt += 1

###################
    

### find each song in each new playlist, lookup song_ids in Youtube Music, add them to list, create new playlist
cnt = 0
while (cnt <= len(need_to_read_file)) and (need_to_read_file[cnt] != 0 and os.path.isfile(need_to_read_file[cnt])):
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
                print('Getting MP3 tags for : ' + file_lookup)
                mp3 = []
                try:
                    mp3 = EasyID3(file_lookup)
                except:
                    print('Cannot extract mp3 tags from ' + file_lookup)
                    line = None
                    continue
                #print(EasyID3.valid_keys.keys())
                check_title = ''
                check_artist = ''
                check_album = ''
                if 'title' in mp3 and 'artist' in mp3:
                    check_title_list = mp3["title"]
                    check_title = check_title_list.pop()
                    try :
                        check_title = check_title.encode('ascii', 'ignore').decode('ascii')
                    except:
                        check_title = ''
                    if type(check_title) == 'unicode':
                        check_title = ''
                    check_artist_list = mp3["artist"]
                    check_artist = check_artist_list.pop()
                    try:
                        check_artist = check_artist.encode('ascii', 'ignore').decode('ascii')
                    except:
                        check_artist = ''
                    if 'album' in mp3:
                        check_album_list = mp3["album"]
                        check_album = check_album_list.pop()
                        try:
                            check_album = check_album.encode('ascii', 'ignore').decode('ascii')
                        except:
                            check_album = ''

                # search for song in Youtube Music
                searchFor = check_artist + " - " 
                if check_album:
                    searchFor += check_album + " - "
                searchFor += check_title
                print("Querying YTMusic for : " + searchFor)
                songDict = list()
                # TODO : add multiple searches with different formats 
                # with artist or album or without
                # combine results into one dict
                try: 
                    songDict = ytm.search(searchFor, 'uploads', limit=40)
                except:
                    print("Failed search for : " + searchFor) 

                print(str(songDict))

                # scan songDict to find song's id (videoID in YTM)
                sd_find = 0
                for sd in songDict:
                    if sd['resultType'] == 'song' and sd['title'] == check_title and sd['artist']:
                        if sd['artist']['name'] == check_artist:
                            print("id : " + str(sd['videoId']))
                            print("artist : " + str(sd['artist']))
                            print("song : " + str(sd['title']))
                            if check_album and sd['album']:
                                print("album " + str(sd['album']))
                                print("comparing " + str(sd['album']['name']) + " to find " + str(check_album))
                                if sd['album']['name'] == check_album:
                                    # try to use album match
                                    pl_songs.append(str(sd['videoId']))
                                    sd_find = 1
                                    break
                            else:
                                # the title and artist match and album is blank 
                                pl_songs.append(str(sd['videoId']))
                                sd_find = 1
                                break
                if not sd_find:
                    print("Could not find " + check_title + " by " + check_artist)
            line = f.readline()
        
    # create new playlist
    print('creating playlist ' + str(need_to_create_name[cnt]))
    playlist_id = ytm.create_playlist(str(need_to_create_name[cnt]),str(need_to_create_name[cnt]))
    plResponse = ytm.add_playlist_items(playlist_id, pl_songs)
    print(str(plResponse))
    print(str(len(pl_songs)) + " songs added ...")

    cnt += 1


print(str(cnt) + " new playlists added ...")

###################
