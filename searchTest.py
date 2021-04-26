#!/usr/bin/env python

from ytmusicapi.ytmusic import YTMusic


ytm = YTMusic('headers_auth.json')

searchList = list()

searchList.append("Lee Moses - Hey Joe")
searchList.append("Joe Bataan - CALL MY NAME")
searchList.append("Creep")
searchList.append("H.E.R. - Fight For You")
searchList.append("Ugly Casanova - Barnacles")


for searchFor in searchList:
   
    print("Querying YTMusic for : " + searchFor)
    songDict = ytm.search(searchFor, 'uploads', limit=40)

    print("Result : ")
    print(str(songDict))

