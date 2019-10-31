#####################
#   Joel Weidenmark #
#   joelwei@kth.se  #
#   29/10 - 2019    #
#   DD1315 - HT15   #
#   Puppgift        #
#####################

# To run the program you have to create a library and a playlists directory
# in the same folder as this file.
# Any songs added to the library folder need to have an empty TRCK tag
# so that the program can write it's own ID


import os
from mutagen.id3 import ID3, TRCK, TIT2, TPE1, TBPM
from mutagen.id3 import ID3NoHeaderError
from shutil import copyfile
import time


class Song:
    #Every song is an object
    def __init__(self, title, artist, bpm, originalName, filePath, songID = None):
        self.title = title
        self.artist = artist
        self.bpm = bpm
        self.originalName = originalName
        self.songID = songID
        self.filePath = filePath
    

class Playlist:
    #Every playlist is an object. songObjectList contains song objects
    def __init__(self, name, songObjectList = None, writeWithBPM = False):
        if songObjectList is None:
            songObjectList = []
        self.name = name
        self.songObjectList = songObjectList
        if self.name == 'library':
            self.writeWithBPM = True
        else:
            self.writeWithBPM = writeWithBPM
        


def startup():
    #Here we will read all song files and playlists

    #Paths for song and playlist library
    songsPath = os.path.abspath("library/")
    playlistsPath = os.path.abspath("playlists/")
    playlistFolderList = os.listdir(playlistsPath)

    #Creates a playlist object of our entire library
    read_playlists(songsPath, "library")

    #Creates playlistobjects of all playlists
    for playlistFolder in playlistFolderList:
        if playlistFolder != ".DS_Store":
            read_playlists(playlistsPath + "/" + playlistFolder, playlistFolder)
    menu()
    
def read_playlists(path, playlistName):
    #Reads the songs from a playlist. Creates a playlist object and adds the object to our playlist list
    currentPlayList = Playlist(playlistName)
    read_song_file(path, currentPlayList.songObjectList)
    playlistLibrary.append(currentPlayList)

def read_song_file(path, songList):
    #Reads all song files in the selected path. Creates song objects and fills the given playlist
    songFileList = os.listdir(path)
    songsNoID = []
    highestID = 0
    for songFile in songFileList:
        if songFile != ".DS_Store":
            currentSongID3 = ID3(path + "/" + songFile)
            title = currentSongID3["TIT2"].text[0]
            artist = currentSongID3['TPE1'].text[0]
            bpm = currentSongID3['TBPM'].text[0]
            songID = currentSongID3['TRCK'].text[0]
            if int(songID) > highestID:
                highestID = int(songID)
            if songID == "0":
                songsNoID.append(currentSongID3)
            newObject = Song(title, artist, bpm, title, path + "/" + songFile, songID)
            songList.append(newObject)
    if len(songsNoID) > 0:
        id_SongsID3(songsNoID, highestID)

def id_SongsID3(songs, highestID):
    #Gives each song in the library an ID
    for song in songs:
        string = str(highestID + 1)
        song["TRCK"] = TRCK(encoding=3, text=string)
        highestID += 1
        song.save()

def showSongs(playList):
    #Prints the songs in the given playList
    songIndex = 0
    print("\n")
    for song in playList.songObjectList:
        songIndex = songIndex + 1
        if playList.writeWithBPM == False:
            print(str(songIndex) + ". " + song.title + " - " + song.artist)
        else:
            print(str(songIndex) + ". " + "(" + song.bpm + ") " + song.title + " - " + song.artist)

def validateChange(what, choice, playList):
    #Validates the input of choosing song to change
    try:    
        inputNum = int(choice)
        if (inputNum - 1) >= 0:
            songObj = playList.songObjectList[inputNum - 1]
            if what == "Title":
                changeInfo(what, songObj, songObj.title)
            elif what == "Artist":
                changeInfo(what, songObj, songObj.artist)
        else:
            raise IndexError
    except (ValueError, IndexError, TypeError):
        print("\nYou have to enter a number between 1 and " + str(len(playList.songObjectList)))

def changeInfo(what, songObj, songAttr):
    #Give a song a new name
    print("Current Name: " + songAttr)
    newName = input("Write new name: ")
    changeString = "Are you sure you want to change\n" + songAttr + "\nto\n" + newName + "\n(y/n):"
    while True:
        confirmChange = input(changeString)
        if confirmChange == "y":
            if what == "Title":  
                songObj.title = newName
            elif what == "Artist":
                songObj.artist = newName
            print(what + " successfully changed to " + newName)
            break
        elif confirmChange == "n":
            break


def playlistSettings(playList):
    #Menu for all changes you can do to a playlist. Takes you to other functions depending on what you want to change
    while True:
        printMenu("Playlist Menu")
        choice = input("What do you want to do?: ")
        if choice == "0":
            break
        else:
            try:
                choice = int(choice)
                if choice < 9:
                    if choice == 1:
                        if not playList.writeWithBPM:
                            playList.writeWithBPM = True
                            showSongs(playList)
                        else:
                            playList.writeWithBPM = False
                            showSongs(playList)
                    elif choice == 2:
                        playList.songObjectList.sort(key = lambda song: song.title.upper(), reverse=False)
                        showSongs(playList)
                    elif choice == 3:
                        playList.songObjectList.sort(key = lambda song: song.artist.upper(), reverse=False)
                        showSongs(playList)
                    elif choice == 4:
                        playList.songObjectList.sort(key = lambda song: song.bpm, reverse=False)
                        showSongs(playList)
                    elif choice == 5:
                        while True:
                            showSongs(playList)
                            songChoice = input("\nChoose song to edit (write 0 to go back): ")
                            if songChoice != "0":
                                validateChange("Title", songChoice, playList)
                            else:
                                break
                    elif choice == 6:
                        while True:
                            showSongs(playList)
                            songChoice = input("\nChoose song to edit (write 0 to go back): ")
                            if songChoice != "0":
                                validateChange("Artist", songChoice, playList)
                            else:
                                break
                    elif choice == 7:
                        #Add song to playlist
                        addSongToPlaylist(playList)

                    elif choice == 8:
                        showSongs(playList)
                else:
                    raise ValueError
            except ValueError:
                print("You have to enter a number between 1 and 8")


def addSongToPlaylist(playList):
    #Function for adding songs to a playlist. First choose a list to add from, then choose what to add
    print("\n" + "Choose a playlist to add songs from\n")
    
    printIndex = 1
    for item in playlistLibrary:
        print(str(printIndex) + ". " + item.name)
        printIndex += 1
    printIndex = 1

    while True:
        choice = input("Playlist number (0 to go back): ")
        try:
            if int(choice) <= len(playlistLibrary) and int(choice) > 0:
                playListChoice = playlistLibrary[int(choice) - 1]
                showSongs(playListChoice)
                choosenSongs = chooseSongsAdd(playListChoice)
                print("")
                for song in choosenSongs:
                    if checkIfAlreadyInList(song, playList):
                        playList.songObjectList.append(song)
                        print(song.title + " - " + song.artist)
                print("\nSongs added successfully!")
                return
            elif int(choice) == 0:
                break
            else:
                raise ValueError
        except ValueError:
            print("Choose a number between 1 and " + str(len(playlistLibrary)) + " or 0 to go back")

def checkIfAlreadyInList(song, playList):
    #Checking if a song is already in a list. If so the song won't be added
    for playlistSong in playList.songObjectList:
        if song.songID == playlistSong.songID:
            return False
    return True

def chooseSongsAdd(playList):
    #Function for choosing what songs to add to a list
    while True:
        choosenSongs = []
        choice = input("\n" + "Choose songs to add, separate with ',' (write 0 to go back):")
        if choice == "0":
            return
        choiceList = choice.replace(" ", "").split(",")
        try:
            for item in choiceList:
                intCheck = int(item)
                checkLen = (intCheck <= len(playList.songObjectList))
                if not checkLen:
                    raise ValueError
                
                choosenSongs.append(playList.songObjectList[intCheck-1])
            return choosenSongs
        except ValueError:
            print("Wrong input. Separate values with ',' and make sure the index is in the list")


def choosePlaylist():
    #Choose playlist to edit
    print("These are your playlists!\n")
    printIndex = 1

    while True:
        print("")
        for item in playlistLibrary:
            print(str(printIndex) + ". " + item.name)
            printIndex += 1
        printIndex = 1
        choice = input("\nChoose playlist (0 to go back):")
        try:
            if int(choice) <= len(playlistLibrary) and int(choice) > 0:
                playListChoice = playlistLibrary[int(choice) - 1]
                showSongs(playListChoice)
                if playListChoice.name == "library":
                    print("\nThese are the songs in your library. You cannot change the library.")
                else:
                    editPlaylistQuestion(playListChoice)
            elif int(choice) == 0:
                break
            else:
                raise ValueError
        except ValueError:
            print("Choose a number between 1 and " + str(len(playlistLibrary)))


def editPlaylistQuestion(playList):
    #Valdate yes and no answer to see if user wants to select this current list
    while True:
        choice = input("\nDo you want to edit playlist " + playList.name + "? (y/n): ")
        try:
            if choice == "y":
                playlistSettings(playList)
            elif choice == "n":
                break
            else:
                raise ValueError
        except ValueError:
            print("Type 'y' for yes and 'n' for no.")

def createNewPlaylist():
    #Create new list and add songs to it
    name = input("Give your new playlist a name (characters only): ")
    while True:
        if name.isalpha():
            newPlayList = Playlist(name)
            addSongToPlaylist(newPlayList)
            playlistLibrary.append(newPlayList)
            print("\nA playlist with the name " +  name + " created successfully!")
            break
        else:
            name = input("Input failed! Give your new playlist a name (characters only): ")


def saveFiles():
    #Saves everything you have done
    playlistPath = os.path.abspath("playlists/")
    
    currentListSongIds = []
    
    libraryDict = {}
    
    for song in playlistLibrary[0].songObjectList:
        libraryDict[song.songID] = song.filePath
        
    #Go through one playlist at the time
    for playlist in playlistLibrary:
        songsToCopy = []
        songObjectIds = []
        currentListSongIds = []
        writeWithBPM = playlist.writeWithBPM
        if playlist.name != "library":
            #Creates list with all files in the playlist folder
            try:
                songFileList = os.listdir(playlistPath + "/" + playlist.name)
            except FileNotFoundError:
                os.mkdir(playlistPath + "/" + playlist.name)
                time.sleep(2)
                songFileList = os.listdir(playlistPath + "/" + playlist.name)

            #Create a list of all IDs of the songs in the playlist folder
            for songFile in songFileList:
                if songFile != ".DS_Store":
                    songID3 = ID3(playlistPath + "/" + playlist.name + "/" + songFile)
                    currentListSongIds.append(songID3['TRCK'].text[0])

            #Check what songs are in objectList. If not in playlist folder, add to copy array
            
            for song in playlist.songObjectList:
                songObjectIds.append(song.songID)
                if song.songID not in currentListSongIds:
                    songsToCopy.append(song)
                    
            for song in songsToCopy:
                copyfile(libraryDict.get(song.songID), playlistPath + "/" + playlist.name + "/" + song.title + " - " + song.artist +  ".mp3")
            
            #Write with or without bpm and change names - Rewerite ID3
            finalSongFileList = os.listdir(playlistPath + "/" + playlist.name)
            for songFile in finalSongFileList:
                if songFile != ".DS_Store":
                    songID3 = ID3(playlistPath + "/" + playlist.name + "/" + songFile)
                    songID3["TIT2"] = TIT2(encoding=3, text=findID3ObjMatch(songID3["TRCK"].text[0], playlist).title)
                    songID3["TPE1"] = TPE1(encoding=3, text=findID3ObjMatch(songID3["TRCK"].text[0], playlist).artist)
                    songID3["TBPM"] = TBPM(encoding=3, text=findID3ObjMatch(songID3["TRCK"].text[0], playlist).bpm)
                    songID3.save()
                    
                    if writeWithBPM:
                        os.rename(playlistPath + "/" + playlist.name + "/" + songFile, playlistPath + "/" + playlist.name + "/" + "("  + songID3['TBPM'].text[0] + ")" + songID3['TIT2'].text[0] + " - " + songID3['TPE1'].text[0] + ".mp3")
                    else:
                        os.rename(playlistPath + "/" + playlist.name + "/" + songFile, playlistPath + "/" + playlist.name + "/" + songID3['TIT2'].text[0] + " - " + songID3['TPE1'].text[0] + ".mp3")

    print("Everything is saved!")

def findID3ObjMatch(ID3songID, playList):
    #Finds the match between a song object and a file
    for song in playList.songObjectList:
        if song.songID == ID3songID:
            return song

def mainMenuChoice(choice):
    #Choices in main menu
    try:
        choice = int(choice)
        if choice < 5:
            if choice == 1:
                for item in playlistLibrary:
                    if item.name == "library":
                        showSongs(item)
            elif choice == 2:
                choosePlaylist()
            elif choice == 3:
                createNewPlaylist()
            elif choice == 4:
                saveFiles()
        else:
            raise ValueError
    except ValueError:
        print("You have to enter a number between 1 and 4")
    return

def printMenu(selection):
    #Function for choosing what menu to print

    if selection == "Main Menu":
        print("\n1. Show song library")
        print("2. Edit playlists")
        print("3. Create new playlist")
        print("4. Save")
        print("0. Exit ")

    elif selection == "Playlist Menu":
        print("\n1. Toggle BPM")
        print("2. Sort by tile")
        print("3. Sort by artist")
        print("4. Sort by BPM")
        print("5. Edit Title of a song")
        print("6. Edit Artist of a song")
        print("7. Add song to playlist")
        print("8. Show songs in current list")
        print("0. Go back")

    return

def menu():
    #Starting menu
    print("\nWelcome to your personal MP3 Handler!")
    print("Please choose from the following options:")
    while True:
        printMenu("Main Menu")
        inputChoice = input("Choose: ")
        if inputChoice == "0":
            break
        else:
            mainMenuChoice(inputChoice)
    print(inputChoice)


#Starts the program and creates a list for all the playlists
playlistLibrary = []
startup()
