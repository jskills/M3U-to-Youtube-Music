#!/usr/bin/env python

from ytmusicapi.ytmusic import YTMusic


### authenticate w Youtube Music

ytm = YTMusic('headers_auth.json')

searchList = list()

searchList.append("Lee Moses - Hey Joe")
searchList.append("Joe Bataan - CALL MY NAME")
searchList.append("Creep")
searchList.append("Ugly Casanova - Barnacles")


for searchFor in searchList:
   
    songDict = list()

    print("Querying YTMusic for : " + searchFor)
    songDict = ytm.search(searchFor, 'uploads', limit=40)
    try: 
        songDict = ytm.search(searchFor, 'uploads', limit=40)
    except:
        print("Failed search for : " + searchFor) 

    print("Result : ")
    print(str(songDict))



###################
