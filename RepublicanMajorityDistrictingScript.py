# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 17:36:02 2020

@author: Denise
"""

import shapefile
from shapely.geometry import shape
import copy
import csv
import math

NUM_DISTRICTS = 8
DISTRICT_FNAME = 'CNG02'
DEM_FNAME = 'DEMOCRAT'
REP_FNAME = 'REPUBLICAN'
PRECINCT_FNAME = 'PRECINCT'
totalVoters = 0

# Define class for the precinct - this will have both the attributes from the 
# shapefile as well as the shapely geometry for detecting overlaps

class Precinct:
    def __init__(self, shapefileRecord, shapefileShape, shapelyGeometry):
        self.sfData = shapefileRecord
        self.shape = shapefileShape
        self.geometry = shapelyGeometry
        self.neighbors = []
        self.neighborsOfOppMaj = []
        self.neighborsOfSameMaj = []
        # Initialized to have no district
        self.district = 0
                
    def checkNeighbor(self,other):
        if self.geometry.touches(other.geometry):
            self.neighbors.append(other)
            other.neighbors.append(self)
            # Check for neighbors that have opposite majority
            if self.getMajority() != other.getMajority():
                self.neighborsOfOppMaj.append(other)
                other.neighborsOfOppMaj.append(self)
            else:
                self.neighborsOfSameMaj.append(other)
                other.neighborsOfSameMaj.append(self)
    
    def getMajority(self):
        if self.sfData[DEM_FNAME] > self.sfData[REP_FNAME]:
            return DEM_FNAME
        else:
            return REP_FNAME
        
class District:
    def __init__(self, num):
        self.districtNum = num
        self.precincts = []
        self.borderPrecincts = []
        self.numRepublicans= 0
        self.numDemocrats = 0
    
    def addPrecinct(self, precinct):
        self.precincts.append(precinct)
        self.numRepublicans += precinct.sfData[REP_FNAME]
        self.numDemocrats += precinct.sfData[DEM_FNAME]
        precinct.district = self.districtNum
        
    def removePrecinct(self, precinct):
        self.precincts.remove(precinct)
        if precinct in self.borderPrecincts:
            self.borderPrecincts.remove(precinct)
        self.numRepublicans -= precinct.sfData(REP_FNAME)
        self.numDemocrats -= precinct.sfData(DEM_FNAME)
       
    def getMajority(self):
        if self.numDemocrats > self.numRepublicans:
            return DEM_FNAME
        else:
            return REP_FNAME
    
    def isDemMajority(self):
        return self.numDemocrats > self.numRepublicans
    
    def isRepMajority(self):
        return self.numRepublicans > self.numDemocrats                      
        
    def PrintSummary(self):
        print('District ', self.districtNum, '-  Democrat: ', self.numDemocrats, " Republican: ", self.numRepublicans)

def MaxDemMajInDistrict(district, frontier, precinct):
    if district.numDemocrats + district.numRepublicans < maxDistrictSize:
        district.addPrecinct(precinct)
        # Frontier should be a list - add the neighbors of the precinct to it
        for neighbor in precinct.neighbors:
            if neighbor.district == 0:
                frontier.append(neighbor)
        # Don't want to get burned by an empty frontier
        if len(frontier) > 0:
            # Now sort the frontier by highest Democratic majority
            frontier.sort(key=lambda x: x.sfData[DEM_FNAME] - x.sfData[REP_FNAME], reverse=True)
            # Add the best of the frontier to the district
            MaxDemMajInDistrict(district, frontier, frontier.pop(0))      
        
def MaxRepMajInDistrict(district, frontier, precinct, recursionNum):
    print('MaxRepMajInDistrict recursion number ', recursionNum)
    print('District ', district.districtNum, ' now has:')
    district.PrintSummary()
    if district.numDemocrats + district.numRepublicans < minDistrictSize:
        district.addPrecinct(precinct)
        print('Added precinct ', precinct.sfData[PRECINCT_FNAME], " to district ", district.districtNum)
        for neighbor in precinct.neighbors:
            if neighbor.district == 0:
                print('Expanded frontier...')
                frontier.append(neighbor)
        # Now sort frontier by least Repubican majority
        frontier.sort(key=lambda x: x.sfData[REP_FNAME] - x.sfData[DEM_FNAME])
        print('Sorted frontier')
        while len(frontier) > 0:
            f = frontier.pop(0)
            newDemNum = district.numDemocrats + f.sfData[DEM_FNAME]
            newRepNum = district.numRepublicans + f.sfData[REP_FNAME]
            # Don't want to ruin Republican majority of district
            if newRepNum > newDemNum:
                MaxRepMajInDistrict(district, frontier, f, recursionNum + 1)
    print('Returning from recursionNum ', recursionNum)
    
def writePrecinctsToCSV(filename, precinctList):
    with open(filename, mode = 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter = ',', quotechar = '"')
        csvWriter.writerow(['PRECINCT','DISTRICT'])
        for p in precinctList:
            csvWriter.writerow([p.sfData[PRECINCT_FNAME], p.sfData[DISTRICT_FNAME]])
        
# Initialize empty districts
# Initialize an empty dictionary to hold the districts
districts = {}
    
# Use pyshp library to read the shapefile
sfRecords = shapefile.Reader("C:/Users/Denise/Documents/CMSC 447/UpdateStupidFiles/Precinct2010_83NadMeters")

precincts = []
i = 0
# Create a precinct object for each entry in the shapefile
for shaperec in sfRecords.iterShapeRecords():
    sfShape = shaperec.shape.__geo_interface__
    recordShape = shape(sfShape)
    precincts.append(Precinct(shaperec.record, shaperec.shape, recordShape))
    print('Added precinct ', i)
    i += 1
        
#for i in range(len(sfRecords.shapes())):
 #   sfRecord = sfRecords.shapeRecords()[i]
  #  recordData = sfRecord.record
   # sfShape = sfRecord.shape.__geo_interface__
    #recordShape = shape(sfShape)
    #precincts.append(Precinct(recordData, recordShape))
    #print('Added precinct ', i)
    
# Determine which precincts are neighbors
# Create temporary variable so precincts aren't double-evaluated
repPrecincts = []
demPrecincts = []
demsWithRepNeighbors = []
repsWithDemNeighbors = []
demSurroundedBySame = []
repSurroundedBySame = []
tempPrecincts = precincts
while len(tempPrecincts) > 0:
    p1 = tempPrecincts[0]
    tempPrecincts.remove(p1)
    # Find all the neighbors
    for p2 in tempPrecincts:
        p1.checkNeighbor(p2)
    if p1.getMajority() == DEM_FNAME:
        demPrecincts.append(p1)
        if len(p1.neighborsOfOppMaj) > 0:
            print(p1.sfData[PRECINCT_FNAME], ' is ', p1.getMajority(), ' with different neighbors')
            demsWithRepNeighbors.append(p1)
        else:
            demSurroundedBySame.append(p1)
    if p1.getMajority() == REP_FNAME:
        repPrecincts.append(p1)
        if len(p1.neighborsOfOppMaj) > 0:
            print(p1.sfData[PRECINCT_FNAME], ' is ', p1.getMajority(), ' with different neighbors')
            repsWithDemNeighbors.append(p1)
        else:
            repSurroundedBySame.append(p1)
    # Add voters to total count
    totalVoters += p1.sfData[REP_FNAME]
    totalVoters += p1.sfData[DEM_FNAME]

# Try to allocate as many Democratic majority precincts as possible to just under half the districts
numDemDistrictsNeeded = math.floor(NUM_DISTRICTS / 2)
if numDemDistrictsNeeded % 2 == 0:
    numDemDistrictsNeeded -= 1
# We can make these districts a little larger to use up more Dem majority precincts
maxDistrictSize = round(1.2 * totalVoters / NUM_DISTRICTS)
minDistrictSize = round(.8 * totalVoters / NUM_DISTRICTS)
numDemDistricts = 0
districts = []
while (numDemDistricts < numDemDistrictsNeeded):
    district = District(len(districts) + 1)
    districts.append(district)
    numDemDistricts += 1
    print('Creating Democratic district ', numDemDistricts)
    # Choose a precinct from the list of Democratic districts surrounded by only Democratic districts
    # and add it to the new district
    frontier = []
    while len(demsWithRepNeighbors) > 0:
        if district.numDemocrats + district.numRepublicans > maxDistrictSize:
            break
        MaxDemMajInDistrict(district, frontier, demSurroundedBySame.pop())
    district.PrintSummary()
    
# Now attempt to create remaining districts as Republican majority
while (len(districts) < NUM_DISTRICTS):
    district = District(len(districts) + 1)
    districts.append(district)
    frontier = []
    print('Creating district ', len(districts))
    while len(repsWithDemNeighbors) > 0:
        if district.numDemocrats + district.numRepublicans >= minDistrictSize:
            break
        precinct = repsWithDemNeighbors.pop()
        if precinct.district == 0:
            MaxRepMajInDistrict(district, frontier, precinct, 0)
    # If we didn't get enough... I don't know what now...
    if district.numDemocrats + district.numRepublicans < minDistrictSize:
        print('Ran out of stuff in the RepWithDemNeighbors list...')
        for p in district.precincts:
            frontier = []
            MaxRepMajInDistrict(district, frontier, precinct, 0)
    district.PrintSummary()   

# Print summary of districts
print('District Summary')
for d in districts:
    d.PrintSummary()     
    
# Now check for orphans
orphanPrecincts = []
for p in precincts:
    if p.district == 0:
        orphanPrecincts.append(p)
print('Number of orphan precincts: ', len(orphanPrecincts))

# Write a new shapefile for the distribution
w = shapefile.Writer("C:/Users/Denise/Documents/CMSC 447/UpdateStupidFiles/RepublicanMajority",shapeType=shapefile.POLYGON)
for p in precincts:
    p.sfData[DISTRICT_FNAME] = p.district
    w.record(p.sfData)
    w.shape(p.shape)
w.close()
  
