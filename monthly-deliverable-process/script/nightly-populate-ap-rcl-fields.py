'''
to be run nightly
populate:
    AP: APN (overlay with parcels) 
        FullAddress, FullAddr_Label_Abbrv, FullAddr_Label (concat attribution)
        Inc_Muni (overlay with city boundary)
        Uninc_Comm, Post_Comm, Post_Code (overlay with zip code boundary)
    RCL: FullAddress, FullAddr_Label_Abbrv, FullAddr_Label (concat attribution)
        IncMuni_L, IncMuni_R (overlay with city boundary)
        UnincComm_L, UnincComm_R, PostComm_L, PostComm_R, PostCode_L, PostCode_R (overlay with zip code boundary)
'''

import arcpy
from datetime import datetime
import os
#from monthly-ap-rcl-delivery import createDeliverables

arcpy.env.overwriteOutput = True

def createDeliverables(ap, rcl, parcel, city, zipcode):

    today = datetime.now().strftime('%m%d%Y')
    arcpy.AddMessage(today)

    arcpy.AddMessage('Address points!')
    # spat join between ap and parcel to grab APN
    arcpy.AddMessage('SJ between AP and Parcels...')
    ap_parcel_sj = arcpy.SpatialJoin_analysis(ap, parcel, r'in_memory\ap_parcel_sj', 'JOIN_ONE_TO_ONE', 'KEEP_ALL', match_option='WITHIN')
    # dict to use in update cursor
    ap_parcel_dict = {row[0]:row[1] for row in arcpy.da.SearchCursor(ap_parcel_sj, ['TARGET_FID', 'PARCELID'])}

    # spat join between ap and city to grab inc_muni
    arcpy.AddMessage('SJ between AP and Cities...')
    ap_city_sj = arcpy.SpatialJoin_analysis(ap, city, r'in_memory\ap_city_sj', 'JOIN_ONE_TO_ONE', 'KEEP_ALL', match_option='WITHIN')
    # dict to use in update cur
    ap_city_dict = {row[0]:row[1] for row in arcpy.da.SearchCursor(ap_city_sj, ['TARGET_FID', 'NAME'])}

    # spat join between ap and city to grab inc_muni
    arcpy.AddMessage('SJ between AP and Zipcodes...')
    ap_zip_sj = arcpy.SpatialJoin_analysis(ap, zipcode, r'in_memory\ap_zip_sj', 'JOIN_ONE_TO_ONE', 'KEEP_ALL', match_option='WITHIN')
    # dict to use in update cur
    ap_zip_dict = {row[0]:[row[1], row[2]] for row in arcpy.da.SearchCursor(ap_zip_sj, ['TARGET_FID', 'zip_code', 'po_name'])}

    # populate APN, Inc_Muni, Uninc_Comm, Post_Comm, Post_Code
    arcpy.AddMessage('Updating APN, Incorp. Muni., Uninc. Muni., Postal Community Name and Code...')
    with arcpy.da.UpdateCursor(ap, ['OBJECTID', 'APN', 'Inc_Muni', 'Uninc_Comm', 'Post_Comm', 'Post_Code']) as ucur:
        for row in ucur:
            # APN
            if row[0] in ap_parcel_dict.keys():
                if ap_parcel_dict[row[0]] != None:
                    if ap_parcel_dict[row[0]].isdigit():
                        row[1] = ap_parcel_dict[row[0]]
            
            # Inc_Muni
            if row[0] in ap_city_dict.keys():
                if ap_city_dict[row[0]] != None:
                    row[2] = ap_city_dict[row[0]]
                    row[3] = None
                else:
                    # Uninc_Comm
                    row[2] = 'Unincorporated'
                    if row[0] in ap_zip_dict.keys():
                        row[3] = ap_zip_dict[row[0]][1]

            # Post_Comm, Post_Code
            if row[0] in ap_zip_dict.keys():
                if ap_zip_dict[row[0]] != None:
                    row[4] = ap_zip_dict[row[0]][1] # post_comm
                    row[5] = ap_zip_dict[row[0]][0] # post_code

            ucur.updateRow(row)

    arcpy.AddMessage('Roads!')
    # buffer roads by side to get left and right values
    arcpy.AddMessage('Buffering road centerlines on right and left...')
    l_buff = arcpy.Buffer_analysis(rcl, r'in_memory\rcl_left', '100 FEET', 'LEFT', 'FLAT', 'NONE', method='PLANAR')
    r_buff = arcpy.Buffer_analysis(rcl, r'in_memory\rcl_right', '100 FEET', 'RIGHT', 'FLAT', 'NONE', method='PLANAR')

    # tabulate intersections to get proportions
    arcpy.AddMessage('Finding the intersection of the buffers and cities...')
    l_tab_city = arcpy.TabulateIntersection_analysis(l_buff, ['ORIG_FID'], city, r'in_memory\l_tab_city', ['NAME'])
    r_tab_city = arcpy.TabulateIntersection_analysis(r_buff, ['ORIG_FID'], city, r'in_memory\r_tab_city', ['NAME'])

    arcpy.AddMessage('Building dictionaries...')
    left_city_OIDset = set([x[0] for x in arcpy.da.SearchCursor(l_tab_city, ['ORIG_FID'])])
    right_city_OIDset = set([x[0] for x in arcpy.da.SearchCursor(r_tab_city, ['ORIG_FID'])])
    left_city_names = {}
    right_city_names = {}

    # build dictionaries for update cur
    for t in left_city_OIDset:
        names = {x[0]:x[1] for x in arcpy.da.SearchCursor(l_tab_city, ['PERCENTAGE', 'NAME'], f'ORIG_FID = {t}')}
        max_p = max(names.keys())

        left_city_names[t] = names[max_p]

    right_city_names = {}
    for t in right_city_OIDset:
        names = {x[0]:x[1] for x in arcpy.da.SearchCursor(r_tab_city, ['PERCENTAGE', 'NAME'], f'ORIG_FID = {t}')}
        max_p = max(names.keys())

        right_city_names[t] = names[max_p]

    arcpy.AddMessage('Finding the intersection of the buffers and the zipcodes...')
    l_tab_zip = arcpy.TabulateIntersection_analysis(l_buff, ['ORIG_FID'], zipcode, r'in_memory\l_tab_zip', ['zip_code', 'po_name'])
    r_tab_zip = arcpy.TabulateIntersection_analysis(r_buff, ['ORIG_FID'], zipcode, r'in_memory\r_tab_zip', ['zip_code', 'po_name'])

    arcpy.AddMessage('Building dictionaries...')
    left_zip_OIDset = set([x[0] for x in arcpy.da.SearchCursor(l_tab_zip, ['ORIG_FID'])])
    right_zip_OIDset = set([x[0] for x in arcpy.da.SearchCursor(r_tab_zip, ['ORIG_FID'])])
    left_zip_names = {}
    right_zip_names = {}

    # build dictionaries for update cur
    for t in left_zip_OIDset:
        names = {x[0]:[x[1], x[2]] for x in arcpy.da.SearchCursor(l_tab_zip, ['PERCENTAGE', 'zip_code', 'po_name'], f'ORIG_FID = {t}')}
        max_p = max(names.keys())

        left_zip_names[t] = names[max_p]

    for t in right_zip_OIDset:
        names = {x[0]:[x[1], x[2]] for x in arcpy.da.SearchCursor(r_tab_zip, ['PERCENTAGE', 'zip_code', 'po_name'], f'ORIG_FID = {t}')}
        max_p = max(names.keys())

        right_zip_names[t] = names[max_p]

    # populate L&R Inc_Muni, Uninc_Comm, Post_Comm, Post_Code
    arcpy.AddMessage('Updating Left and Right Incorp. Muni., Uninc. Muni., Postal Community Name and Code...')
    with arcpy.da.UpdateCursor(rcl, ['OBJECTID', 'IncMuni_L', 'IncMuni_R', 'UnincCom_L', 'UnincCom_R', 'PostComm_L', 'PostComm_R', 'PostCode_L', 'PostCode_R']) as ucur:
        for row in ucur:

            # Inc_Muni_L
            if row[0] in left_city_names.keys():
                if left_city_names[row[0]] != None:
                    row[1] = left_city_names[row[0]]
                    row[3] = None
                else:
                    row[1] = 'Unincorporated'
                    # Uninc_Comm_L
                    if row[0] in left_zip_names.keys():
                        if left_zip_names[row[0]][1] != None:
                            row[3] = left_zip_names[row[0]][1]
            # Inc_Muni_R
            if row[0] in right_city_names.keys():
                if right_city_names[row[0]] != None:
                    row[2] = right_city_names[row[0]]
                    row[4] = None
                else:
                    row[2] = 'Unincorporated'
                    # Uninc_Comm_R
                    if row[0] in right_zip_names.keys():
                        if right_zip_names[row[0]][1] != None:
                            row[4] = right_zip_names[row[0]][1]
            
            # Post_Comm_L, Post_Code_L
            if row[0] in left_zip_names.keys():
                if left_zip_names[row[0]][0] != None:
                    row[5] = left_zip_names[row[0]][1] # post_comm
                    row[7] = left_zip_names[row[0]][0] # post_code

            # Post_Comm_R, Post_Code_R
            if row[0] in right_zip_names.keys():
                if right_zip_names[row[0]][0] != None:
                    row[6] = right_zip_names[row[0]][1] # post_comm
                    row[8] = right_zip_names[row[0]][0] # post_code

            ucur.updateRow(row)

    # calculate FullAddress, FullAddr_Label_Abbrv, FullAddr_Label for rcl and ap
    # FullAddress (E E ST, BENICIA, CA, 94510), FullAddr_Label_Abbrv (E E ST), FullAddr_Label (EAST E STREET)

    arcpy.AddMessage('Reading domain values for street types and directions...')
    desc = arcpy.da.Describe(ap)
    if desc['path'].endswith('.gdb'):
        # in a feature dataset
        ws = desc['path']
    else:
        ws = arcpy.da.Describe(desc['path'])['path']

    st_dirs_domain = [d for d in arcpy.da.ListDomains(ws) if d.name == 'LegacyStreetNameDirectional'][0]
    st_dirs = dict((v.upper(), k.upper()) for k,v in st_dirs_domain.codedValues.items())
    st_types_domain = [d for d in arcpy.da.ListDomains(ws) if d.name == 'LegacyStreetNameType'][0]
    st_types = dict((v.upper(), k.upper()) for k,v in st_types_domain.codedValues.items())

    # ap
    arcpy.AddMessage('Address points, again!')
    arcpy.AddMessage('Updating the label fields...')
    ap_flds = ['FullAddress', 'FullAddr_Label_Abbrv', 'FullAddr_Label', 'AddNum_Pre', 'Add_Number', 'AddNum_Suf', 'St_PreMod',
            'St_PreDir', 'St_PreTyp', 'St_PreSep', 'St_Name', 'St_PosTyp', 'St_PosDir', 'St_PosMod', 'Post_Comm', 'State', 'Post_Code']
    with arcpy.da.UpdateCursor(ap, ap_flds) as ucur:
        for row in ucur:
            fulladd_concat_flds = row[3:14]
            bnd_concat_flds = row[14:]
            if fulladd_concat_flds[1] != None:
                fulladd_concat_flds[1] = str(fulladd_concat_flds[1])
            if fulladd_concat_flds[4] not in [None, '']:
                if fulladd_concat_flds[4].upper() in st_dirs.keys():
                    fulladd_concat_flds[4] = st_dirs[fulladd_concat_flds[4].upper()]
            if fulladd_concat_flds[5] not in [None, '']:
                if fulladd_concat_flds[5].upper() in st_types.keys():
                    fulladd_concat_flds[5] = st_types[fulladd_concat_flds[5].upper()]
            if fulladd_concat_flds[8] not in [None, '']:
                if fulladd_concat_flds[8].upper() in st_types.keys():
                    fulladd_concat_flds[8] = st_types[fulladd_concat_flds[8].upper()]
            if fulladd_concat_flds[9] not in [None, '']:
                if fulladd_concat_flds[9].upper() in st_dirs.keys():
                    fulladd_concat_flds[9] = st_dirs[fulladd_concat_flds[9].upper()]

            fulladd_clean = [f for f in fulladd_concat_flds if f != None and f != '']
            fulladd_str = (' '.join(fulladd_clean)).upper()
            bnd_clean = [b for b in bnd_concat_flds if b!= None and b != '']
            bnd_str = (', '.join(bnd_clean)).upper()
            fulladd_final = f'{fulladd_str}, {bnd_str}'

            fulladd_label_concat_flds = row[3:14]
            if fulladd_label_concat_flds[1] != None:
                fulladd_label_concat_flds[1] = str(fulladd_label_concat_flds[1])
            label_clean = [l for l in fulladd_label_concat_flds if l != None and l != '']
            label_str = (' '.join(label_clean)).upper()

            row[0] = fulladd_final
            row[1] = fulladd_str
            row[2] = label_str

            ucur.updateRow(row)
    
    # FullAddress (E E ST, BENICIA, CA, 94510), FullAddr_Label_Abbrv (E E ST), FullAddr_Label (EAST E STREET)
    
    # rcl
    arcpy.AddMessage('Roads, again!')
    arcpy.AddMessage('Updating label fields...')
    rcl_flds = ['FullAddress', 'FullAddr_Label_Abbrv', 'FullAddr_Label', 'St_PreMod', 'St_PreDir', 'St_PreTyp', 'St_PreSep', 
                'St_Name', 'St_PosTyp', 'St_PosDir', 'St_PosMod', 'PostComm_L', 'State_L', 'PostCode_L']
    with arcpy.da.UpdateCursor(rcl, rcl_flds) as ucur:
        for row in ucur:
            fulladd_concat_flds = row[3:11]
            bnd_concat_flds = row[11:]
            if fulladd_concat_flds[1] not in [None, '']:
                if fulladd_concat_flds[1].upper() in st_dirs.keys():
                    fulladd_concat_flds[1] = st_dirs[fulladd_concat_flds[1].upper()]
            if fulladd_concat_flds[2] not in [None, '']:
                if fulladd_concat_flds[2].upper() in st_types.keys():
                    fulladd_concat_flds[2] = st_types[fulladd_concat_flds[2].upper()]
            if fulladd_concat_flds[5] not in [None, '']:
                if fulladd_concat_flds[5].upper() in st_types.keys():
                    fulladd_concat_flds[5] = st_types[fulladd_concat_flds[5].upper()]
            if fulladd_concat_flds[6] not in [None, '']:
                if fulladd_concat_flds[6].upper() in st_dirs.keys():
                    fulladd_concat_flds[6] = st_dirs[fulladd_concat_flds[6].upper()]

            fulladd_clean = [f for f in fulladd_concat_flds if f != None and f != '']
            fulladd_str = (' '.join(fulladd_clean)).upper()
            bnd_clean = [b for b in bnd_concat_flds if b!= None and b != '']
            bnd_str = (', '.join(bnd_clean)).upper()
            fulladd_final = f'{fulladd_str}, {bnd_str}'

            fulladd_label_concat_flds = row[3:11]
            label_clean = [l for l in fulladd_label_concat_flds if l != None and l != '']
            label_str = (' '.join(label_clean)).upper()

            row[0] = fulladd_final
            row[1] = fulladd_str
            row[2] = label_str

            ucur.updateRow(row)

    arcpy.AddMessage('Done!')

if __name__ == '__main__':

    ## inputs
    workingfolder = r'D:\pro\projects\Solano'
    sde_cxn = r"D:\pro\projects\Solano\graceT@sdeHub.sde"
    fd = r"D:\pro\projects\Solano\graceT@sdeHub.sde\sdeHub.GRACET.GraceSolanoTest"

    in_ap = r"\sdeHub.GRACET.GraceSolanoTest\sdeHub.GRACET.APs_subset"
    in_rcl = r"\sdeHub.GRACET.GraceSolanoTest\sdeHub.GRACET.RCLs_subset"
    in_parcels = r"\sdeHub.GRACET.GraceSolanoTest\sdeHub.GRACET.parcels"
    in_city = r"\sdeHub.GRACET.GraceSolanoTest\sdeHub.GRACET.city_bound"
    in_zipcodes = r"\sdeHub.GRACET.GraceSolanoTest\sdeHub.GRACET.zipcodes"

    try:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Beginning process...')

        # Make backup fgdb of APs and RCLs
        arcpy.AddMessage('Creating backup...')
        backupgdb = 'AP_RCL_backup_{}'.format(datetime.now().strftime('%m%d%y'))
        arcpy.management.CreateFileGDB(workingfolder, backupgdb)
        arcpy.management.CopyFeatures(sde_cxn + in_ap, r'{}\{}.gdb\APs'.format(workingfolder, backupgdb))
        arcpy.management.CopyFeatures(sde_cxn+ in_rcl, r'{}\{}.gdb\RCLs'.format(workingfolder, backupgdb))

        # Disable editor tracking
        arcpy.AddMessage('Disabling editor tracking...')
        arcpy.management.DisableEditorTracking(fd)

        # Create temporary version
        # arcpy.AddMessage("Checking if temp version already exists...")
        # versions = [ver.name for ver in arcpy.da.ListVersions(sde_cxn)]
        # if 'GRACET.populateFieldsTemp' in versions:
        #     arcpy.DeleteVersion_management(sde_cxn, 'GRACET.populateFieldsTemp')
        
        # arcpy.AddMessage("Creating populateFieldsTemp version...")
        # arcpy.CreateVersion_management(sde_cxn, 'sde.DEFAULT', 'populateFieldsTemp', 'PRIVATE')
        # arcpy.AddMessage("Creating connection file w temp version") #NEEDS TO BE UPDATED
        # arcpy.CreateDatabaseConnection_management(workingfolder, "populateFieldsTemp@sdeHub", "SQL_SERVER", "10.0.0.4", 
        #             "DATABASE_AUTH","GraceT", "gtgCL0udDb616*", "SAVE_USERNAME", "sdeHub", "", "TRANSACTIONAL", "GRACET.populateFieldsTemp")
        # temp_sde_cxn = workingfolder + r"\populateFieldsTemp@sdeHub.sde"

        # Execute function
        arcpy.AddMessage('Exceuting createDeliverables function...')
        #arcpy.CalculateField_management(in_rcl, "FullAddress", 'None', "PYTHON3")
        createDeliverables(sde_cxn+in_ap, sde_cxn+in_rcl, sde_cxn+in_parcels, sde_cxn+in_city, sde_cxn+in_zipcodes)

        # Clean up, aisle 5
        # arcpy.AddMessage("Reconcile and posting edits to sde.DEFAULT")
        # arcpy.AddMessage("Version populateFieldsTemp will be deleted...") #NEEDS TO BE UPDATED
        # arcpy.ReconcileVersions_management(temp_sde_cxn, "ALL_VERSIONS", "sde.DEFAULT", "GRACET.populateFieldsTemp", "LOCK_ACQUIRED", "", "", "", 
        #                                    "POST", "DELETE_VERSION", workingfolder + r"\populateFieldsTempReconcile.txt")
        
        # arcpy.AddMessage('Deleting sde connection to deleted version')
        # if os.path.exists(temp_sde_cxn):
        #     os.remove(temp_sde_cxn)

        # Re-enable editor tracking
        arcpy.AddMessage('Re-enabling editor tracking...')
        arcpy.management.EnableEditorTracking(fd)

        arcpy.AddMessage('Done!')
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))

    except Exception as e:
        arcpy.AddMessage(datetime.now().strftime('%m%d%Y %H:%M:%S'))
        arcpy.AddMessage('Problem!')
        arcpy.AddMessage(e)

        # removing version
        # versions = [ver.name for ver in arcpy.da.ListVersions(sde_cxn)]
        # if 'GRACET.populateFieldsTemp' in versions:
        #     arcpy.DeleteVersion_management(sde_cxn, 'GRACET.populateFieldsTemp')
        # if os.path.exists(temp_sde_cxn):
        #     os.remove(temp_sde_cxn)