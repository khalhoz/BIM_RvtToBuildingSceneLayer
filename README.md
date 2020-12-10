# RvtToBuildingScnenLayer - Automation
This script can be used to execute the workflow - **converting a Revit building model into Building Scene Layer package then upload it into ArcGIS Online server and publish it as Scene Layer (Hosted)** <br/>
This code is meant to be a starting work-frame from which you can develop your pipeline in similar or related workflows. 
It still can be used to execute the exact workflow mentioned, however for it to run you need to be automatically logged in in ArcGIS Pro. Otherwise, you should adjust the code in the Authentication part to grant access to ArcGIS Online content. For more information about the workflow and the code, refer to this [Story Map](https://storymaps.arcgis.com/stories/3c2c29a8ff544db5a6df94d936430bd6).
<br/>
Moreover, the repository contains a Python script toolbox (geoprocessing toolbox). This is created and derived using the same Python script and can be used directly in ArcGIS Pro to run the same worflow. For more details about the toolbox, refer to the following [blog](https://community.esri.com/t5/arcgis-pro-blog/creating-geoprocessing-python-toolboxes-and-automating-your/ba-p/1007339)  

### The repository contains the following 
1. This file **README.md**
2. LICENCE
    #### Files for automating a standalone script
3. A Python file named `BIMpublication` # this is the main Python Script that can be used direcly or modified to fit your workflow
4. A (.bat) file named `runPythonScript` #this can be used for automating using [Task Scheduler](https://datatofish.com/python-script-windows-scheduler/)
5. A txt file named `TimesLog.txt`#this file is used for the helper function **checkDateFunction()**
    #### Files for automating in ArcGIS Pro
6. A toolbox named `BIMpublicationToolbox` #this toolbox (the script is embedded) can be used directly in ArcGIS Pro and it runs the exact workflow mentioned above. 
7. A Python file named `BIMpublicationScriptToolVerssion` #this script is a copy of BIMpublication.py, however it is adjusted to be read by the toolbox. This file can be used to develop the Geoprocessing tool to fit your workflow if you wish to.

### **workflow:**
+ Check if a revit file has been modifed since the last run #optional: using helper function
+ Creating geodatabase folder in your local machine
+ Importing Revit data into the geodatabase created
+ If desired making some changes
+ Making Building Layer
+ Creating Building Scene Layer Package (.slpk)
+ Uploading (or updating) the created Building Scene Layer Package (.slpk file) into ArcGIS Online
+ Finally, publishing (or replacing) it as Scene Layer (Hosted) 

### **Parameterization**
#### + Function 1 **`"def CreateBSLpackage()"`** arguments:
> Required 
  1. workSpaceEnv      = r"C:\user\AutoFolder"   #path to a folder in which a .gdb file is created
  2. Rvt_directory     = r"C:\Users\Berging.rvt" #path to rvt file 
  3. BSL_name          = r"BSLpackage.slpk"  #defaul is BSLpackage.slpk
  4. spatial_reference = r"RD New"               #default is "RD New"
  5. nameOfBuildingL   = r"BuildL_A"             #this name will show on the ArcGIS online 
> Optional
  6. out_FeatureDataset= r"Building_A"           #default "Building_A"
  7. includeDate       = False                   #Include date of the day in the returned slpk file e.g. (name20202112.slpk) <br/>
  
#### + Function 2 **`"def publishBSLfunction()"`** arguments:
> Required
  1. DirectoryTo_SLPK = None                    # if not provided the script will try derive it from the arguments of function 1 (if provided)
  2. itemID_BSLp  = "itemID"                    # if not provided the program will simply upload the Building Scene Layer Package provided 
  3. itemID_Hosted= "itemID"                    # if not provided the program will search for Scene Layer that holds the same name and replace it. If not found 
  it will publish a new one. In this [blog](https://community.esri.com/t5/arcgis-online-blog/where-can-i-find-the-item-id-for-an-arcgis-online-item/ba-p/890284#:~:text=Find%20the%20Layers%20section%2C%20click,ID%20in%20the%20address%20bar.) you can find a tutorial on how to get an item_id from ArcGIS Online.
  4. dictOfPackageLayer             = #dictionary: Value Dictionary Options for the item_properties argument: <br/> **example:** {"overwrite" : True, "tags" : ["ArcGIS", "BuildingSceneLayer", "revit"], "snippet": "Here goes the description about your Building Scene Layer Package"} <br/>
  **overwrite** parameter is importatnt to be set on **True** ##Only change if you know what you are doing; [here](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.ContentManager.add) you can find full explaination on the values that can be used##
  This dictionary can be used to update the Building Scene Layer Pckage/Scene Layer (Hosted) item_properties details/information such as title, tags etc. However, it is advised to use [**Update()**](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.ContentManager.add) method as it performs faster after publishing. 

### example of using the function in Python

```
import BIMpublication

# create building scene layer function
# Required
########## 
workSpaceEnv      =  r"C:\Users\username\Desktop\AutomationTest" 
Rvt_directory     =  r"C:\Users\username\Desktop\AutomationTest\revitFiles\171025_BLOKA.rvt" 
BSL_name          =  r"BSLpackage.slpk" 
spatial_reference =  r"RD New" 
nameOfBuildingL   =  r"BuildL_Anew" #this name will show on the ArcGIS online
# optional
########## 
out_FeatureDataset= r"Building_A"
GDBfolder_name    = r"Automation.gdb" #default
includeDate       = False 
BIMpublication.CreateBSLpackage(workSpaceEnv, GDBfolder_name       , \
			       out_FeatureDataset, spatial_reference    , Rvt_directory, BSL_name,\
				   nameOfBuildingL   , includeDate )


# Publish Building scene layer function
# Required parameters 
##########
itemID_BSLp             = None 
itemID_Hosted           = None
# overwrite parameter is importatnt to be set on **True** ##Only change if you know what you are doing##  
dictOfPackageLayer      = {"overwrite" : True}
DirectoryTo_SLPK        = None
BIMpublication.publishBSLfunction(itemID_BSLp, itemID_Hosted, dictOfPackageLayer, DirectoryTo_SLPK)
```
