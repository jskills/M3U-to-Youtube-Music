# M3U-to-Youtube-Music
Convert local music playlist files from m3u format to become playlists in Youtube Music library.

This is for those of us that still have libraries of MP3 files and playlists in m3u format.  The m3u playlist format is still a nice way to universally manage playlists and is used by many media players (e.g. Winamp, Media Monkey, iTunes).

This is quick and dirty script you can run regularly to:
  - scan a directory of local m3u playlists
  - pull down all playlists you have in Youtube Music
  - compare and identfy what playlists are not in Youtube Music
  - grab MP3 tags from local songs and find the IDs of those songs in Youtube Music
  - use those IDs to recreate those playlists in Youtube Music

You'll need to go through initial steps to authenticate with Google to ensure it sees your script as one of your authorized devices.  These steps are in the first part of the script.

### TO DO:
  - WRITE ALL OF THE ACTUAL CODE FOR THIS
  
  - ability to prompt user for Y/N as to whether to import each playlist in "all" mode
  - functionality to examine existing Youtube Music playlists and update them if changes have been made to local m3u versions
  - added comparison criteria for mp3 key "album" to further ensure we're looking up the right version of the song for a given artist

