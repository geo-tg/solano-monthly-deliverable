'''
Update TaxMaps shape with newly create Parcel TaxMaps
MUST run the Update Tax Maps tool in the Parcel Monthly Delivery
toolset first.
'''

arcpy.env.overwriteOutput = True

import arcpy 
from datetime import datetime


def updateTaxMaps(fldr, updated_tm, orig_tm):

    now = datetime.now().strftime('%m%d%Y')

    arcpy.AddMessage('Disbaling ET on AP/RCL tax maps...')
    arcpy.DisableEditorTracking_management(orig_tm)

    arcpy.AddMessage('Taking backup of TaxMaps...')
    aprcl_tm_copy = arcpy.CopyFeatures_management(orig_tm, fldr + f'.gdb\backup_APRCL_TaxMaps_{now}')
    parcel_tm_copy = arcpy.CopyFeatures_management(updated_tm, fldr + f'.gdb\backup_parcel_TaxMaps_{now}')

    arcpy.DisableEditorTracking_management(parcel_tm_copy)

    orig_flds = ['TaxMapNumber', 'GTGEditor', 'GTGReviewStatus', 'created_user', 'created_date', 'last_edited_user', 'last_edited_date']
    taxmap_dict = dict([(t[0], (t[1], t[2], t[3], t[4], t[5], t[6]))for t in arcpy.da.SearchCursor(aprcl_tm_copy, orig_flds)])

    arcpy.AddMessage('Updating rows in dissolve output...')
    update_flds = ['TaxMapNumber', 'TaxMapURL', 'GTGEditor', 'GTGReviewStatus', 
                    'created_user', 'created_date', 'last_edited_user', 'last_edited_date']
    with arcpy.da.UpdateCursor(parcel_tm_copy, update_flds) as ucur:
        for r in ucur:
            if r[0].isdigit():
                r[1] = 'http://www.solanocounty.com/subapp/scips/asr/gis_parcelmap.asp?gisparcel={}'.format(r[0])
            if r[0] in taxmap_dict.keys():
                r[2] = taxmap_dict[r[0]][0]
                r[3] = taxmap_dict[r[0]][1]
                r[4] = taxmap_dict[r[0]][2]
                r[5] = taxmap_dict[r[0]][3]
                r[6] = taxmap_dict[r[0]][4]
                r[7] = taxmap_dict[r[0]][5]

            ucur.updateRow(r)

    arcpy.AddMessage('Deleting rows from tax maps...')
    arcpy.DeleteRows_management(orig_tm)
    arcpy.AddMessage('Appending rows...')
    arcpy.Append_management(parcel_tm_copy, orig_tm, 'NO_TEST')

    arcpy.AddMessage('Enabling ET...')
    arcpy.EnableEditorTracking_management(orig_tm, 'created_user', 'created_date', 'last_edited_user', 'last_edited_date')


if __name__ == '__main__':

    ## inputs
    working_fldr = arcpy.GetParameterAsText(0)
    parcel_taxmaps = arcpy.GetParameterAsText(1)
    aprcl_taxmaps = arcpy.GetParameterAsText(2)

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Beginning process...')

        updateTaxMaps(working_fldr, parcel_taxmaps, aprcl_taxmaps)

        arcpy.AddMessage('Done!')
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddMessage(e)

