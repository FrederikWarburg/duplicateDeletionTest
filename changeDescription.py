# change description.json
import os
import json
import pandas as pd
import numpy as np

cityPath = '/Volumes/jcivera/Bangkok'

paths = open(os.path.join(cityPath,"paths.txt"))
#paths = ['from: [13.7, 100.4] to: [13.755, 100.4]']
for path in paths:
    path = path[:-1]
    print(os.path.join(cityPath,path,"description.json"))
    with open(os.path.join(cityPath,path,"description.json")) as f:
        description = json.load(f)

    sequenceSets = description["sequenceSets"]

    n = len(sequenceSets)
    kmArray =[]
    for sequenceNumber in range(n):

        sequenceSetPath = os.path.join(cityPath,path,"sequenceSet" + str(sequenceNumber))

        data = pd.read_csv(os.path.join(sequenceSetPath,"info.csv"))

        frames = int(len(data) / 4)

        sequence = sequenceSets["sequence" + str(sequenceNumber)]

        km = np.round(sequence['km'],3)
        sequence['km'] = km
        kmArray.append(km)
        sequence["frames"] = frames
        sequenceSets["sequence" + str(sequenceNumber)] = sequence

    totalKm = np.sum(np.array(kmArray))

    description["totalKm"] = totalKm
    description["sequenceSets"] = sequenceSets

    with open(os.path.join(cityPath,path,"description.json"), 'w') as fp:
        json.dump(description, fp, indent=4, sort_keys=True)