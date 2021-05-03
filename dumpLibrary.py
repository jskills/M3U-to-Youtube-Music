#!/usr/bin/env python

from ytmusicapi.ytmusic import YTMusic

songLimit = 100000

ytm = YTMusic('headers_auth.json')

songList = ytm.get_library_upload_songs(limit=songLimit)

for sl in songList:
    print(str(sl))
