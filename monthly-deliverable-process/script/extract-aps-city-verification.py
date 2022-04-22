#-*- coding: utf-8 -*-
#Name: extract-aps-city-verification.py
#Description: extracts address points to send to cities

#Import system modules
import arcpy
from datetime import datetime
import shutil
import pandas as pd

arcpy.env.overwriteOutput = True


def exportFlagged(APs, city, domain_num, out_folder, RCLs, query_field):
    arcpy.AddMessage("Exporting flags for {}".format(city))

    #create folder and gdb
    today = datetime.now().strftime('%m%d%Y')
    name = 'NeedsVerification_{}_{}'.format(city, today)
    arcpy.CreateFolder_management(out_folder,name)
    folderToZip = '{}\{}'.format(out_folder,name)
    arcpy.CreateFileGDB_management(folderToZip, name)
    
    #select APs
    q = '{} = {}'.format(query_field, domain_num)
    APselection = arcpy.SelectLayerByAttribute_management(APs, 'NEW_SELECTION', q)
    #make fc
    apfc = arcpy.FeatureClassToFeatureClass_conversion(APselection, r'{}\{}.gdb'.format(folderToZip, name), 'APsToVerify_{}_{}'.format(city, today))
    #make kmz
    kmzPath = r'{0}\{1}.kmz'.format(folderToZip, 'APsToVerify_{}_{}'.format(city, today))
    arcpy.LayerToKML_conversion(APselection, kmzPath)
    arcpy.management.SelectLayerByAttribute(APs, 'CLEAR_SELECTION')
    #make excel list
    # excel_result = arcpy.TableToExcel_conversion(apfc, folderToZip + r'\APsToVerify_{}_{}.xls'.format(city, today))
    # excel_path = excel_result[0]
    # df = pd.read_excel(excel_path)
    # APfieldstodrop = ['DiscrpAgID','DateUpdate','Effective','Expire','Country','State','County','AddDataURI','Inc_Muni','Uninc_Comm','Nbrhd_Comm','LSt_PreDir','LSt_Name','LSt_Type','LSt_PosDir','ESN','MSAGComm','Post_Comm','Post_Code','Post_Code4','Building','Floor','Room','Seat','Addtl_Loc','LandmkName','Mile_Post','Place_Type','Placement','Long','Lat','Elev','GC_Exception','created_user','created_date','last_edited_user','last_edited_date','GlobalID','ADDRESS_ID','SEGMENT_ID','NAME_ID','SIDE','ANOMALY','UNIT_NUM','UNIT_TYPE']
    # #APfieldstodrop = ['OBJECTID','srcUnqID','gcLgFlAdr','gcFullAdr','placeType','msagComm','zipCode','esn','srcOfData','taxlotID','srcLastEd','effective','rSrcUnqID','addNumComb','postType','gcFullName','lgcyPreDir','lgcyName','lgcyType','lgcyPstDir','gcLgFlName','building','floor','unitDesc','unitNo','room','seat','location','gcLabel','landmark','zipCode4','country','state','county','incMuni','unincComm','nbrhdComm','postComm','long','lat','milepost','voipEsn','comments','exception','gcCaseNum','gcNotes','gcReview','lastName','firstName','telephone','AT_NAME','SP_NAME','CR_NAME','created_user','created_date','last_edited_user','last_edited_date','GlobalID']
    # df.drop(APfieldstodrop, axis=1, inplace=True)
    # writer = pd.ExcelWriter(excel_path)
    # df.to_excel(writer, 'Sheet1')
    # writer.save()


    excel_result = arcpy.TableToExcel_conversion(apfc, folderToZip + r'\NeedsVerification_{}_{}.xls'.format(city, today))
    excel_path = excel_result[0]
    df = pd.read_excel(excel_path)
    APfieldstodrop = ['DiscrpAgID','DateUpdate','Effective','Expire','Country','State','County','AddDataURI','Inc_Muni','Uninc_Comm','Nbrhd_Comm','LSt_PreDir','LSt_Name','LSt_Type','LSt_PosDir','ESN','MSAGComm','Post_Comm','Post_Code','Post_Code4','Building','Floor','Room','Seat','Addtl_Loc','LandmkName','Mile_Post','Place_Type','Placement','Long','Lat','Elev','GC_Exception','created_user','created_date','last_edited_user','last_edited_date','GlobalID','ADDRESS_ID','SEGMENT_ID','NAME_ID','SIDE','ANOMALY','UNIT_NUM','UNIT_TYPE']
    #APfieldstodrop = ['OBJECTID','srcUnqID','gcLgFlAdr','gcFullAdr','placeType','msagComm','zipCode','esn','srcOfData','taxlotID','srcLastEd','effective','rSrcUnqID','addNumComb','postType','gcFullName','lgcyPreDir','lgcyName','lgcyType','lgcyPstDir','gcLgFlName','building','floor','unitDesc','unitNo','room','seat','location','gcLabel','landmark','zipCode4','country','state','county','incMuni','unincComm','nbrhdComm','postComm','long','lat','milepost','voipEsn','comments','exception','gcCaseNum','gcNotes','gcReview','lastName','firstName','telephone','AT_NAME','SP_NAME','CR_NAME','created_user','created_date','last_edited_user','last_edited_date','GlobalID']
    df.drop(APfieldstodrop, axis=1, inplace=True)
    writer = pd.ExcelWriter(excel_result)
    df.to_excel(writer, sheet_name = 'APs')
    writer.save()

    #select and export RCLs, if applicable
    if RCLs:
        RCLlyr = arcpy.MakeFeatureLayer_management(RCLs, 'RCLsToVerify_{}_{}'.format(city, today))
        RCLselection = arcpy.SelectLayerByAttribute_management(RCLlyr, 'NEW_SELECTION', q)
        rclfc =arcpy.FeatureClassToFeatureClass_conversion(RCLselection, r'{}\{}'.format(folderToZip, '{}.gdb'.format(name)), 'RCLsToVerify_{}_{}'.format(city, today))
        kmzPath = r'{0}\{1}.kmz'.format(folderToZip, 'RCLsToVerify_{}_{}'.format(city, today))
        arcpy.LayerToKML_conversion(RCLselection, kmzPath)
        excel_result2 = arcpy.TableToExcel_conversion(rclfc, folderToZip + r'\RCLsToVerify_{}_{}.xls'.format(city, today))
        excel_path2 = excel_result2[0]
        df = pd.read_excel(excel_path2)
        #RCLfieldstodrop = ['OBJECTID', 'srcUnqID', 'gcLgFlName', 'gcFullName', 'rdOwner', 'esnL', 'esnR', 'postCommL', 'postCommR', 'zipCodeL', 'zipCodeR', 'srcOfData', 'srcLastEd', 'effective', 'gcLabel', 'lgcyPreDir', 'lgcyName', 'lgcyType', 'lgcyPstDir', 'parityL', 'parityR', 'speedLimit', 'oneWay', 'roadClass', 'minutes', 'miles', 'fcc', 'fZlevel', 'tZlevel', 'countryL', 'countryR', 'stateL', 'stateR', 'countyL', 'countyR', 'incMuniL', 'incMuniR', 'unincCommL', 'unincCommR', 'nbrhdCommL', 'nbrhdCommR', 'msagCommL', 'msagCommR', 'voipEsnL', 'voipEsnR', 'rdNumber', 'alias', 'exception', 'gcCaseNum', 'gcNotes', 'AT_NAME', 'SP_NAME', 'CR_NAME', 'created_user', 'created_date', 'last_edited_user', 'last_edited_date', 'GlobalID', 'Shape_Length']
        #df.drop(RCLfieldstodrop, axis=1, inplace=True)
        #writer = pd.ExcelWriter(excel_path)
        df.to_excel(writer, sheet_name = 'RCLs')
        writer.save()



    #zip folder 
    try:
        shutil.make_archive(folderToZip, 'zip', folderToZip)
        #arcpy.management.Delete(folderToZip)
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