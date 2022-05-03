'''
Update TaxMaps shape with newly dissolved 
Parcels. Should be done before monthly 
deliverable. 
'''

arcpy.env.overwriteOutput = True

import arcpy 
from datetime import datetime

def dissolveParcels(fldr, parcel, dissolve_fld, orig_tm):
    
    arcpy.AddMessage('Dissolving parcels...')
    dissolve = arcpy.PairwiseDissolve_analysis(parcel, fldr + r'\dissolveParcels', dissolve_fld, '', 'MULTI_PART')

    arcpy.AddMessage('Adding fields...')
    add_flds = ['TaxMapURL', 'GTGEditor', 'GTGReviewStatus']
    for f in add_flds:
        arcpy.AddMessage('Adding {}...'.format(f))
        arcpy.AddField_management(dissolve, f, 'TEXT', field_length=255, field_alias=f)

    arcpy.AddMessage('Enabling ET...')
    arcpy.EnableEditorTracking_management(dissolve, 'created_user', 'created_date', 'last_edited_user', 'last_edited_date', add_fields='ADD_FIELDS')
    arcpy.AddMessage('Disbale ET...')
    arcpy.DisableEditorTracking_management(dissolve)

    arcpy.AddMessage('Building tax map dictionary...')
    orig_flds = ['TaxMapNumber', 'GTGEditor', 'GTGReviewStatus', 'created_user', 'created_date', 'last_edited_user', 'last_edited_date']
    taxmap_dict = dict([(t[0], (t[1], t[2], t[3], t[4], t[5], t[6]))for t in arcpy.da.SearchCursor(orig_tm, orig_flds)])

    arcpy.AddMessage('Updating rows in dissolve output...')
    update_flds = ['TaxMapNumber', 'TaxMapURL', 'GTGEditor', 'GTGReviewStatus', 
                    'created_user', 'created_date', 'last_edited_user', 'last_edited_date']
    with arcpy.da.UpdateCursor(dissolve, update_flds) as ucur:
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

    arcpy.AddMessage('Done with part 1!')

    return(dissolve)


def updateTaxMaps(fldr, updated_tm, orig_tm):

    now = datetime.now().strftime('%m%d%Y')

    arcpy.AddMessage('Disbaling ET on original tax maps...')
    arcpy.DisableEditorTracking_management(orig_tm)

    arcpy.AddMessage('Taking backup of TaxMaps...')
    arcpy.Copy_management(orig_tm, fldr + r'\backup_TaxMaps_{}'.format(now))

    arcpy.AddMessage('Deleting rows from tax maps...')
    arcpy.DeleteRows_management(orig_tm)
    arcpy.AddMessage('Appending rows...')
    arcpy.Append_management(updated_tm, orig_tm, 'NO_TEST')

    arcpy.AddMessage('Enabling ET...')
    arcpy.EnableEditorTracking_management(orig_tm, 'created_user', 'created_date', 'last_edited_user', 'last_edited_date')


if __name__ == '__main__':

    ## inputs
    working_fldr = arcpy.GetParameterAsText(0)
    parcels = arcpy.GetParameterAsText(1)
    diss_fld = arcpy.GetParameterAsText(2)    
    taxmaps = arcpy.GetParameterAsText(3)

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Beginning process...')

        diss_tm = dissolveParcels(working_fldr, parcels, diss_fld, taxmaps)
        updateTaxMaps(working_fldr, diss_tm, taxmaps)

        arcpy.AddMessage('Done!')
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddMessage(e)


