The Department of Water and Environtal Regulation (DWER), provided a number of LiDAR derived DEM files 
to Dept. of Biodiversity, Conservation and Attrications (DBCA).
Due to the size of this asc files (200968_Pilbara_Rivers_Area3_DEM_MGA50_B.asc 139,408,422 KB), 
and in a x,y,z column text format, they were not readily accecssable to the DBCA (dept).

Graham Loewenthal produces a series of scripts that would process the asc files into rasters.

Function_1_PartitionCSV_Into_Smaller_CSV_Dask.py

using dask and pandas

The asc file is read in in partitions.

Each partitino is provided as a column header and written as a csv file


The series of scripts is:
Function_1_PartitionCSV_Into_Smaller_CSV_Dask.py

Function_2_CSV_To_Vector_To_Raster_version2_beta.py

Function_3_Merge_Raster_Subsets_gdal.txt (gdasl commands lines not PYthon script)

ClipRasterByVectorTile_20241113_working.py (still await feedback as to know if this product is suitable)
