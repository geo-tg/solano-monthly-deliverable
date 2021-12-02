'''
makes monthly deliv
'''

import arcpy
from datetime import datetime

in_parcels = r''
gis_table = r''
gis_table_flds = [f.name for f in arcpy.ListFields(gis_table) if f.name != 'OBJECTID']
out_ws = r''

today = datetime.now().strftime('%m%d%Y')

# create date stamped file geodatabase for delivery
print('Creating workspace...')
fgdb = str(arcpy.CreateFileGDB_management(out_ws, 'Parcels_{}'.format(today))[0])
fdataset = str(arcpy.CreateFeatureDataset_management(fgdb, 'ParcelData', in_parcels)[0])

# copy over parcels to feature dataset
print('Copying parcels...')
out_parcels = arcpy.Copy_management(in_parcels, fdataset + r'\Development_Parcels')

# build topology
print('Building topology...')
topology = arcpy.CreateTopology_management(fdataset, 'parcelTopology', 0.1)
print('Adding parcels to topology...')
arcpy.AddFeatureClassToTopology_management(topology, out_parcels, 1)
print('Adding rules...')
arcpy.AddRuleToTopology_management(topology, 'Must Not Have Gaps (Area)', out_parcels)
arcpy.AddRuleToTopology_management(topology, 'Must Not Overlap (Area)', out_parcels)
print('Validating at full extent...')
arcpy.ValidateTopology_management(topology, 'Full_Extent')

# disable ET 
# MUST NOT overlap with future field calcs
print('Disabling editor tracking...')
arcpy.DisableEditorTracking_management(out_parcels)

# add requested fields and calculate
add_fields = {'AssessorMap':['Solano County Assessor Map', "'https://www.solanocounty.com/subapp/scips/asr/gis_parcelmap.asp?gisparcel=' + !PARCELID!"], 
            'PropertyChar':['Property Characteristics', "'https://www.solanocounty.com/subapp/scips/asr/propchar.asp?MenuSource=asr&Parcel_Id=' + !PARCELID!"],
            'TaxInfo':['Parcel Tax Information', "'https://www.solanocounty.com/subapp/scips/tax/SecTaxDetail.asp?MenuSource=tax&ParcelId=' + !PARCELID! + '&OccurId=1&rollyear=202021'"]}

print('Adding requested fields...')
for k, v in add_fields.items():
    name = k
    alias = v[0]
    exp = v[1]
    print('Adding {}...'.format(name))
    arcpy.AddField_management(out_parcels, name, 'TEXT', field_length=254, field_alias=alias)
    arcpy.CalculateField_management(out_parcels, name, exp, 'PYTHON3')

# create internal copy
print('Creating internal copy of parcels...')
internal_parcels = arcpy.Copy_management(out_parcels, fdataset + r'\Development_Parcels_internal')
print('Joining fields...')
arcpy.JoinField_management(internal_parcels, 'PARCELID', gis_table, 'asmtnum', gis_table_flds)

# create partners copy
part_del_flds = ['LOWPARCELI', 'created_user', 'created_date', 'last_edited_user', 'last_edited_date', 'gtg_review', 'GTG_Notes', 'Solano_Notes', 'asmtnum']
print('Creating partners copy of parcels...')
partner_parcels = arcpy.CreateFeatureclass_management(fdataset, 'Development_Parcels_partners', 'POLYGON', internal_parcels)
print('Removing fields...')
arcpy.DeleteField_management(partner_parcels, part_del_flds)
print('Appending data...')
arcpy.Append_management(internal_parcels, partner_parcels, 'NO_TEST')

# create public copy
public_del_flds = ['LOWPARCELI', 'created_user', 'created_date', 'last_edited_user', 'last_edited_date', 'gtg_review', 'GTG_Notes', 'Solano_Notes', 
            'assessee', 'addr1', 'addr2', 'addr3', 'addr3_city', 'addr3_state', 'addrzip']
print('Creating public copy of parcels...')
public_parcels = arcpy.CreateFeatureclass_management(fdataset, 'Development_Parcels_public', 'POLYGON', internal_parcels)
print('Removing fields...')
arcpy.DeleteField_management(public_parcels, public_del_flds)
print('Appending data...')
arcpy.Append_management(internal_parcels, public_parcels, 'NO_TEST')

print('Done?')
print('Remember to do work in the GTG Solano Workstation!')
print('Get number of mismatches between the parcels and GIS table...maybe script this later')
