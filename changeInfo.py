# change description.json
import os
import json
import pandas as pd
import numpy as np

cityPath = '/Users/frederikwarburg/Desktop/Bangkok'

paths = open(os.path.join(cityPath,"paths.txt"))

for path in paths:
    path = path[:-1]

    with open(os.path.join(cityPath,path,"overview.json")) as f:
        overview = json.load(f)

    for seqNum in overview:

        sequence = overview[seqNum]

        data = pd.read_csv(os.path.join(cityPath,path,"sequenceSet" + seqNum, "info.csv"))

        yearsInfo = data['year']
        panoidsInfo = np.array(data['panoid'])

        frames = int(len(panoidsInfo)/4)

        newYearsInfo = np.array(['      '] * 4* frames)

        for i in range(4):

            for k, date in enumerate(sequence):

                dateSequence = sequence[date]
                panoids = dateSequence['panoid']

                if np.all(panoids == panoidsInfo[frames*i:(i+1)*frames]):
                    tmp = [date]*frames

                    newYearsInfo[frames*i:(i+1)*frames] = tmp

        data['year'] = newYearsInfo
        data.to_csv(os.path.join(cityPath,path,"sequenceSet" + seqNum, "info.csv"),index=False)
