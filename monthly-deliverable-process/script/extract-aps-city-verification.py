#-*- coding: utf-8 -*-
#Name: extract-aps-city-verification.py
#Description: extracts address points to send to cities

#Import system modules
import arcpy
from datetime import datetime
import shutil
import pandas as pd
import openpyxl

arcpy.env.overwriteOutput = True


def exportFlagged(APs, city, domain_num, out_folder, RCLs, query_field):
    
    q = '{} = {}'.format(query_field, domain_num)

    #select and count APs
    APselection = arcpy.SelectLayerByAttribute_management(APs, 'NEW_SELECTION', q)
    apflagcount = int(arcpy.management.GetCount(APselection)[0])
    if apflagcount == 0:
        arcpy.AddWarning('There are no flagged address points for {}'.format(city))

    #select and count RCLs, if applicable
    rclflagcount = 0
    if RCLs:
        RCLselection = arcpy.SelectLayerByAttribute_management(RCLs, 'NEW_SELECTION', q)
        rclflagcount = int(arcpy.management.GetCount(RCLselection)[0])
        if rclflagcount == 0:
            arcpy.AddWarning('There are no flagged road centerlines for {}'.format(city))

    if apflagcount != 0 or rclflagcount != 0:

        #create folder, gdb, and excel file/writer
        today = datetime.now().strftime('%m%d%Y')
        name = 'NeedsVerification_{}_{}'.format(city, today)
        arcpy.CreateFolder_management(out_folder,name)
        folderToZip = '{}\{}'.format(out_folder,name)
        arcpy.CreateFileGDB_management(folderToZip, name)
        wb = openpyxl.Workbook()
        path = folderToZip + r'\NeedsVerification_{}_{}.xlsx'.format(city, today)
        writer = pd.ExcelWriter(path, engine = 'openpyxl')
        writer.book = wb
        
        #export AP flags
        if apflagcount > 0:
            #make fc
            apfc = arcpy.FeatureClassToFeatureClass_conversion(APselection, r'{}\{}.gdb'.format(folderToZip, name), 'APsToVerify_{}_{}'.format(city, today))
            arcpy.AddMessage('Calculating XY...')
            arcpy.CalculateGeometryAttributes_management(apfc, [['Long', 'POINT_X'], ['Lat', 'POINT_Y']], coordinate_format='DD')
            #make kmz
            kmzPath = r'{0}\{1}.kmz'.format(folderToZip, 'APsToVerify_{}_{}'.format(city, today))
            arcpy.LayerToKML_conversion(APselection, kmzPath)
            #make list
            excel_result1 = arcpy.TableToExcel_conversion(apfc, folderToZip + r'\APsToVerify_{}_{}.xlsx'.format(city, today), 'NAME', 'DESCRIPTION')
            excel_path1 = excel_result1[0]
            df1 = pd.read_excel(excel_path1)
            APfieldstodrop = ['OBJECTID', 'DiscrpAgID','DateUpdate','Effective','Expire','Country','State','County','AddDataURI','Inc_Muni','Uninc_Comm','Nbrhd_Comm','LSt_PreDir','LSt_Name','LSt_Type','LSt_PosDir','ESN','MSAGComm','Post_Comm','Post_Code','Post_Code4','Building','Floor','Room','Seat','Addtl_Loc','LandmkName','Mile_Post','Place_Type','Placement','Elev','GC_Exception','created_user','created_date','last_edited_user','last_edited_date','GlobalID','ADDRESS_ID','SEGMENT_ID','NAME_ID','SIDE','ANOMALY','UNIT_NUM','UNIT_TYPE', 'AddCode']
            df1.drop(APfieldstodrop, axis=1, inplace=True)
            df1.to_excel(writer, sheet_name = 'APs')
            arcpy.management.Delete(excel_result1)
        
        #export RCL flags
        if RCLs and rclflagcount > 0:
            #make fc
            rclfc = arcpy.FeatureClassToFeatureClass_conversion(RCLselection, r'{}\{}.gdb'.format(folderToZip, name), 'RCLsToVerify_{}_{}'.format(city, today))
            #make kmz
            kmzPath = r'{0}\{1}.kmz'.format(folderToZip, 'RCLsToVerify_{}_{}'.format(city, today))
            arcpy.LayerToKML_conversion(RCLselection, kmzPath)
            #make list
            excel_result2 = arcpy.TableToExcel_conversion(rclfc, folderToZip + r'\RCLsToVerify_{}_{}.xlsx'.format(city, today), 'NAME', 'DESCRIPTION')
            excel_path2 = excel_result2[0]
            df2 = pd.read_excel(excel_path2)
            RCLfieldstodrop = ['OBJECTID','LSt_PreDir','LSt_Name','LSt_Type','LSt_PosDir','ESN_L','ESN_R','MSAGComm_L','MSAGComm_R','Country_L','Country_R','State_L','State_R','County_L','County_R','IncMuni_L','IncMuni_R','UnincCom_L','UnincCom_R','NbrhdCom_L','NbrhdCom_R','PostCode_L','PostCode_R','PostComm_L','PostComm_R','OneWay','SpeedLimit','Valid_L','Valid_R','DiscrpAgID','DateUpdate','Effective','Expire','GC_Exception','created_user','created_date','last_edited_user','last_edited_date','GlobalID','SEGMENT_ID','NAME_ID','ANOMALY','fromElev','toElev','fromToCost','toFromCost', 'AddCode_L', 'AddCode_R', 'Shape_Length']
            df2.drop(RCLfieldstodrop, axis=1, inplace=True)
            df2.to_excel(writer, sheet_name = 'RCLs')
            arcpy.management.Delete(excel_result2)

        #save excel file
        sheet = wb.get_sheet_by_name('Sheet')
        wb.remove_sheet(sheet)
        writer.save()       #??????
        wb.save(folderToZip + r'\NeedsVerification_{}_{}.xlsx'.format(city, today))

        #zip folder 
        try:
            shutil.make_archive(folderToZip, 'zip', folderToZip)
            #arcpy.management.Delete(folderToZip)
        except PermissionError as e:
            print(e)
            arcpy.AddMessage(e)

    arcpy.management.SelectLayerByAttribute(APs, 'CLEAR_SELECTION')
    if RCLs: arcpy.management.SelectLayerByAttribute(RCLs, 'CLEAR_SELECTION')


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
    Vacaville = arcpy.GetParameter(8)
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

        if Vacaville:
            exportFlagged(APs, 'Vacaville', '7', out_folder, RCLs, query_field)

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