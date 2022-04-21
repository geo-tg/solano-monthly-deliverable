#-*- coding: utf-8 -*-
#Name: Encroachment_Parcels_FTF.py
#Description: Use FeatureClassToFeatureClass with an expression to create a subset of Parcels marked Encroachment

#Import system modules
import arcpy
from datetime import datetime
import pandas as pd

arcpy.env.overwriteOutput = True

def extractEncroachmentParcels(in_features, out_folder, where_clause):

    print("Running Feature Class to Feature Class...")
    tempgdb = arcpy.CreateFileGDB_management(out_folder, 'temporary')
    extracted_EncroachmentParcels = arcpy.FeatureClassToFeatureClass_conversion(in_features, tempgdb, 'encroachments', where_clause)
    
    arcpy.AddMessage("Removing extra fields (nonrequired)...")
    arcpy.DeleteField_management(extracted_EncroachmentParcels, ["LOWPARCELI", "created_user", "created_date", "gtg_review", "Data_Notes", "TaxMapNumber"])
    arcpy.AddMessage("Running Table to Excel...")
    excel_result = arcpy.TableToExcel_conversion(extracted_EncroachmentParcels, out_folder + r'\EncroachmentParcels.xls')
    excel_path = excel_result[0]
    arcpy.management.Delete(tempgdb)

    arcpy.AddMessage("Formatting Excel file...")
    df = pd.read_excel(excel_path)
    df.drop(['OBJECTID', 'GlobalID', 'Shape_Length', 'Shape_Area'], axis=1, inplace=True)
    writer = pd.ExcelWriter(excel_path)
    df.to_excel(writer, 'Sheet1')
    arcpy.AddMessage("Saving Excel...")
    writer.save()

if __name__ == "__main__":

    # inputs
    in_parcels = arcpy.GetParameterAsText(0)
    query_field = arcpy.GetParameterAsText(1)
    out_folder = arcpy.GetParameterAsText(2)

    q = "{} LIKE '%Encroachment%'".format(query_field)

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Beginning process...')

        extractEncroachmentParcels(in_parcels, out_folder, q)

        arcpy.AddMessage("Parcels Encroachment Tool successfully executed!")
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddError(e)