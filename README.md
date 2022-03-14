# solano-monthly-deliverable
Prepares Solano parcels for monthly deliverable

All versions should be posted to Default and all monthly deliverable work should be done while connected to Default!

Every month GTG is to complete the monthly deliverable task. Currently, this task is prompted when Solano staff send GTG the SCIPS table (usually via a WeTransfer email). There is a plan for GTG to retrieve the SCIPS table themselves, however, as of 01/05/2022 this is pending. The SCIPS table is required before GTG can start the deliverable. The monthly deliverable includes: 

- Creating the delivery file geodatabase  
- Loading the file geodatabase onto the Solano GTG Workstation 
- Loading the partners and public parcels into Solano’s enterprise geodatabase 
- Overwriting the REGIS and public parcel feature services and updating their descriptions in ArcGIS Portal 
- Notify Solano of delivery and number of mismatched parcels and SCIPS records via email  

Before the deliverable can be built, the parcel must be inspected for topology errors and obvious data issues. The parcels must not contain any true topology errors. If many topology errors exist, the technician should be consulted and confirm there were no issues with the reconcile and post process. Otherwise, the errors must be corrected or marked as exceptions. Obvious data issues include drastically misaligned parcel edges and half complete parcel blocks. These issues should be resolved in the Monthly Deliverable Prep process (see above).  

1. Bring in the topology and parcels (make sure it is connected as the Default version) 
2. Once brought into a map, validate at the full extent.  
    a. If errors are found, determine if they can be quickly resolved or if a technician should be assigned the work (50+ errors may warrant a tech to handle) 
    b. The monthly deliverable should never be delivered with any topology errors!  
3. After errors are repaired, validate again at full extent to ensure all dirty errors are resolved and only exceptions exist.  

Run the Update Tax Maps tool- must be data owner, GTG.  

1. Ensure you have the most recent copy of the Update Tax Map tool (check with PM or Jessy Beasley) 
2. Open the tool interface in ArcGIS Pro 
3. Supply a working file geodatabase path into the Working FGDB input. It is recommended to use a newly created date stamped file geodatabase to avoid previous data overwrites and for record keeping.  
4. Input the Development Parcels into the Parcels input. ALWAYS use the Default version and be connected as the GTG user (aka, the data owner) 
5. Choose Tax Map Number as the Dissolve Field input. A drop down list should be enabled after the parcels have been input.  
6. Input the Tax Maps into the Tax Maps input. Again, ALWAYS use the Default and GTG user connection.  
7. Hit run.  
8. Open the View Details and see Messages to keep track of the tool’s progress.  
9. If an error is thrown, interpret it and determine if you can fix it. If not, contact Jessy Beasley for assistance. Send her a screenshot of the Messages window.  
10. Once the tool completes, review the outputs for accuracy  
    a. Compare the Tax Map Number in the newly refreshed Tax Maps to the Development Parcels 

Create a folder in a local workspace (ideally, within a folder on your C:). It should be named similarly to: Parcels_MMDDYYYY, where MMDDYYYY represents the current month, day, and year.  

1. Open the tool interface in ArcGIS Pro
2. Input the newly created folder in the Working Folder input 
3. Input the Development Parcels into the Development Parcels input 
4. Input the Tax Maps into the Tax Maps input  
5. Hit run 
6. If an error is thrown, interpret it and determine if you can fix it. If not, contact Jessy Beasley for assistance. Send her a screenshot of the Messages window.  
7. Once the tool completes, review the outputs for accuracy  
    a. Pull the Parcels and Tax Maps from the newly created file geodatabase into the map and check row counts, ensure all parcels and tax maps draw, check editor tracking in both to be sure the ET fields were not overwritten during the export.  

The deliverable includes a file geodatabase containing at minimum six (6) datasets and a CSV with the APN, X centroid, and Y centroid. Solano County may request other ad-hoc datasets and the PM should be aware of these requests. The six datasets are: 

1. Development parcels 
2. Development parcels topology 
3. Internal parcels 
4. Partners parcels 
5. Public parcels 
6. Tax maps   

Description automatically generatedBuilding the deliverables is done by running the Solano Monthly Delivery tool in ArcGIS Pro, or by running the monthly-parcel-delivery-tool Python file. You must run the tool using the Default version! The user must designate the output folder where the file geodatabase and CSV will be written, the input development parcels, the input tax maps, and the most recent SCIPS table. The SCIPS table must live in a file geodatabase.

1. Open the tool interface in ArcGIS Pro 
2. Input the folder you created in the above Prep the Deliverable section into the Working Folder input 
3. Input the file geodatabase created by the Prep Solano Monthly Deliverable tool (should be named Parcles_MMDDYYYY.gdb) into the Working FGDB input. 
4. Input the ParcelData feature dataset into the Feature Dataset with Parcels input.  
5. Input the Development Parcels that were exported in the Prep Solano Monthly Deliverable tool into the Development Parcels input 
6. Input the most recent SCIPS table into the SCIPS Table input  
    a. SCIPS table is delivered by Stew to the PM  
    
The tool can take significant time to run. It is creating four (4) new datasets and calculating numerous fields and geometries. Be sure to allot enough time for it to run and be reviewed.  

The deliverable must be reviewed before loading onto Solano’s GTG Workstation. Key elements to review are: 
- Confirming row count matches the feature class in the enterprise geodatabase  
- Parcels cover the expected extent 
    
This step may be completed at any time between the Inspect Parcels and Notify Solano steps. Mismatches between the development parcels and the SCIPS table must be counted. This includes parcels with no SCIPS match, and SCIPS records with no parcel match. Mismatches are found by performing joins. Joining data within a file geodatabase, versus an enterprise geodatabase, will be quicker. Therefore, it is recommended that this step be performed once the delivery file geodatabase has been created, however, it is not necessary.  

To find parcels with no SCIPS match: 
1. Description automatically generatedAdd the development parcels and the SCIPS table to a map. 
2. Right click the development parcels and select “Joins and Relates”. 
3. Select “Add Join”. 
4. Enter the following parameters: 
    - Input table: Development Parcels 
    - Input join field: PARCELID 
    - Join table: SCIPS table 
    - Join table field: asmtnum 
5. Click OK to execute.  
6. Once joined, open the development parcels attribute table. 
7. Run a Select by Attribute where:  
    - asmtnum IS NULL 
8. Record the number of parcels selected.  

To find SCIPS records with no parcel match: 

1. Add the development parcels and the SCIPS table to a map. 
2. Right click the SCIPS table and select “Joins and Relates”. 
3. Select “Add Join”. 
4. Enter the following parameters: 
    - Input table: SCIPS table 
    - Input join field: asmtnum 
    - Join table: Development Parcels  
    - Join table field: PARCELID 
        - Ignore the warning that asmtnum is not indexed. 
5. Click OK to execute.  
6. Once joined, open the SCIPS table. 
7. Run a Select by Attribute where:  
    - PARCELID IS NULL 
8. Record the number of selected records. 

Once the tool is completed, the metadata must be imported. The metadata XMLs can be on GTG Solano SharePoint

1. In ArcGIS Pro, navigate to the deliverable file geodatabase. 
2. Right click one of the feature classes (ex. Development_Parcels) and choose ‘View Metadata’ 
    - This will open the Catalog window 
3. In the Catalog ribbon, select Import and choose the corresponding XML file. 
    - Choose to allow ArcGIS Pro to discover the type of metadata (it is coded in the XML file) 
4. Once imported, update the following items within the metadata for Development_Parcels, and the Public, Partners, and Internal copies of the parcels: 
    - The dates within the Summary and Description should be updated to the current date 
    - The mismatched SCIPS records should be updated if there was a change from the previous month 
        - the parcels with no SCIPS match increases (or decreases) investigate as to why there are mismatches (ex. Parcels were recently added, parcels are missing APNs, etc.) 
    - The topology error counts  
5. Make sure you save the changes made to the metadata 
6. To make next month easier, please export the metadata after the date/SCIPS counts/topology errors have been updated.  
7. Overwrite the files on SharePoint to ensure they are up to date. 
    - This may simplify tracking changes in SCIPS mismatches  

