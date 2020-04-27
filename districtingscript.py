# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 17:36:02 2020

@author: Denise
"""

import shapefile
from shapely.geometry import shape
import copy
import csv

NUM_DISTRICTS = 8
DISTRICT_FNAME = 'CNG02'
DEM_FNAME = 'DEMOCRAT'
REP_FNAME = 'REPUBLICAN'
PRECINCT_FNAME = 'PRECINCT'
DISTRICT_NUM_PREFIX = 2400

# Define class for the precinct - this will have both the attributes from the 
# shapefile as well as the shapely geometry for detecting overlaps

class Precinct:
    def __init__(self, shapefileData, shapelyGeometry):
        self.sfData = shapefileData
        self.geometry = shapelyGeometry
        self.neighborsInDistrict = []
        self.neighborsOutOfDistrict = []
        
    def checkNeighbor(self,other):
        if self.geometry.touches(other.geometry):
            print('Found neighbor of ',self.sfData[PRECINCT_FNAME])
            if self.sfData[DISTRICT_FNAME] == other.sfData[DISTRICT_FNAME]:
                self.neighborsInDistrict.append(other)
                other.neighborInDistrict.append(self)
            else:
                self.neighborsOutOfDistrict.append(other)
                other.neighborsOutOfDistrict.append(self)
                
    def changeDistrict(self,newDistrict):
        oldDistrict = self.district
        self.district = newDistrict
        self.sfData[DISTRICT_FNAME] = newDistrict.districtNum
        # all neighbors that were in district are now out
        tempOut = self.neighborsInDistrict
        # Neighbors that were out of district may now be in district
        precinctsToMove = []
        for other in self.neighborsOutOfDistrict:
            if self.sfData[DISTRICT_FNAME] == other.sfData[DISTRICT_FNAME]:
                precinctsToMove.append(other)
        
        for p in precinctsToMove:
            self.neighborsOutOfDistrict.remove(p)
            self.neighborsInDistrict.append(p)   
            
        self.neighborsOutOfDistrict.extend(tempOut)
        # Add to new district and remove from old
        oldDistrict.removePrecinct(self)
        newDistrict.addPrecinct(self)
        print('Moved ',self.sfData[PRECINCT_FNAME],' from ',oldDistrict.districtNum, ' to ',newDistrict.districtNum)
            
    def assignDistrict(self,districtToAssign):
        self.district = districtToAssign
        
    
class District:
    def __init__(self, num):
        self.districtNum = num
        self.precincts = []
        self.borderPrecincts = []
        self.numRepublicans= 0
        self.numDemocrats = 0
    
    def addPrecinct(self, precinct):
        self.precincts.append(precinct)
        if len(precinct.neighborsOutOfDistrict) > 0:
            self.borderPrecincts.append(precinct)
        self.numRepublicans += precinct.sfData[REP_FNAME]
        self.numDemocrats += precinct.sfData[DEM_FNAME]
        
    def removePrecinct(self, precinct):
        self.precincts.remove(precinct)
        if precinct in self.borderPrecincts:
            self.borderPrecincts.remove(precinct)
        self.numRepublicans -= precinct.sfData(REP_FNAME)
        self.numDemocrats -= precinct.sfData(DEM_FNAME)
        
    def isDemMajority(self):
        return self.numDemocrats > self.numRepublicans
    
    def isRepMajority(self):
        return self.numRepublicans > self.numDemocrats                      
        
def AddDemocrats(DoNotTakeFromDistricts,district, precinct):
    if district.numDemocrats <= district.numRepublicans:
        i = 0
        while i < len(precinct.neighborsOutOfDistrict):
            candidate = precinct.neighborsOutOfDistrict[i]
            # If candidate district will be net addition of Democrats, 
            # check if it can be added to this district
            if candidate.sfData[DEM_FNAME] > candidate.sfData[REP_FNAME]:
                if candidate.district not in DoNotTakeFromDistricts:            
                    candidate.changeDistrict(precinct.sfData[DISTRICT_FNAME])
                    AddDemocrats(DoNotTakeFromDistricts,district, candidate)
                    
def AddRepublicans(DoNotTakeFromDistricts,district, precinct):
    if district.numRepublicans <= district.numDemocrats:
        i = 0
        while i < len(precinct.neighborsOutOfDistrict):
            candidate = precinct.neighborsOutOfDistrict[i]
            # If candidate district will be net addition of Republicans, 
            # check if it can be added to this district
            if candidate.sfData[DEM_FNAME] > candidate.sfData[REP_FNAME]:
                if candidate.district not in DoNotTakeFromDistricts:            
                    candidate.changeDistrict(precinct.sfData[DISTRICT_FNAME])
                    AddRepublicans(DoNotTakeFromDistricts,district, candidate)

def writePrecinctsToCSV(filename, precinctList):
    with open(filename, mode = 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter = ',', quotechar = '"')
        csvWriter.writerow(['PRECINCT','DISTRICT'])
        for p in precinctList:
            csvWriter.writerow([p.sfData[PRECINCT_FNAME], p.sfData[DISTRICT_FNAME]])
        
# Initialize empty disctricts
districts = []
for i in range(NUM_DISTRICTS):
    districts.append(District(i + DISTRICT_NUM_PREFIX))
    
# Use pyshp library to read the shapefile
sfRecords = shapefile.Reader("C:/Users/Denise/Documents/CMSC 426/Precinct2010_83NadMeters")

precincts = []
# Create a precinct object for each entry in the shapefile
for i in range(len(sfRecords.shapes())):
    sfRecord = sfRecords.shapeRecords()[i]
    recordData = sfRecord.record
    sfShape = sfRecord.shape.__geo_interface__
    recordShape = shape(sfShape)
    precincts.append(Precinct(recordData, recordShape))
    print('Added precinct ', i)
    
# Create temporary variable so precincts aren't double-evaluated
tempPrecincts = precincts
while len(tempPrecincts) > 0:
    p1 = tempPrecincts[0]
    tempPrecincts.remove(p1)
    # Find all the neighbors
    for p2 in tempPrecincts:
        p1.checkNeighbor(p2)
    # Assign to the appropriate district
    districtNum = p1.sfData[DISTRICT_FNAME]
    district = districts[districtNum]
    district.addPrecinct(p1)
    p1.assignDistrict(district)

# Backup original distribution
orig_districts = copy.deepcopy(districts)

# Redistrict to Republican majority
demMajorityDistricts = []
repMajorityDistricts = []
minChangeNeeded = 0
minChangeDistrict = []
for d in districts:
    if d.numDemocrats > d.numRepublicans:
        demMajorityDistricts.append(d)
        if (d.numRepublicans - d.numDemocrats) < minChangeNeeded:
            minChangeDistrict.append(d)
    else:
        repMajorityDistricts.append(d)
        
# Republican majority districts must be more than half the districts to satisfy criteria
while len(repMajorityDistricts) < (NUM_DISTRICTS / 2):
    # Start with the district that has the minimum change needed
    i = 0
    while i < len(minChangeDistrict.borderPrecincts):
        while not minChangeDistrict.isDemMajority():
            AddRepublicans(demMajorityDistricts,minChangeDistrict,minChangeDistrict.borderPrecincts[i])
            i += 1
    demMajorityDistricts.remove(minChangeDistrict)
    repMajorityDistricts.append(minChangeDistrict)
    
writePrecinctsToCSV('RepublicanRedistricting',precincts)

# Redistrict to Democratic majority
demMajorityDistricts = []
repMajorityDistricts = []
minChangeNeeded = 0
minChangeDistrict = []
for d in districts:
    if d.numRepublicans > d.numDemocrats:
        repMajorityDistricts.append(d)
        if (d.numDemocrats - d.numRepublicans) < minChangeNeeded:
            minChangeDistrict.append(d)
    else:
        demMajorityDistricts.append(d)
        
# Democratic majority districts must be more than half the districts to satisfy criteria
while len(demMajorityDistricts) < (NUM_DISTRICTS / 2):
    # Start with the district that has the minimum change needed
    i = 0
    while i < len(minChangeDistrict.borderPrecincts):
        while not minChangeDistrict.isDemMajority():
            AddDemocrats(demMajorityDistricts,minChangeDistrict,minChangeDistrict.borderPrecincts[i])
            i += 1

writePrecinctsToCSV('DemocratRedistricting',precincts)     

# Redistrict to swing majority
demMajorityDistricts = []
repMajorityDistricts = []
minChangeNeeded = 0
minChangeDistrict = []
for d in districts:
    if d.numRepublicans > d.numDemocrats:
        repMajorityDistricts.append(d)
        if (d.numDemocrats - d.numRepublicans) < minChangeNeeded:
            minChangeDistrict.append(d)
    else:
        demMajorityDistricts.append(d)
        
# Democratic majority districts must be equal to half the districts to satisfy criteria
#while len(demMajorityDistricts) != (NUM_DISTRICTS / 2):
    # Start with the district that has the minimum change needed
#    i = 0
#    while i < len(minChangeDistrict.borderPrecincts):
#        while not minChangeDistrict.isDemMajority():
#            AddDemocrats(demMajorityDistricts,minChangeDistrict,minChangeDistrict.borderPrecincts[i])
#            i += 1

#writePrecinctsToCSV('DemocratRedistricting',precincts)  
    
    
        

    
        
    