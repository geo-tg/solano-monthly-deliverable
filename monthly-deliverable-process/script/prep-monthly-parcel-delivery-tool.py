'''
prep monthly deliv
'''

import arcpy
from datetime import datetime

arcpy.env.overwriteOutput = True

def extractFeatures(out_ws, in_parcels, in_taxmaps):

    today = datetime.now().strftime('%m%d%Y')

    # create date stamped file geodatabase for delivery
    arcpy.AddMessage('Creating workspace...')
    fgdb = str(arcpy.CreateFileGDB_management(out_ws, 'Parcels_{}'.format(today))[0])
    fdataset = str(arcpy.CreateFeatureDataset_management(fgdb, 'ParcelData', in_parcels)[0])

    # copy over parcels to feature dataset
    arcpy.AddMessage('Copying parcels...')
    arcpy.AddMessage(datetime.now())
    out_parcels = arcpy.Copy_management(in_parcels, fdataset + r'\Development_Parcels')

    # copy over taxmaps to feature dataset
    arcpy.AddMessage('Copying taxmaps...')
    arcpy.AddMessage(datetime.now())
    arcpy.Copy_management(in_taxmaps, fdataset + r'\TaxMaps')

    # clean up rel classes and tables
    arcpy.AddMessage('Clean up!')

    arcpy.AddMessage('Deleting the data_edit feature datsaet and tables brought over due to rel classes...')
    clean_up = [['EditData', 'FeatureDataset'], ['ParcelsNoSCIPSMatch', ''], ['TaxMapUpdates', '']]
    for c in clean_up:
        arcpy.AddMessage('Removing {}...'.format(c[0]))
        if arcpy.Exists(fgdb + r'\{}'.format(c[0])):
            arcpy.Delete_management(fgdb + r'\{}'.format(c[0]), c[1])

    arcpy.AddMessage('Deleting the attribute rules...')
    arcpy.DeleteAttributeRule_management(out_parcels, ['Calculate Tax Map Number', 'Populate LOWPARCELID','Calculate GIS Acreage'])

    arcpy.AddMessage('Done!')


if __name__ == '__main__':

    ## inputs
    working_fldr = arcpy.GetParameterAsText(0)
    parcels = arcpy.GetParameterAsText(1)
    taxmaps = arcpy.GetParameterAsText(2)

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Beginning process...')

        extractFeatures(working_fldr, parcels, taxmaps)

        arcpy.AddMessage('Done!')
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddMessage(e)
