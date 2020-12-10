##################################################################################################
#this script can be used to automate the forkflow: from .rvt file to building scene layer package
#using arcgis.gis and arcpy pachages and tools.  
#author                 : Khaled Alhoz
#supervisor             : Niels van der Vaart 
#date 					: 15-Nov-2020		
##################################################################################################

# **importing required Modules**
import time 
import arcpy
import os
import shutil
import arcgis.gis 
from   arcgis.gis import GIS
from   time       import strftime
from   datetime   import datetime

def CreateBSLpackage(workSpaceEnv = None, GDBfolder_name    = r"AutomationGDB.gdb",\
	out_FeatureDataset= r"Building_A"   , spatial_reference = r"RD New", \
	Rvt_directory     = None            , BSL_name          = r"BSLpackage.slpk",\
	nameOfBuildingL   = r"BuildL_A"     , includeDate       = False):
    
	
	""" 
	Function 1: CreateBSLpackage():
	This function creates BSL packages from a local revit folders
	and it store it in a desired local folder
	"""
	# checking if workspace environment and rvt file directory correct
	if not os.path.exists(workSpaceEnv) :raise NotADirectoryError(r"Directory for workSpaceEnv is incorrect or doesn't exist")
	if not os.path.isfile(Rvt_directory):raise NotADirectoryError(r"Directory to the Rvt file is incorrect or it doesn't exist")
	arcpy.AddMessage ("Directories of workspace and rvt are found")
	# Set local variables
	out_gdb_path    = workSpaceEnv + "\\" + GDBfolder_name
	# Set workspace
	arcpy.env.workspace = workSpaceEnv
	arcpy.AddMessage ("workspace is set")

	# Create a file geodatabase for the feature dataset
	arcpy.env.overwriteOutput = True
	arcpy.CreateFileGDB_management(workSpaceEnv , GDBfolder_name)
	arcpy.AddMessage ("File geodatabase is created.\n Next: Importing revit data into geodatabase...")
	# **BIMFileToGeodatabase**
	# Execute BIMFileToGeodatabase  
	arcpy.BIMFileToGeodatabase_conversion( Rvt_directory   , 
	                                      out_gdb_path     , out_FeatureDataset, 
	                                      spatial_reference)
	arcpy.AddMessage ("BIM file is imported into the geodatabase.\n Next: Making Building Layer")

	##############################################################
	#####example of making some changes on the database if desired
	#####this part will remain commented  
	##############################################################
	"""
	arcpy.env.workspace = out_gdb_path
	datasets = arcpy.ListDatasets(feature_type='feature')
	print (datasets)
	featuresClassesList = arcpy.ListFeatureClasses(feature_dataset=datasets[0]  )
	print (featuresClassesList)
	for i in range (len(featuresClassesList)//2):
		arcpy.management.Delete(featuresClassesList[i])
	featuresClassesList = arcpy.ListFeatureClasses(feature_dataset=datasets[0]  )
	print (featuresClassesList)
	"""

	# Set Overwrite option
	arcpy.env.overwriteOutput = True
	feature_dataset = out_gdb_path + "\\" + out_FeatureDataset
	# Make a building layer from a Dataset

	arcpy.MakeBuildingLayer_management(feature_dataset, nameOfBuildingL)
	arcpy.AddMessage ("The following Building Layer is made: {}".format(nameOfBuildingL))

	# Create a building Scene layer package
	if includeDate:
		now = datetime.now()
		day = now.strftime("%Y%m%d")
		BSL_name = BSL_name[:-5] + day + BSL_name[-5:]
	arcpy.AddMessage (" Next: Creating BSL package with name ({})".format(BSL_name))
	slpk = arcpy.CreateBuildingSceneLayerPackage_management(nameOfBuildingL, BSL_name, spatial_reference)
	arcpy.AddMessage ("Finsihed creating the following Building Scene Layer package {}".format(slpk))
	
	return slpk

def publishBSLfunction(itemID_BSLp = None, itemID_Hosted=None, dictOfPackageLayer = {}, DirectoryTo_SLPK = None ):

	""" in this part of the code we will be accessing Web GIS and publish it into ArcGIS Online"""

	gis = GIS("pro") # accessing ArcGIS online 
	arcpy.AddMessage ("Logged in as {}".format(gis.properties.user.username))
	
	
	if itemID_BSLp is None:
		arcpy.AddMessage ("There is no itemID of type:Scene Package provided")
		arcpy.AddMessage ("Uploading BSL Package....")
		slpk_item = gis.content.add(item_properties = dictOfPackageLayer, data= DirectoryTo_SLPK)
		arcpy.AddMessage ("Publishing the updloaded Building Scene Layer package.....")
		slpk_published = slpk_item.publish()
		arcpy.AddMessage (r"work done")
		return

	itemPackage = gis.content.get(itemID_BSLp)
	if itemID_Hosted is None:
		itemHosted  = gis.content.search(query=itemPackage.title, item_type="Scene Layer")
	else:
		itemHosted  = gis.content.get(itemID_Hosted) 
		itemHosted  = [itemHosted]

	if len(itemHosted) > 0:
		for itemL in itemHosted:
			if itemL["title"] == itemPackage["title"]:
				itemHosted = itemL
		if type (itemHosted) is list: 
			arcpy.AddMessage ("Couldn't find the correct (Hosted) item: many items holds the same title")
			return None
		arcpy.AddMessage ("Working on the following Layers \n1 - {} \n2 - {}".format(itemPackage, itemHosted ))

		arcpy.AddMessage ("Updating BSL Package....")
		slpk_item = gis.content.add(item_properties= dictOfPackageLayer, data= DirectoryTo_SLPK)
		# print (stop)
		# get a string of todays data
		now = datetime.now()
		day = now.strftime("%Y%m%d")
		# Update the name with the date of today
		slpk_item.update(item_properties= {"title": slpk_item["title"] + day})
		slpk_published = None
		try:
			arcpy.AddMessage ("Publishing the updated BSL package.....")
			checker = False
			slpk_published = slpk_item.publish()
			try:
				checker = arcpy.server.ReplaceWebLayer(itemHosted["id"], "Archive_" + itemHosted ["title"] + day , slpk_published["id"], "KEEP", "TRUE")
			except:
				arcpy.AddMessage ("Replacement didn't work, trying with different name")
			if not checker:
				try:
					checker = arcpy.server.ReplaceWebLayer(itemHosted["id"], "Archive_" + itemHosted ["title"] + day + "__2", slpk_published["id"], "KEEP", "TRUE")
					arcpy.AddMessage ("Hosted Layer Scuccesfully replaced")
				except:
					arcpy.AddMessage ("Replacement didn't work, this layer has already been replaced twice today")
					slpk_published.delete()
		except:
			if slpk_published is not None:
				slpk_published.delete()
			arcpy.AddMessage ("(error): \nTry to delete the following layer {} of Type \"Hosted Service\" ".format(slpk_item["title"]))
			arcpy.AddMessage ("Or run publishBSLfunction () separetely")
		slpk_item.update(item_properties= {"title": slpk_item["title"][:-len(day)]})
		arcpy.AddMessage (r"work done")

	else:
		arcpy.AddMessage ("Updating Building Scene Layer Package....")
		slpk_item = gis.content.add(item_properties = dictOfPackageLayer, data= DirectoryTo_SLPK)
		arcpy.AddMessage ("Publishing the updated Building Scene Layer Package.....")
		slpk_published = slpk_item.publish()
		arcpy.AddMessage (r"work done")
#Helper function to check if revit file at hand was last modefied since last run
def checkDateFunction(Rvt_directory="",directoryToTXTfile=""):
	checkTime = os.path.getmtime(Rvt_directory)
	with  open(directoryToTXTfile, "r+") as f:
		lines = f.read().splitlines()
		if len(lines)==0:
			f.write(str(checkTime))
			return True
		else:
			compareWith = lines[-1]
			if float (compareWith) ==checkTime:
				return False
			else:
				f.write("\n{}".format(str(checkTime)) )
				return True

if __name__ == '__main__':

	# converting the string true value into boolean True
	run_CreateBSLpackage       = arcpy.GetParameterAsText(0)
	if run_CreateBSLpackage    == "true":
		run_CreateBSLpackage   = True
	else:
		run_CreateBSLpackage   = False
	

	run_publishBSLfunction     = arcpy.GetParameterAsText(9)
	if run_publishBSLfunction  == "true":
		run_publishBSLfunction = True
	else:
		run_publishBSLfunction = False


	checkDateOfRevitFile       = arcpy.GetParameterAsText(13) # only works if you add (TimesLog.txt) file and the directory to it
	if checkDateOfRevitFile    == "true":
		checkDateOfRevitFile   = True
	else:
		checkDateOfRevitFile   = False 
	
	###########################################################################################################
	#directry to the text file in which the histoy log is stored and used for the date check of revit files####
	## see helper function:)
	directoryToTXTfile    = arcpy.GetParameterAsText(14) 

	"""required parameters and Optional parameters for the workflow
	this workflow is devided into two main parts (here functions)

	                   #################################
	                   ###Function 1 CreateBSLpackage()#
	                   #################################
	"""

	# Required
	########## 
	workSpaceEnv      =  arcpy.GetParameterAsText(1) # path to a folder to createGDB
	Rvt_directory     =  arcpy.GetParameterAsText(2) # path to rvt file 
	BSL_name          =  arcpy.GetParameterAsText(3) + ".slpk" # BSLpackage Name defaul is **BSLpackage.slpk**
	spatial_reference =  arcpy.GetParameterAsText(4)  #default is "RD New"
	nameOfBuildingL   =  arcpy.GetParameterAsText(5) #this will show on the ArcGIS online 
	# optional
	########## 
	out_FeatureDataset= arcpy.GetParameterAsText(6)
	GDBfolder_name    = arcpy.GetParameterAsText(7)  + ".gdb" #default
	includeDate       = arcpy.GetParameterAsText(8)
	if includeDate == "true":includeDate = True
	else:includeDate = False  
	####################################
	# check date if True and run the Function :CreateBSLpackage
	if checkDateOfRevitFile and run_CreateBSLpackage:
		run_CreateBSLpackage = checkDateFunction(Rvt_directory,directoryToTXTfile)
		if not run_CreateBSLpackage:
			run_publishBSLfunction = False
			arcpy.AddMessage ("The last version of the Revit file is already uploaded")

	if run_CreateBSLpackage:
		CreateBSLpackage(workSpaceEnv, GDBfolder_name       , \
			       out_FeatureDataset, spatial_reference    , Rvt_directory, BSL_name,\
				   nameOfBuildingL   , includeDate )


	#####################################################################
	#####################################################################
	#####################################################################
	"""                ###################################
	                   ###Function 2 publishBSLfunction()#
	                   ###################################
	"""
	# Required
	##########
	# converting the empty string input to Python None value
	itemID_BSLp             = arcpy.GetParameterAsText(10)
	if itemID_BSLp  =="": itemID_BSLp  = None

	itemID_Hosted           = arcpy.GetParameterAsText(11) 
	if itemID_Hosted=="": itemID_Hosted= None

	# overwrite parameter is importatnt to be set on **True** ##Only change if you know what you are doing##  
	dictOfPackageLayer      = {"overwrite" : True}
	DirectoryTo_SLPK        = arcpy.GetParameterAsText(12)
	#### this parameter is automaticlly derived from the arguments of function 1 
	#### do not change it unless you know what you are doing
	if includeDate:
		now = datetime.now()
		day = now.strftime("%Y%m%d")
		BSL_name = BSL_name[:-5] +day + BSL_name[-5:] 
	if  DirectoryTo_SLPK == "":
		DirectoryTo_SLPK  = workSpaceEnv + "\\" + BSL_name

	if run_publishBSLfunction:
		publishBSLfunction(itemID_BSLp, itemID_Hosted, dictOfPackageLayer, DirectoryTo_SLPK)