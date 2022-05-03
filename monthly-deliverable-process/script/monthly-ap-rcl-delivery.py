'''
makes monthly AP/RCL deliv
populate:
    AP: APN (overlay with parcels)
        FullAddress, FullAddr_Label_Abbrv, FullAddr_Label (concat attribution)
        Inc_Muni (overlay with city boundary)
        Uninc_Comm, Post_Comm, Post_Code (overlay with zip code boundary)
    RCL: FullAddress, FullAddr_Label_Abbrv, FullAddr_Label (concat attribution)
        IncMuni_L, IncMuni_R (overlay with city boundary)
        UnincComm_L, UnincComm_R, PostComm_L, PostComm_R, PostCode_L, PostCode_R (overlay with zip code boundary)


NOT COMPLETE!!
'''

import arcpy
from datetime import datetime

arcpy.env.overwriteOutput = True

def createDeliverables(folder, fgdb, fdataset, parcels, gis_table):

    today = datetime.now().strftime('%m%d%Y')
    arcpy.AddMessage(today)

    


if __name__ == '__main__':

    ## inputs
    in_ap = arcpy.GetParameterAsText(0)
    in_rcl = arcpy.GetParameterAsText(1)
    in_parcels = arcpy.GetParameterAsText(2)
    in_city = arcpy.GetParameterAsText(3)
    in_zipcodes = arcpy.GetParameterAsText(4)

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Beginning process...')

        # createDeliverables(working_fldr, working_fgdb, working_ds, parcels, scips)

        arcpy.AddMessage('Done!')
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddMessage(e)

