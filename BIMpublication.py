##################################################################################################
#this script can be used to automate the forkflow: from .rvt file to building scene layer package
#using arcgis.gis and arcpy pachages and tools.  
#author     : Khaled Alhoz
#supervisor : Niels van der Vaart 
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
	print ("Directories of workspace and rvt are found")
	# Set local variables
	out_gdb_path    = workSpaceEnv + "\\" + GDBfolder_name
	# Set workspace
	arcpy.env.workspace = workSpaceEnv
	print ("workspace is set")

	# Create a file geodatabase for the feature dataset
	arcpy.env.overwriteOutput = True
	arcpy.CreateFileGDB_management(workSpaceEnv , GDBfolder_name)
	print ("File geodatabase is created.\n Next: Importing revit data into geodatabase...")
	# **BIMFileToGeodatabase**
	# Execute BIMFileToGeodatabase  
	arcpy.BIMFileToGeodatabase_conversion( Rvt_directory   , 
	                                      out_gdb_path     , out_FeatureDataset, 
	                                      spatial_reference)
	print ("BIM file is imported into the geodatabase.\n Next: Making Building Layer")

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
	print ("The following Building Layer is made: {}".format(nameOfBuildingL))

	# Create a building Scene layer package
	if includeDate:
		now = datetime.now()
		day = now.strftime("%Y%m%d")
		BSL_name = BSL_name[:-5] + day + BSL_name[-5:]
	print (" Next: Creating BSL package with name ({})".format(BSL_name))
	slpk = arcpy.CreateBuildingSceneLayerPackage_management(nameOfBuildingL, BSL_name, spatial_reference)
	print ("Finsihed creating the following Building Scene Layer package {}".format(slpk))
	
	return slpk

def publishBSLfunction(itemID_BSLp = None, itemID_Hosted=None, dictOfPackageLayer = {}, DirectoryTo_SLPK = None ):

	""" in this part of the code we will be accessing Web GIS and publish it into ArcGIS Online"""

	gis = GIS("pro") # accessing ArcGIS online 
	print ("Logged in as {}".format(gis.properties.user.username))
	
	
	if itemID_BSLp is None:
		print ("There is no itemID of type:Scene Package provided")
		print ("Uploading BSL Package....")
		slpk_item = gis.content.add(item_properties = dictOfPackageLayer, data= DirectoryTo_SLPK,\
		 folder='packages')
		print ("Publishing the updloaded BSL package.....")
		slpk_published = slpk_item.publish()
		print (r"work done")
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
			print ("Couldn't find the correct (Hosted) item: many items holds the same title")
			return None
		print ("Working on the following Layers \n1 - {} \n2 - {}".format(itemPackage, itemHosted ))

		print ("Updating BSL Package....")
		slpk_item = gis.content.add(item_properties= dictOfPackageLayer, data= DirectoryTo_SLPK)
		print (slpk_item,slpk_item["title"], slpk_item["id"] )
		# print (stop)
		# get a string of todays data
		now = datetime.now()
		day = now.strftime("%Y%m%d")
		# Update the name with the date of today
		slpk_item.update(item_properties= {"title": slpk_item["title"] + day})
		slpk_published = None
		try:
			print ("Publishing the updated BSL package.....")
			checker = False
			slpk_published = slpk_item.publish()
			try:
				checker = arcpy.server.ReplaceWebLayer(itemHosted["id"], "Archive_" + itemHosted ["title"] + day , slpk_published["id"], "KEEP", "TRUE")
			except:
				print ("Replacement didn't work, trying with different Name")
			if not checker:
				try:
					checker = arcpy.server.ReplaceWebLayer(itemHosted["id"], "Archive_" + itemHosted ["title"] + day + "__2", slpk_published["id"], "KEEP", "TRUE")
					print ("Hosted Layer Scuccesfully replaced")
				except:
					print ("Replacement didn't work, this layer has already been replaced twice today")
					slpk_published.delete()
		except:
			if slpk_published is not None:
				slpk_published.delete()
			print ("(error): \nTry to delete the following layer {} of Type \"Hosted Service\" ".format(slpk_item["title"]))
			print ("Or run publishBSLfunction () separetely")
		slpk_item.update(item_properties= {"title": slpk_item["title"][:-len(day)]})
		print (r"work done")

	else:
		print ("Updating BSL Package....")
		slpk_item = gis.content.add(item_properties = dictOfPackageLayer, data= DirectoryTo_SLPK,\
		 folder='packages')
		print ("Publishing the updated BSL package.....")
		slpk_published = slpk_item.publish()
		print (r"work done")

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

	run_CreateBSLpackage  = True
	run_publishBSLfunction= True
	checkDateOfRevitFile  = True # only works if you add (TimesLog.txt) file and the directory to it
	
	###########################################################################################################
	#directry to the text file in which the histoy log is stored and used for the date check of revit files####
	## see helper function:)
	directoryToTXTfile    = r"C:\Users\alhoz\Desktop\Automation\FinalPythonCodes\TimesLog.txt" 

	"""required parameters and Optional parameters for the workflow
	this workflow is devided into two main parts (here functions)

	                   #################################
	                   ###Function 1 CreateBSLpackage()#
	                   #################################
	"""

	# Required
	########## 
	workSpaceEnv      =  r"C:\Users\alhoz\Desktop\AutomationTest" # path to a folder to createGDB
	Rvt_directory     =  r"C:\Users\alhoz\Desktop\AutomationTest\revitFiles\171025_BLOKA.rvt" # path to rvt file 
	BSL_name          =  r"BSLpackageBlockNew.slpk" # BSLpackage Name defaul is **BSLpackage.slpk**
	spatial_reference =  r"RD New" #default is "RD New"
	nameOfBuildingL   =  r"BuildL_Anew" #this will show on the ArcGIS online 
	
	# optional
	########## 
	out_FeatureDataset= r"Building_A"
	GDBfolder_name    = r"AutomationTESTnew.gdb" #default
	includeDate       = False 
	####################################
	# check date if True and run the Function :CreateBSLpackage
	if checkDateOfRevitFile and run_CreateBSLpackage:
		run_CreateBSLpackage = checkDateFunction(Rvt_directory,directoryToTXTfile)
		if not run_CreateBSLpackage:
			run_publishBSLfunction = False
			print ("The last version of the Revit file is already uploaded")
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
	itemID_BSLp             = "a3826c603e0d4f7d8c2a79ea35a88465" 
	itemID_Hosted           = "0af1fd92f95d46768a72b59845175bae"
	# overwrite parameter is importatnt to be set on **True** ##Only change if you know what you are doing##  
	dictOfPackageLayer      = {"overwrite" : True}
	DirectoryTo_SLPK        = None
	#### this parameter is automaticlly derived from the arguments of function 1 
	#### do not change it unless you know what you are doing
	if includeDate:
		now = datetime.now()
		day = now.strftime("%Y%m%d")
		BSL_name = BSL_name[:-5] +day + BSL_name[-5:] 
	if  DirectoryTo_SLPK is None:
		DirectoryTo_SLPK  = workSpaceEnv + "\\" + BSL_name

	if run_publishBSLfunction:
		publishBSLfunction(itemID_BSLp, itemID_Hosted, dictOfPackageLayer, DirectoryTo_SLPK)