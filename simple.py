from ytmusicapi.ytmusic import YTMusic 

ytm = YTMusic('headers_auth.json')

results = ytm.search(query='love', scope='uploads', limit=20)
results = ytm.search(query='love', filter='songs', limit=20)
results = ytm.get_library_upload_songs(100)
results = ytm.get_library_playlists()

print(results)


