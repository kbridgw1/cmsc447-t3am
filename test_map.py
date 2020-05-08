import cmsc447app as mainApp
import pytest
import map_new as mapNew
#import districtingscript as DS

# testing of the map function all functions must start with test_ this is how 
# pytest knows where to look and what to run
def test_map():
    #create new map
    newMap = mapNew.Map()
    # assert checks to make sure the values in the map are not null
    # if they are NULL/ None then they are not loaded properly
    assert  newMap.save != None, "map not saved"
    assert  newMap != None, "map not loaded properly"

    """"
    #attempted to run more test on other functions but there is a hard coded path
    def district_init_test(self):
        dSctripObj = DS.District(4)
        initError = 0
        if(dSctripObj.districtNum != 4): 
            initError += 1
            self.errorCount += 1
            self.errorSummary.append("districtNum is not the value passed in")
            
        if(dSctripObj.numRepublicans != 0):
            initError += 1
            self.errorCount += 1
            self.errorSummary.append("number of rep is not set to 0")
            
        if(dSctripObj.numDemocrats != 0):
            initError += 1
            self.errorCount += 1
            self.errorSummary.append("number of dem is not set to 0")
            
        if(initError == 0):
            self.errorSummary.append("distric init passed test")

    """
test_map()