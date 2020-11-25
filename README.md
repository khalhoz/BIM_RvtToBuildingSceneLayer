# RvtToBuildingScnenLayer - Automation
This script can be to run to execute the workflow of converting a Revit Building model into Building Scene Layer package then upload it into ArcGIS online server as Scene Layer (Hosted) <br/>
The repository contains this file and a Python file named **BIMpublication** and a (.bat) file named **runPythonScript**
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
+ Function 1 **"def CreateBSLpackage()"** arguments:
> Required 
  1. workSpaceEnv      = r"C:\user\AutoFolder"   #path to a folder in which a .gdb file is created
  2. Rvt_directory     = r"C:\Users\Berging.rvt" #path to rvt file 
  3. BSL_name          = r"BSLpackageTest.slpk"  #defaul is BSLpackage.slpk
  4. spatial_reference = r"RD New"               #default is "RD New"
  5. nameOfBuildingL   = r"BuildL_A"             #this name will show on the ArcGIS online 
> Optional
  6. out_FeatureDataset= r"Building_A"           #default "Building_A"
  7. includeDate       = False                   #Include date of the day in the returned slpk file e.g. (name20202112.slpk)
+ Function 2 **"def publishBSLfunction()"** arguments:
> Required
  1. DirectoryTo_SLPK = None                    # if not provided the script will try derive it from the arguments of function 1 (if provided)
  2. itemID_BSLp  = "itemID"                    # if not provided the program will simply upload the Building Scene Layer Package provided 
  3. itemID_Hosted= "itemID"                    # if not provided the program will search for Scene Layer that holds the same name and replace it. If not found 
  it will publish a new one. In this [blog](https://community.esri.com/t5/arcgis-online-blog/where-can-i-find-the-item-id-for-an-arcgis-online-item/ba-p/890284#:~:text=Find%20the%20Layers%20section%2C%20click,ID%20in%20the%20address%20bar.) you can find a tutorial on how to get an item_id from ArcGIS Online.
  4. dictOfPackageLayer             = #dictionary: Value Dictionary Options for the item_properties argument: <br/> **example:** {"overwrite" : True, "tags" : ["ArcGIS", "BuildingSceneLayer", "revit"], "snippet": "Here goes the description about your Building Scene Layer Package"} <br/>
  **overwrite** parameter is importatnt to be set on **True** ##Only change if you know what you are doing; [here](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.ContentManager.add) you can find full explaination on the values that can be used##
  This dictionary can be used to update the Building Scene Layer Pckage/Scene Layer (Hosted) item_properties details/information such as title, tags etc. However, it is advised to use [**Update()**](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.ContentManager.add) method as it performs faster after publishing. 

