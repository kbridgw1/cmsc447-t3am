# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 17:36:02 2020

@author: Denise
"""

import shapefile
from shapely.geometry import shape
from shapely.ops import unary_union
import csv
import math
from array import array
from geojson import Point, Feature, FeatureCollection, dump


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
        self.neighborsInSameDistrict = []
        self.neighborsInOtherDistrict = []
        self.orphanNeighbors = []
        # Initialized to have no district
        self.district = None
                
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
                
    def getCounty(self):
        splitName = self.sfData['NAME']
        return splitName[0]
                
    def getMajority(self):
        if self.sfData[DEM_FNAME] > self.sfData[REP_FNAME]:
            return DEM_FNAME
        else:
            return REP_FNAME
        
    def findAdopter(self):
        # Look through its neighbors to see if it can join the same district
        for neighbor in self.neighbors:
            # The neighbor might also be an orphan...
            if neighbor.district != None:
                # If majoirty of district and precinct are the same - no problem!
                if self.getMajority() == neighbor.district.getMajority():
                    neighbor.district.addPrecinct(orphan)
                    print('Orphan assigned to district with same majority')
                    break        
                else:
                    # Can join a district of a different majority as long as it doesn't change the majority
                    print('Neighbors are in district of different majority...')
                    if neighbor.district.getMajority() == neighbor.district.tentativeAddPrecinct(orphan):
                        print('Assigned to district of different majority')
                        neighbor.district.addPrecinct(orphan)                    
                    else:
                        print('Assigning to this district would ruin desired majority')
                        print('Trying to swap precincts...')
                        # Try to swap along the border of the district
                        district = neighbor.district
                        for p1 in district.precincts:
                            # Examine the neighbors of the precinct to see if it is on the border
                            for p2 in p1.neighbors:
                                if p2.district != None and p2.district != p1.district:
                                    # p1 is on the border of its district
                                    # Can we move this precinct into the other district?
                                    if p2.district.getMajority() == p2.district.tentativeAddPrecinct(p1):
                                        print('Border precinct could be moved into other district')
                                        # Does this make it possible to move in the orphan
                                        if p2.district.testReplace(self, p1):
                                            print('Precinct can be replaced to allow orphan')
                                            district.addPrecinct(self)
                                            district.removePrecinct(p1)
                                            p2.district.addPrecinct(p1)    
                                            return
            else:
                print('Neighbor is also an orphan')       
        
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
        precinct.district = self
        
    def tentativeAddPrecinct(self, precinct):
        newNumDemocrats = self.numDemocrats + precinct.sfData[DEM_FNAME]
        newNumRepublicans = self.numRepublicans + precinct.sfData[REP_FNAME]
        if newNumDemocrats > newNumRepublicans:
            return DEM_FNAME
        else:
            return REP_FNAME
        
    def removePrecinct(self, precinct):
        self.precincts.remove(precinct)
        precinct.district = None
        self.numRepublicans -= precinct.sfData[REP_FNAME]
        self.numDemocrats -= precinct.sfData[DEM_FNAME]
        
    def testReplace(self, precinctIn, precinctOut):
        newNumDemocrats = self.numDemocrats - precinctOut.sfData[DEM_FNAME] + precinctIn.sfData[DEM_FNAME]
        newNumRepublicans = self.numRepublicans - precinctOut.sfData[REP_FNAME] + precinctIn.sfData[REP_FNAME]
        if newNumDemocrats > newNumRepublicans:
            return DEM_FNAME
        else:
            return REP_FNAME
        
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
            if neighbor.district == None:
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
            if neighbor.district == None:
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
        csvWriter.writerow(['NAME','DISTRICT'])
        for p in precinctList:
            csvWriter.writerow([p.sfData['NAME'], p.sfData[DISTRICT_FNAME]])
        
# Initialize empty districts
# Initialize an empty dictionary to hold the districts
districts = {}
    
# Use pyshp library to read the shapefile
sfRecords = shapefile.Reader("OriginalDistribution")

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
tempPrecincts = precincts.copy()
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
    while len(demSurroundedBySame) > 0:
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
        if precinct.district == None:
            MaxRepMajInDistrict(district, frontier, precinct, 0)
    # If we didn't get enough... I don't know what now...
    if district.numDemocrats + district.numRepublicans < minDistrictSize:
        print('Ran out of stuff in the RepWithDemNeighbors list...')
        for p in district.precincts:
            frontier = []
            MaxRepMajInDistrict(district, frontier, precinct, 0)
    district.PrintSummary()   
   
# Now check for orphans
orphanPrecincts = []
for p in precincts:
    if p.district == None:
        orphanPrecincts.append(p)
print('Number of orphan precincts: ', len(orphanPrecincts))
origNumOrphans = len(orphanPrecincts)

while len(orphanPrecincts) > 0:
    # Oh great. There are orphans. Now what do we do with them... 
    # Shove them in the same district as one of their neighboring precincts, 
    # trying not to mess up the majority of that district
    for orphan in orphanPrecincts:
        # Look through its neighbors and find a district that has the same majority
        for n in orphan.neighbors:
            n.findAdopter()
        if orphan.district == None:
            print('Could not assign the orphan to a district')
    
    # Recheck orphans        
    orphanPrecincts = []
    for p in precincts:
        if p.district == None:
            orphanPrecincts.append(p)
            
    numAdopted = origNumOrphans - len(orphanPrecincts)
    if numAdopted == 0:
        print('Could not assign any orphans to a district')
        break
    else:
        print('Orphan precincts reduced by ', origNumOrphans - len(orphanPrecincts))
        origNumOrphans = len(orphanPrecincts)
        
# There are still orphans... Because some precincts have no neighbors
# Maybe try to add them to the same district as other precincts in the same county
for orphan in orphanPrecincts:
    # The county is the first word in the precinct name
    for p in precincts:
        # If not comparing to itself and compared precinct is in same county
        if orphan != p and (orphan.getCounty() == p.getCounty()):
            # If adding to the district wouldn't mess it up
            if p.district != None and (p.district.getMajority() == p.district.tentativeAddPrecinct(orphan)):
                p.district.addPrecinct(orphan)
    if orphan.district == None:
        print('Precinct is still an orphan :-(')    

orphanPrecincts = []
for p in precincts:
    if p.district == None:
        orphanPrecincts.append(p)
        
# Create a dictionary of lists to hold the precinct shapes for each district
districtPrecinctShapes = {}
for d in districts:
    districtPrecinctShapes[d.districtNum] = []
    
for p1 in precincts:
    p1.sfData[DISTRICT_FNAME] = p1.district.districtNum
    # Add shape to the appropriate district
    districtPrecinctShapes[p1.district.districtNum].append(p1.geometry)
writePrecinctsToCSV('RepublicanRedistricting1.csv',precincts)       

# Now try creating GeoJSON file of new district outlines from merged precincts...
features = []
for d1 in districtPrecinctShapes:
    mergedDistrict = unary_union(districtPrecinctShapes[d1])
    features.append(mergedDistrict)
    
feature_collection = FeatureCollection(features)

with open('RepublicanMajority.geojson', 'w') as f:
   dump(feature_collection, f)

# Print summary of districts
print('District Summary')
for d in districts:
    d.PrintSummary()     

