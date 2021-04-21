from ytmusicapi.ytmusic import YTMusic 

ytm = YTMusic('headers_auth.json')

#results = ytm.search('kind', filter='uploads', limit=20)
results = ytm.get_library_playlists()

print(results)


