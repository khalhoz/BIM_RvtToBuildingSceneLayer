# RvtToBuildingScnenLayer - Automation
This script can be to run to execute the workflow of converting a Revit Building model into Building Scene Layer package then upload it into ArcGIS online server as Scene Layer (Hosted) <br/>
<br/>
**workflow:**
* Creating geodatabase folder in your local machine
* Importing Revit data into the geodatabase created
* If desired making some changes
* Making Building Layer
* Creating Building Scene Layer Package (.slpk)
* Uploading (or updating) the created Building Scene Layer Package (.slpk file) into ArcGIS Online
* Finally, publishing (or replacing) it as Scene Layer (Hosted) 

**Parameterization**
1. Function 1 arguments:
> Required 
* workSpaceEnv      = r"C:\user\AutoFolder"   #path to a folder in which a .gdb is created
* Rvt_directory     = r"C:\Users\Berging.rvt" #path to rvt file 
* BSL_name          = r"BSLpackageTest.slpk"  #defaul is BSLpackage.slpk
* spatial_reference = r"RD New"               #default is "RD New"
* nameOfBuildingL   = r"BuildL_A"             #this name will show on the ArcGIS online 
> Optional
* out_FeatureDataset= r"Building_A"           #default "Building_A"
* includeDate       = False                   #Include date of the day in the returned slpk file e.g. (name20202112.slpk)
2. Function 2 arguments:
* 
