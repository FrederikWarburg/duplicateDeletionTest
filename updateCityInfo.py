import json
import numpy as np
import os

cityPath = '/Users/frederikwarburg/Desktop/Bangkok'
cityName = 'Bangkok'
sizeGB = '58.62'
totalKm = 0
totalNImages = 0
totalNPaths = 0
totalNSequenceSets = 0

allFramesArray = []
allYearsArray = []
allMonthsArray = []

paths = open(os.path.join(cityPath,"paths.txt"))
for path in paths:
    path = path[:-1]

    with open(os.path.join(cityPath,path,"description.json")) as f:
        description = json.load(f)

    totalKm += description["totalKm"]

    numberOfSequenceSets = description['numberOfSequenceSets']

    for idx in range(numberOfSequenceSets):
        frames = description['sequenceSets']['sequence'+str(idx)]['frames']
        allFramesArray.append(frames)

        dates = description['sequenceSets']['sequence' + str(idx)]['dates']

        for date in dates:
            allYearsArray.append(int(date[:4]))
            allMonthsArray.append(int(date[-2:]))

        totalNImages += frames * 4 * 2 #frames*4dates*2directions

    totalNPaths += 1

    totalNSequenceSets += numberOfSequenceSets

distFrames, binFrames = np.histogram(allFramesArray,list(range(4,32)))
distYears, binYears = np.histogram(allYearsArray,list(range(2011,2019)))
distMonths, binMonths = np.histogram(allMonthsArray,list(range(0,14)))
print(distMonths,binMonths)
print(len(distMonths),len(binMonths))

cityInfoFile = open(os.path.join(cityPath,"cityInfo.txt"),'w')

cityInfoFile.write("#####\n")
cityInfoFile.write("# Here is an overview of the data from {}.\n".format(cityName))
cityInfoFile.write("#####\n")
cityInfoFile.write("\n")
cityInfoFile.write("# Size: {} GB\n".format(sizeGB))
cityInfoFile.write("# Length: {} km\n".format(np.round(totalKm,2)))
cityInfoFile.write("# Number of images: {}\n".format(totalNImages))
cityInfoFile.write("# Number of paths: {}\n".format(totalNPaths))
cityInfoFile.write("# Number of sequenceSets: {}\n".format(totalNSequenceSets))
cityInfoFile.write("# Number of sequences: {}\n".format(int(totalNSequenceSets*4)))
cityInfoFile.write("\n")
cityInfoFile.write("#####\n")
cityInfoFile.write("# The distribution of the length of the sequenceSets are as follows:\n")
cityInfoFile.write("#####\n")
cityInfoFile.write("\n")

for distFrame, binFrame in zip(distFrames, binFrames):
    cityInfoFile.write("{0} sequences of {1} frames\n".format(distFrame,binFrame))

cityInfoFile.write("\n")
cityInfoFile.write("#####\n")
cityInfoFile.write("# The distribution of the years of the sequences are as follows:\n")
cityInfoFile.write("#####\n")
cityInfoFile.write("\n")

for distYear, binYear in zip(distYears, binYears):
    print(distYear,binYear)
    cityInfoFile.write("{0} sequences from {1}\n".format(distYear,binYear))

cityInfoFile.write("\n")
cityInfoFile.write("#####\n")
cityInfoFile.write("# The distribution of the years of the sequences are as follows:\n")
cityInfoFile.write("#####\n")
cityInfoFile.write("\n")

monthNames = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
distMonths = distMonths[1:]
binMonths = binMonths[1:]
for distMonth, binMonth in zip(distMonths, binMonths):
    cityInfoFile.write("{0} sequences from {1}\n".format(distMonth,monthNames[int(binMonth)-1]))

cityInfoFile.write("\n")


# CityInfo.txt

####
#
# Here is an overview of City Name.
#
####

# Size: X GB
# Size: X km
# Number of images: X
# Number of paths: X
# Number of sequenceSets: X

####
# The distribution of the length of the sequenceSets are as follows:
####



####
# The distribution of the years of the sequences are as follows:
####




####
# The distribution of the months of the sequences are as follows:
####