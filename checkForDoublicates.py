import os
import json
import pandas as pd
import cv2
import numpy as np
import shutil

def deleteImage(path):

    if os.path.exists(path):

        datePath, imageName = os.path.split(path)
        sequencePath, dateName = os.path.split(datePath)
        pathPath, sequenceName = os.path.split(sequencePath)

        file = open(os.path.join(sequencePath,"dates.txt"))
        dates = []

        for date in file:
            dates.append(date[:-1])
        file.close()

        imageNumber = imageName[:-4]

        ############
        # delete image
        ############

        for date in dates:
            pathToRemove = os.path.join(sequencePath, date, imageName)
            os.remove(pathToRemove)

            pathToRemove = os.path.join(sequencePath, "Reverse" + date, imageName)
            os.remove(pathToRemove)

        ############
        # rename images
        ############

        for date in dates:
            n = len(os.listdir(os.path.join(sequencePath, "Reverse" + date)))

            for i in range(n):
                imagePath = os.path.join(sequencePath, "Reverse"+date, str(i) + ".png")

                if not os.path.exists(imagePath):
                    imagePathNext = os.path.join(sequencePath, "Reverse" + date, str(i+1) + ".png")

                    os.rename(imagePathNext,imagePath)

                imagePath = os.path.join(sequencePath, date, str(i) + ".png")

                if not os.path.exists(imagePath):
                    imagePathNext = os.path.join(sequencePath, date, str(i+1) + ".png")

                    os.rename(imagePathNext,imagePath)

        ############
        # change info.csv
        ############

        data = pd.read_csv(os.path.join(sequencePath,"info.csv"))

        imageNames = data['imageName']

        newData = data[imageNames != imageName].copy()
        newImageNames = []

        for i in range(4*n):
            newImageNames.append(str(i%n) + ".png")

        if len(np.array(newImageNames)) != len(newData.iloc[:,2]):
            print("newImageNames is not same length as newData.iloc[:,2]")
            print(len(np.array(newImageNames)),len(newData.iloc[:,2]))
            print(sequencePath)

        newData.iloc[:,2] = np.array(newImageNames)
        newData.to_csv(os.path.join(sequencePath,"info.csv"),index=False)

        ############
        # change overview.json
        ############

        with open(os.path.join(pathPath,"overview.json")) as f:
            overview = json.load(f)

        sequenceNumber = sequenceName[len("sequenceSet"):]
        sequence = overview[sequenceNumber]

        for date in dates:
            overviewDate = sequence[date]

            overviewLat = overviewDate['lat']
            overviewLon = overviewDate['lon']
            overviewOrientation = overviewDate['orientation']
            overviewPanoid = overviewDate['panoid']

            newOverviewLat = []
            newOverviewLon = []
            newOverviewOrientation = []
            newOverviewPanoid = []

            for i in range(len(overviewLat)):

                if str(i) != imageNumber:
                    newOverviewLat.append(overviewLat[i])
                    newOverviewLon.append(overviewLon[i])
                    newOverviewOrientation.append(overviewOrientation[i])
                    newOverviewPanoid.append(overviewPanoid[i])

            overviewDate['lat'] = newOverviewLat
            overviewDate['lon'] = newOverviewLon
            overviewDate['name'] = newImageNames[:n]
            overviewDate['orientation'] = newOverviewOrientation
            overviewDate['panoid'] = newOverviewPanoid

            sequence[date] = overviewDate

        overview[sequenceNumber] = sequence

        with open(os.path.join(pathPath,"overview.json"), 'w') as fp:
            json.dump(overview, fp, indent=4, sort_keys=True)

        ############
        # change description.json
        ############

        with open(os.path.join(pathPath,"description.json")) as f:
            description = json.load(f)

        sequenceSets = description["sequenceSets"]
        sequence = sequenceSets["sequence" + sequenceNumber]
        frames = sequence["frames"]
        sequence["frames"] = int(frames) - 1
        sequenceSets["sequence" + sequenceNumber] = sequence
        description["sequenceSets"] = sequenceSets

        with open(os.path.join(pathPath,"description.json"), 'w') as fp:
            json.dump(description, fp, indent=4, sort_keys=True)



def getNextDouplicatePanoidsAndPaths(cityPath):

    file = open(os.path.join(cityPath, "paths.txt"))
    paths = []
    for path in file:
        paths.append(path[:-1])

    file.close()

    panoids = []

    sequencePaths = []

    for j, path in enumerate(paths):
        pathPath = os.path.join(cityPath, path)

        with open(os.path.join(pathPath, "description.json")) as f:
            description = json.load(f)

        numberOfSequenceSets = description['numberOfSequenceSets']

        for i in range(numberOfSequenceSets):

            sequencePath = os.path.join(pathPath, "sequenceSet" + str(i))

            data = pd.read_csv(os.path.join(sequencePath, "info.csv"))

            panoidForThisSequence = data['panoid']
            imageNames = data['imageName']
            years = data['year']

            for panoid, year, imageName in zip(panoidForThisSequence, years, imageNames):
                panoids.append(panoid)
                sequencePaths.append(os.path.join(pathPath, "sequenceSet" + str(i), str(year), imageName))

        # print("{0} / {1}".format(j,nPaths))

                if len(np.array(panoids)) != len(np.unique(np.array(panoids))):
                    panoids = np.array(panoids)
                    more = True
                    return panoids, sequencePaths, more

    panoids = np.array(panoids)
    if len(np.array(panoids)) != len(np.unique(np.array(panoids))):
        more = True
    else:
        more = False
    print("HEY")
    return panoids, sequencePaths, more

def getPanoidsAndPaths(cityPath):
    file = open(os.path.join(cityPath,"paths.txt"))
    paths = []
    for path in file:
        paths.append(path[:-1])

    file.close()
    #paths = ["from: [13.7, 100.408] to: [13.663, 100.441]"]
    panoids = []

    sequencePaths = []
    nPaths = len(paths)
    for j, path in enumerate(paths):
        pathPath = os.path.join(cityPath, path)

        with open(os.path.join(pathPath, "description.json")) as f:
            description = json.load(f)

        numberOfSequenceSets  = description['numberOfSequenceSets']

        for i in range(numberOfSequenceSets):

            sequencePath = os.path.join(pathPath,"sequenceSet" + str(i))

            data = pd.read_csv(os.path.join(sequencePath,"info.csv"))

            panoidForThisSequence = data['panoid']
            imageNames = data['imageName']
            years = data['year']

            for panoid, year, imageName in zip(panoidForThisSequence,years,imageNames):
                panoids.append(panoid)
                sequencePaths.append(os.path.join(pathPath, "sequenceSet" + str(i), str(year), imageName))

        #print("{0} / {1}".format(j,nPaths))

    panoids = np.array(panoids)

    return panoids, sequencePaths

def duplicates(lst, item):
    return [i for i, x in enumerate(lst) if x == item]

import matplotlib.pyplot as plt



def checkDates(path1,path2):

    basePath1, imageName1 = os.path.split(path1)
    basePath1, date1 = os.path.split(basePath1)

    basePath2, imageName2 = os.path.split(path2)
    basePath2, date2 = os.path.split(basePath2)

    if date1 == date2:
        return True
    else:
        return False

def checkEmpty(path):

    basePath, imageName = os.path.split(path)

    nImages = len(os.listdir(basePath))

    if nImages <= 3:
        return True
    else:
        return False


def deleteFolder(path):

    basePath1, imageName = os.path.split(path)
    basePath2, date = os.path.split(basePath1)

    #print(basePath2)

    basePath3, sequenceName = os.path.split(basePath2)

    sequenceNumber = int(sequenceName[len("sequenceSet"):])

    # change description
    with open(os.path.join(basePath3, "description.json")) as f:
        description = json.load(f)

    numberOfSequenceSets = description['numberOfSequenceSets']
    totalKm = description['totalKm']

    sequenceSets = description['sequenceSets']

    newSequenceSets = {}

    for i, sequence in enumerate(sequenceSets):

        if i < sequenceNumber:
            newSequenceSets[sequence] = sequenceSets[sequence]

        elif i == sequenceNumber:
            km = sequenceSets[sequence]['km']

        elif i > sequenceNumber:
            newSequenceSets["sequence" + str(i-1)] = sequenceSets[sequence]

    description['sequenceSets'] = newSequenceSets
    description['totalKm'] = totalKm - km

    description['numberOfSequenceSets'] = numberOfSequenceSets - 1

    with open(os.path.join(basePath3, "description.json"), 'w') as fp:
        json.dump(description, fp, indent=4, sort_keys=True)

    # change overview

    with open(os.path.join(basePath3, "overview.json")) as f:
        overview = json.load(f)

    newOverview = {}

    for i, sequence in enumerate(overview):

        if i < sequenceNumber:
            newOverview[sequence] = overview[sequence]

        elif i > sequenceNumber:
            newOverview["sequence" + str(i - 1)] = overview[sequence]

    with open(os.path.join(basePath3, "overview.json"), 'w') as fp:
        json.dump(newOverview, fp, indent=4, sort_keys=True)

    # remove and rename sequenceSets

    shutil.rmtree(basePath2)

    for i in range(numberOfSequenceSets):

        if i > sequenceNumber:
            src = os.path.join(basePath3,"sequenceSet" + str(i))
            dst = os.path.join(basePath3,"sequenceSet" + str(i - 1))
            os.rename(src,dst)

def duplicatePaths():

    panoids, paths = getPanoidsAndPaths(cityPath)

    count = 0
    panoids = np.array(panoids)
    uniquePanoids = np.unique(panoids)

    nUniquePanoids = len(uniquePanoids)

    if nUniquePanoids != len(panoids):
        more = True
    else:
        more = False

    counter = 0

    while more:

        for k, uniquePanoid in enumerate(uniquePanoids):
            counter += 1
            idxs = duplicates(panoids,uniquePanoid)

            if len(idxs) > 1:
                path1 = paths[idxs[0]]
                path2 = paths[idxs[1]]

                deleteImage(path2)
                count +=1

                if len(idxs) > 2:
                    print(idxs)

                isEmpty = checkEmpty(path2)

                if isEmpty:
                    deleteFolder(path2)

                panoids, paths = getPanoidsAndPaths(cityPath)
                #print(panoids, paths)

            if counter % 1000 == 0:

                print("{0} / {1}".format(k,nUniquePanoids))
                print(len(np.unique(panoids)), " / ", len(panoids))

            if len(np.unique(panoids)) == len(panoids):
                more = False

    print(count)


cityPath = "/Volumes/jcivera/Bangkok1"

panoids, sequencePaths = getPanoidsAndPaths(cityPath)

print("Before")
print(len(panoids))
print(len(np.unique(panoids)))

duplicatePaths()

panoids, sequencePaths = getPanoidsAndPaths(cityPath)

print("After")
print(len(panoids))
print(len(np.unique(panoids)))

#path1 = "/Volumes/jcivera/Bangkok/from: [13.663, 100.441] to: [13.7076, 100.381]/sequenceSet24/201201/4.png"
#path2 = "/Volumes/jcivera/Bangkok/from: [13.663, 100.44] to: [13.711, 100.43]/sequenceSet12/201410/7.png"
