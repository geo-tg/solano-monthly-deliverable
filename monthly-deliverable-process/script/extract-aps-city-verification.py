#-*- coding: utf-8 -*-
#Name: extract-aps-city-verification.py
#Description: extracts address points to send to cities

#Import system modules
import arcpy
from datetime import datetime
import shutil

arcpy.env.overwriteOutput = True


def exportFlagged(APs, city, domain_num, out_folder, RCLs, query_field):
    arcpy.AddMessage("Exporting flags for {}".format(city))

    #create folder and gdb
    today = datetime.now().strftime('%m%d%Y')
    name = 'NeedsVerification_{}_{}'.format(city, today)
    arcpy.CreateFolder_management(out_folder,name)
    folderToZip = '{}\{}'.format(out_folder,name)
    arcpy.CreateFileGDB_management(folderToZip, name)
    
    q = '{} = {}'.format(query_field, domain_num)

    #select and export APs
    APselection = arcpy.SelectLayerByAttribute_management(APs, 'NEW_SELECTION', q)

    arcpy.FeatureClassToFeatureClass_conversion(APselection, r'{}\{}.gdb'.format(folderToZip, name), 'APsToVerify_{}_{}'.format(city, today))

    kmzPath = r'{0}\{1}.kmz'.format(folderToZip, 'APsToVerify_{}_{}'.format(city, today))
    arcpy.LayerToKML_conversion(APselection, kmzPath)

    arcpy.AddMessage('gonna make an excel list :)')


    #select and export RCLs, if applicable
    if RCLs:
        RCLlyr = arcpy.MakeFeatureLayer_management(RCLs, 'RCLsToVerify_{}_{}'.format(city, today))
        RCLselection = arcpy.SelectLayerByAttribute_management(RCLlyr, 'NEW_SELECTION', q)
        arcpy.FeatureClassToFeatureClass_conversion(RCLselection, r'{}\{}'.format(folderToZip, '{}.gdb'.format(name)), 'RCLsToVerify_{}_{}'.format(city, today))
        kmzPath = r'{0}\{1}.kmz'.format(folderToZip, 'RCLsToVerify_{}_{}'.format(city, today))
        arcpy.LayerToKML_conversion(RCLselection, kmzPath)

    #zip folder 
    try:
        shutil.make_archive(folderToZip, 'zip', folderToZip)
        arcpy.management.Delete(folderToZip)
    except PermissionError as e:
        print(e)
        arcpy.AddMessage(e)


if __name__ == "__main__":

    # inputs
    APs = arcpy.GetParameterAsText(0)
    RCLs = arcpy.GetParameterAsText(1)
    query_field = arcpy.GetParameterAsText(2)
    out_folder = arcpy.GetParameterAsText(3)
    Benicia = arcpy.GetParameter(4)
    RioVista = arcpy.GetParameter(5) 
    Fairfield = arcpy.GetParameter(6) 
    Vallejo = arcpy.GetParameter(7) 
    Vacacille = arcpy.GetParameter(8)
    Suisun = arcpy.GetParameter(9)
    Dixon = arcpy.GetParameter(10)
    Unincorporated = arcpy.GetParameter(11) 

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Beginning process...')

        if Benicia:
            exportFlagged(APs, 'Benicia', '3', out_folder, RCLs, query_field)
        
        if RioVista:
            exportFlagged(APs, 'RioVista', '4', out_folder, RCLs, query_field)

        if Fairfield:
            exportFlagged(APs, 'Fairfield', '5', out_folder, RCLs, query_field)

        if Vallejo:
            exportFlagged(APs, 'Vallejo', '6', out_folder, RCLs, query_field)

        if Vacacille:
            exportFlagged(APs, 'Vacacille', '7', out_folder, RCLs, query_field)

        if Suisun:
            exportFlagged(APs, 'Suisun', '8', out_folder, RCLs, query_field)

        if Dixon:
            exportFlagged(APs, 'Dixon', '9', out_folder, RCLs, query_field)

        if Unincorporated:
            exportFlagged(APs, 'Unincorporated', '10', out_folder, RCLs, query_field)

        arcpy.AddMessage('Success!')
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddError(e)