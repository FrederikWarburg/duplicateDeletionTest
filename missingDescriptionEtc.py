import pandas as pd
import numpy as np
import json
import os
import math
from gmplot import gmplot

def makePlotOfResults(data, lat, lon):

    gmap = gmplot.GoogleMapPlotter(lat,lon, 12)

    colors = ['#f44283','#f44283','#f44283','#5b91a0','#632596','#963725','#d6b753', '#20b2aa','#ffc3a0','#fff68f','#f6546a',
            '#468499','#ff6666','#666666','#66cdaa','#c39797','#00ced1','#ff00ff','#008000','#088da5']
    colors2 = ['red','green','blue','yellow']

    for j, s in enumerate(data):
        dates = data[s]
        for i, date in enumerate(dates):
            obs = dates[date]

            lats = obs['lat']
            lons = obs['lon']
            print(j,i,date,lats)
            gmap.scatter(lats, lons, colors2[i%len(colors2)], edge_width=10)
            gmap.plot(lats, lons, colors[j%len(colors)], edge_width=10)

    return gmap

def calculateOrientation(directions, north):
    # Inspired by
    # https://math.stackexchange.com/questions/529555/signed-angle-between-2-vectors

    u = north

    angles = []
    for direction in directions:

        v = np.array(direction)

        result = math.atan2(v[1],v[0])-math.atan2(u[1],u[0])

        angles.append(result % (2*math.pi))

    return angles

def getOrientations(lats, lons):
    lats = np.array(lats)
    lons = np.array(lons)

    lats_new = []
    lons_new = []
    directions = []

    # First calculate the oritentation relative to world coordinates
    north = np.array([1,0])

    for i in range(len(lons) - 1):

        dx = lats[i + 1] - lats[i]
        dy = lons[i + 1] - lons[i]


        direction = np.array([dx, dy])

        norminator = np.linalg.norm(direction)

        if np.linalg.norm(direction) != 0.0:
            direction = direction / norminator

            directions.append(direction)
            lats_new.append(lats[i])
            lons_new.append(lons[i])

    directions = np.array(directions)
    orientations = calculateOrientation(directions, north)

    pos = np.transpose(np.array([lats_new, lons_new,orientations]))

    return pos


def measure(lat1, lon1, lat2, lon2):  # generally used geo measurement function
    R = 6378.137  # Radius of earth in KM
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1 * math.pi / 180) * math.cos(
        lat2 * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d  # km

basePath = '/Users/frederikwarburg/Desktop/Bangkok'
pathPath = 'from: [13.7, 100.408] to: [13.663, 100.441]'


center = [13.7, 100.408]
path = os.path.join(basePath,pathPath)

##########
# Description
##########

numberOfSequenceSets = 4
kmArray = []

description = {}
description['numberOfSequenceSets'] = numberOfSequenceSets

sequenceSets = {}

for i in range(numberOfSequenceSets):

    sequence = {}
    data = pd.read_csv(os.path.join(path, "sequenceSet" + str(i), "info.csv"))

    lats = data['latitude']
    lons = data['longitude']

    frames = int(len(lats) / 4)

    lats = lats[:frames]
    lons = lons[:frames]

    totalDist = 0

    for k in range(len(lats)-1):
        dist = measure(lats[k],lons[k],lats[k+1],lons[k+1])
        totalDist += dist

    sequence['km'] = totalDist
    kmArray.append(totalDist)

    sequence['frames'] = frames

    dates = np.unique(data['year'])
    datesString = []

    for date in dates:
        datesString.append(str(date))


    sequence['dates'] = datesString

    sequenceSets["sequence"+ str(i)] = sequence

totalKm = np.sum(np.array(kmArray))
description['name'] = pathPath
description['totalKm'] = totalKm
description["sequenceSets"] = sequenceSets

with open(os.path.join(path, "description.json"), 'w') as fp:
    json.dump(description, fp, indent=4, sort_keys=True)

##########
# Overview
##########

overview = {}

for sNumber in range(numberOfSequenceSets):

    dateArray = {}

    data = pd.read_csv(os.path.join(path, "sequenceSet" + str(sNumber),"info.csv"))
    years = np.array(data['year'])
    panoids = np.array(data['panoid'])
    imageNames = np.array(data['imageName'])
    latitudes = np.array(data['latitude'])
    longitudes = np.array(data['longitude'])
    print(latitudes)
    frames = int(len(years)/4)

    for i in range(4):

        sequenceArray = {}

        lat = latitudes[(i*frames):(i+1)*frames]
        lon = longitudes[(i*frames):(i + 1) * frames]
        name = imageNames[(i*frames):(i + 1) * frames]
        panoid = panoids[(i*frames):(i + 1) * frames]

        positions = getOrientations(lat,lon)

        orientations = positions[:,2]

        orientationList = []

        for orientation in orientations:
            orientationList.append(orientation)

        orientationList.append(orientation)

        latList = []
        lonList = []
        nameList = []
        panoidList = []

        for a,b,c,d in zip(lat,lon,name,panoid):
            latList.append(a)
            lonList.append(b)
            nameList.append(c)
            panoidList.append(d)

        sequenceArray['lat'] = latList
        sequenceArray['lon'] = lonList
        sequenceArray['name'] = nameList
        sequenceArray['orientation'] = orientationList
        sequenceArray['panoid'] = panoidList

        date = years[i*frames]
        dateArray[str(date)] = sequenceArray

    overview[str(sNumber)] = dateArray

with open(os.path.join(path, "overview.json"), 'w') as fp:
    json.dump(overview, fp, indent=4, sort_keys=True)

# make plot of the results
gmap = makePlotOfResults(overview, center[0], center[1])
gmap.draw(os.path.join(path, "overview_map.html"))
