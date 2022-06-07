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

arcpy.env.overwriteOutput = True