'''
makes monthly deliv
'''

import arcpy
from datetime import datetime

arcpy.env.overwriteOutput = True

def createDeliverables(folder, fgdb, fdataset, parcels, gis_table):

    today = datetime.now().strftime('%m%d%Y')
    arcpy.AddMessage(today)

    # build topology
    arcpy.AddMessage('Building topology...')
    topology = arcpy.CreateTopology_management(fdataset, 'parcelTopology', 0.0032808333)
    arcpy.AddMessage('Adding parcels to topology...')
    arcpy.AddFeatureClassToTopology_management(topology, parcels, 1)
    arcpy.AddMessage('Adding rules...')
    arcpy.AddRuleToTopology_management(topology, 'Must Not Have Gaps (Area)', parcels)
    arcpy.AddRuleToTopology_management(topology, 'Must Not Overlap (Area)', parcels)
    arcpy.AddMessage('Validating at full extent...')
    arcpy.ValidateTopology_management(topology, 'Full_Extent')

    # disable ET 
    # MUST NOT overwrite with future field calcs
    arcpy.AddMessage('Disabling editor tracking...')
    arcpy.DisableEditorTracking_management(parcels)

    # add acreage and centroid XY fields and calculate
    add_geom_flds = {'Xcentroid': ['X Centroid', 'CENTROID_X', 'DD', ''],
                    'Ycentroid': ['Y Centroid', 'CENTROID_Y', 'DD', '']} # 'GIS_Acreage': ['GIS Acreage', 'AREA', '', 'ACRES'],
    for fname, fprop in add_geom_flds.items():
        alias = fprop[0]
        geom_prop = fprop[1]
        coo_unit = fprop[2]
        a_unit = fprop[3]

        arcpy.AddMessage('Adding {}...'.format(fname))
        arcpy.AddMessage(datetime.now())
        arcpy.AddField_management(parcels, fname, 'DOUBLE', field_alias=alias)
        arcpy.CalculateGeometryAttributes_management(parcels, [[fname, geom_prop]], area_unit=a_unit, coordinate_system=parcels, coordinate_format=coo_unit)

    # add requested fields and calculate
    add_fields = {'AssessorMap':['Solano County Assessor Map', "'https://www.solanocounty.com/subapp/scips/asr/gis_parcelmap.asp?gisparcel=' + !PARCELID!"], 
                'PropertyChar':['Property Characteristics', "'https://www.solanocounty.com/subapp/scips/asr/propchar.asp?MenuSource=asr&Parcel_Id=' + !PARCELID!"],
                'TaxInfo':['Parcel Tax Information', "'https://www.solanocounty.com/subapp/scips/tax/SecTaxDetail.asp?MenuSource=tax&ParcelId=' + !PARCELID! + '&OccurId=1&rollyear=202021'"]}

    arcpy.AddMessage('Adding requested fields...')
    for k, v in add_fields.items():
        name = k
        alias = v[0]
        exp = v[1]
        arcpy.AddMessage('Adding {}...'.format(name))
        arcpy.AddMessage(datetime.now())
        arcpy.AddField_management(parcels, name, 'TEXT', field_length=254, field_alias=alias)
        arcpy.CalculateField_management(parcels, name, exp, 'PYTHON3')
    
    # listing SCIPS fields for joining
    gis_table_flds = [f.name for f in arcpy.ListFields(gis_table) if f.name != 'OBJECTID']

    # create internal copy
    arcpy.AddMessage('Creating internal copy of parcels...')
    internal_parcels = arcpy.CreateFeatureclass_management(fdataset, 'Development_Parcels_internal', 'POLYGON', parcels)
    arcpy.Append_management(parcels, internal_parcels, 'NO_TEST')
    arcpy.AddMessage('Joining fields...')
    arcpy.JoinField_management(internal_parcels, 'PARCELID', gis_table, 'asmtnum', gis_table_flds)

    # add and calculate field to calculate acreage difference
    if 'acres' in gis_table_flds:
        arcpy.AddMessage('Adding Acreage_Diff field...')
        arcpy.AddField_management(internal_parcels, 'Acreage_Diff', 'DOUBLE', field_alias='GIS/SCIPS Acreage Difference')
        arcpy.AddMessage('Calculating Acreage_Diff...')
        arcpy.AddMessage(datetime.now())
        arcpy.CalculateField_management(internal_parcels, 'Acreage_Diff', "!GIS_Acreage! - !acres!", 'PYTHON3')
    else:
        arcpy.AddMessage('Field ''acres'' does not exist in SCIPS table... :(')
        
    # create partners copy
    part_del_flds = ['LOWPARCELI', 'created_user', 'created_date', 'last_edited_user', 'last_edited_date', 'gtg_review', 'GTG_Notes', 'Solano_Notes', 'asmtnum']
    arcpy.AddMessage('Creating partners copy of parcels...')
    partner_parcels = arcpy.CreateFeatureclass_management(fdataset, 'Development_Parcels_partners', 'POLYGON', internal_parcels)
    arcpy.AddMessage('Removing fields...')
    arcpy.DeleteField_management(partner_parcels, part_del_flds)
    arcpy.AddMessage('Appending data...')
    arcpy.Append_management(internal_parcels, partner_parcels, 'NO_TEST')

    # create public copy
    public_del_flds = ['LOWPARCELI', 'created_user', 'created_date', 'last_edited_user', 'last_edited_date', 'gtg_review', 'GTG_Notes', 'Solano_Notes', 
                'assessee', 'addr1', 'addr2', 'addr3', 'addr3_city', 'addr3_state', 'addrzip']
    arcpy.AddMessage('Creating public copy of parcels...')
    public_parcels = arcpy.CreateFeatureclass_management(fdataset, 'Development_Parcels_public', 'POLYGON', internal_parcels)
    arcpy.AddMessage('Removing fields...')
    arcpy.DeleteField_management(public_parcels, public_del_flds)
    arcpy.AddMessage('Appending data...')
    arcpy.Append_management(internal_parcels, public_parcels, 'NO_TEST')

    #creating csv of APN, X, Y
    arcpy.AddMessage('Creating APN/X/Y CSV file...')
    tempTab = arcpy.TableToTable_conversion(parcels, 'in_memory', 'temp_Development_Parcels')
    keep_flds = ['PARCELID', 'Xcentroid', 'Ycentroid']
    del_flds = [fld.name for fld in arcpy.ListFields(tempTab) if (fld.name not in keep_flds and not fld.required)]
    arcpy.DeleteField_management(tempTab, del_flds)
    arcpy.TableToTable_conversion(tempTab, folder, 'Development_Parcels_XY.csv')

    # finding mismatches 
    scips_desc = arcpy.da.Describe(gis_table)
    scips_name = scips_desc['name']
    parcel_joined_scips = arcpy.AddJoin_management(parcels, 'PARCELID', gis_table, 'asmtnum')
    parcel_select = arcpy.SelectLayerByAttribute_management(parcel_joined_scips, 'NEW_SELECTION', '{}.asmtnum IS NULL'.format(scips_name))
    parcels_no_match = arcpy.GetCount_management(parcel_select)[0]
    
    parcel_desc = arcpy.da.Describe(parcels)
    parcels_name = parcel_desc['name']
    scips_joined_parcels = arcpy.AddJoin_management(gis_table, 'asmtnum', parcels, 'PARCELID')
    scips_select = arcpy.SelectLayerByAttribute_management(scips_joined_parcels, 'NEW_SELECTION', '{}.PARCELID IS NULL'.format(parcels_name))
    scips_no_match = arcpy.GetCount_management(scips_select)[0]

    arcpy.AddMessage('{} parcels have no SCIPS match!'.format(parcels_no_match))
    arcpy.AddMessage('{} SCIPS rows have no parcel match!'.format(scips_no_match))

    arcpy.AddMessage('Done? Almost...')
    arcpy.AddMessage('Remember to update the metadata!! Update SCIPS mismatch values, the edit date, and topology errors!')
    arcpy.AddMessage('Remember to upload and publish in the GTG Solano Workstation!')

    arcpy.AddMessage(datetime.now())

if __name__ == '__main__':

    ## inputs
    working_fldr = arcpy.GetParameterAsText(0)
    working_fgdb = arcpy.GetParameterAsText(1)
    working_ds = arcpy.GetParameterAsText(2)
    parcels = arcpy.GetParameterAsText(3)
    scips = arcpy.GetParameterAsText(4)

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Beginning process...')

        createDeliverables(working_fldr, working_fgdb, working_ds, parcels, scips)

        arcpy.AddMessage('Done!')
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddMessage(e)

