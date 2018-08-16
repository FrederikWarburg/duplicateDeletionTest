import os

basepath = '/Volumes/jcivera'
cityName = 'Bangkok'

cityPath = os.path.join(basepath,cityName)

folders = os.listdir(cityPath)

file = open(os.path.join(cityPath,"paths.txt"), "w+")

badFolders = ["usedPanoids.txt", "cityInfo.txt", ".DS_Store"]

for folder in folders:
    if folder not in badFolders:
        file.write(folder + "\n")

