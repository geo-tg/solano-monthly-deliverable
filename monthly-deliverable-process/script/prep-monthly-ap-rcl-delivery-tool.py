'''
prep monthly deliv for AP and RCL
'''

import arcpy
from datetime import datetime

arcpy.env.overwriteOutput = True

def extractFeatures(out_ws, in_fc, in_taxmaps, ap_or_rcl):

    today = datetime.now().strftime('%m%d%Y')

    if ap_or_rcl == 'ap':
        fgdbname = 'AddressPoints_'
        fdsname = 'AddressData'
    elif ap_or_rcl == 'rcl':
        fgdbname = 'RoadCenterlines_'
        fdsname = 'RoadsData'

    fc_name = arcpy.da.Describe(in_fc)['baseName'].split('.')[-1]

    # create date stamped file geodatabase for delivery
    arcpy.AddMessage('Creating workspace...')
    fgdb = str(arcpy.CreateFileGDB_management(out_ws, fgdbname + today)[0])
    fdataset = str(arcpy.CreateFeatureDataset_management(fgdb, fdsname, in_fc)[0])

    # copy over feature class to feature dataset
    arcpy.AddMessage('Copying dataset...')
    arcpy.AddMessage(datetime.now())
    out_fc = arcpy.Copy_management(in_fc, fdataset + f'\{fc_name}')

    arcpy.DisableEditorTracking_management(out_fc)

    # copy over taxmaps to feature dataset
    arcpy.AddMessage('Copying taxmaps...')
    arcpy.AddMessage(datetime.now())
    fc_copy = arcpy.Copy_management(in_taxmaps, fdataset + r'\TaxMap_RCL_AP_review')

    arcpy.DisableEditorTracking_management(fc_copy)

    arcpy.AddMessage('Done!')


if __name__ == '__main__':

    ## inputs
    working_fldr = arcpy.GetParameterAsText(0)
    aps = arcpy.GetParameterAsText(1)
    rcls = arcpy.GetParameterAsText(2)
    taxmaps = arcpy.GetParameterAsText(3)

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

        arcpy.AddMessage('Beginning process for APs...')
        extractFeatures(working_fldr, aps, taxmaps, 'ap')

        arcpy.AddMessage('Beginning process for RCLs...')
        extractFeatures(working_fldr, rcls, taxmaps, 'rcl')

        arcpy.AddMessage('Done!')
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddMessage(e)
