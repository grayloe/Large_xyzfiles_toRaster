# -*- coding: utf-8 -*-
"""
Created on Fri May 10 12:39:57 2024

@author: GrahamLoewenthal
"""

# -*- coding: utf-8 -*-

import os
import glob
import pandas as pd

import geopandas as gpd
from shapely.geometry import Point

import math
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds


### USER ACTIONS PRIOT TO SCRIPT ###

### 1) READ THE ASSOCIATED REPORT TO DETERMINE THE SOURCE CRS OF THE CSV FILE
### 2) DETERMINE IF THE DATA IS TO BE REPROJECTED

### THE SCRIPT EXPECTS THE FILE NAME TO HAVE A NAME OF THE CRS IN THE FORMAT "GDA2020", OR "GDA1994" SEPERATED BY "_"
### THE SCRIPT WILL CHANGE THE GDAyyyy TO GDAyyyyMGAzz or GDAyyyy TO GDAyyyyAlbers

### IF IT DOES NOT EITHER: 
### A) CHANGE THE SINGLUAR (NOT PARTITIONED) SOURCE FILE TO HAVE THIS FORMATE
### B) CHANGE THE PARTITIONED SOURCE FILES TO HAVE THIS FORMATE
### C) COPY AND UPDATE THE SCRIPT  (MAYBE ASK GRAHAM)

### GRAHAM THE OUTPUT RASTER HAS A TOO LARGE EXTENT #### IT WORKS THOUGH ###
### GRAHAM NEED TO FIX THIS


####################
### SCRIPT START ###
####################

##################
### USER INPUT ###
##################

### REVEIEW THE METADATA TO DETERMINE THE SROUCE CRS OF THE DATA.
print("IF ONLY GDA1994 OR GDA2020 IS EXPLAINED, FIND THE LOCATION ON A MAP TO SEE WHICH ZONE IT IS IN.")




### USER INPUT: Update the file path of the Source file path name
src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Ashburton_LiDAR_1m_DSM_GDA2020.asc" # gda94 mga50 # depite the name of the file
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Burrup_Lidar_30Oct2018_50cm_DSM_Final_GDA2020.asc" # mga50
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Elverdton_Mine_Oct_2022_1m_LiDAR_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Irwin_River_50cm_DEM_Apr_2023_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Oakajee_LiDAR_Jan_2021_1m_DEM_GDA2020.asc" # Oakajee WA near Gealdton
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Perth_1m_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Shire_of_Denmark_Feb_2023_1m_LiDAR_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\South_Metro_Jan_2023_1m_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Town_of_Bassendean_1m_DEM_LiDAR_GDA2020.asc"




### USER INPUT: Identifies the original substring (in the file name) that denotes the CRS, which will be replaced with the standard CRS description (either re-projected or not) 
sub_str = "GDA2020"

### USER INPUT: As a EPSG code, Update the original Coordinate Referance System (crs) of the delievery asc (csv) file, see metadata
src_crs = 28350 # 7850 # 7851

### USER INPUT: As a EPSG code, Update destination Coordinate Referance System (crs) of the rasters # It can be same as the original crs
dst_crs = 28350 # 28351 

#################
### FUNCTIONS ###
#################


def epsg2string(epsg_de_gdf):
    """Prepare a projected "GDA zone" name for file string, should work from GDA ALbers, GDA2020 zone ...and GDA 1994 zone ... """
    
    print("Assessing the EPGS code and converting into a string for the file name...")
    # https://pyproj4.github.io/pyproj/dev/api/crs/crs.html # https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
    #src_gdf.crs.is_projected # this might be needed if the source crs is geographic rather then projected
    
    crs_nom = epsg_de_gdf
    crs_val = {' ': '', '/': '_', 'zone': '','Australia': ''}
    for x,y in crs_val.items(): 
        crs_nom = crs_nom.replace(x, y)
        #epsg_de_gdf = epsg_de_gdf.replace(x, y)
    print(crs_nom)
    
    return crs_nom


def csv2raster(sourceCSV, sourceCRS, destinationCRS, substringCRS): # the last two prarmeters should be the epgs codes in integer, can be the same if no reprojection
    """Reads each CSV files, converts to a gdf, defines is original crs, re-projects it if defined, rasterises it, writes to file."""


    print("Determineing the directories, based on the source filepath...")
    wrk_dir = os.path.join("E:\DWER_LIDAR\Working", os.path.splitext(os.path.basename(sourceCSV))[0])
    csv_dir = os.path.join(wrk_dir, "csv") # this should already be created
    vec_dir = os.path.join(wrk_dir, "vector")
    rst_dir = os.path.join(wrk_dir, "raster")
    
    print("Creating a directory, if not already existing...")
    if not os.path.exists(vec_dir): os.makedirs(vec_dir)
    if not os.path.exists(rst_dir): os.makedirs(rst_dir)

    print("Collating all the csv files to process...")
    search_criteria = "*.csv" # include the 0 so that it exclused final products
    q = os.path.join(csv_dir, search_criteria)
    lst_csv = glob.glob(q)
    
    print("Loop through the csv files and create rasters...")
    for fil_csv in lst_csv[:]:
        print("\n" + fil_csv + "\n")
        
        print("Reading csv... ~ 5 sec")
        src_csv = pd.read_csv(fil_csv, index_col= "id") 
        
        print("Dataframe to Geodataframe...")        
        src_gdf = gpd.GeoDataFrame(src_csv, geometry=gpd.points_from_xy(src_csv.x, src_csv.y)) # Dataframe to geodataframe # sec 3 sec
        
        
        # Adjusting the top and left coords to the centroid coords (a shift of 0.5m) # trasnform() presumes geomtry as top left cnr not centroids
        #src_gdf = gpd.GeoDataFrame(src_csv, geometry=gpd.points_from_xy(src_csv.x - 0.5, src_csv.y - 0.5)) # Dataframe to geodataframe # sec 3 sec
        
        print("Defining crs based on user input: " + str(sourceCRS) + "... (1 secs)")
        src_gdf = src_gdf.set_crs(sourceCRS, allow_override=True) # Define crs as gda2020 zone 50
       
        print("Preparing the file name for writing...")
        dst_nom = os.path.basename(fil_csv[:-4]) # Gettign the name of the file
        
        if sourceCRS != destinationCRS:
            print("Reprojecting gdf to destination crs EPSG: " + str(destinationCRS) + "... (~ 4 sec)")
            src_gdf = src_gdf.to_crs(destinationCRS) # Transform crs to gda94 z50 (4 sec)
            crs_nom = epsg2string(src_gdf.crs.name) # See funtion for details
            #dst_nom = os.path.basename(fil_csv[:-4]).replace("GDA2020", crs_nom) # Ensure that this substring exists, else add searchString as new parameter to function
            dst_nom = os.path.basename(fil_csv[:-4]).replace(substringCRS, crs_nom) # Updates the original substring with standard CRS description
            
        else:
            print("Not reprojecting from EPSG: " + str(sourceCRS))
            
            crs_nom = epsg2string(src_gdf.crs.name) # See funtion for details
            #dst_nom = os.path.basename(fil_csv[:-4]).replace("GDA2020", crs_nom) # Ensure that this substring exists, else add searchString as new parameter to function
            dst_nom = os.path.basename(fil_csv[:-4]).replace(substringCRS, crs_nom) # Updates the original substring with standard CRS description
            #print(src_gdf.crs.name)
            
               
        print("Writing gdf to file... (~30 secs")
        """This works but writing to vector slows to processing down considerably."""
        #dst_vec = os.path.join(vec_dir, dst_nom) # full path for vector files
        #src_gdf.to_file(dst_fil + ".gpkg", layer = "points", driver="GPKG") # time sec 48
        #src_gdf.to_file(dst_fil + ".shp", driver = "ESRI Shapefile")  # time sec 41 and smallest
        #src_gdf.to_file(dst_vec + ".geojson", driver='GeoJSON')  # sec 45
    
        
        #########################
        ### Vector to raster  ###
        #########################  
    
        # https://gis.stackexchange.com/questions/422146/specify-spatial-resolution-using-rasterio-rasterize
        # NEED TO RUN FOR HERE
        print("Calcuating the spatial parameters for rasterising the vector...")
        geom_value = ((geom,value) for geom, value in zip(src_gdf.geometry, src_gdf['z']))    # Calculating the geometry and values
        min_x, min_y, max_x, max_y = src_gdf['geometry'].total_bounds # Calculating the xy coordinates # teh extent is too far south
        print(min_x, min_y, max_x, max_y)

        pixel_size = 1.0 # USER INPUT                                                  # Calculating the transform and determining the pixel size 
        
        # rasterio.transform.from_origin() "Return an Affine transformation given upper left and pixel sizes", so...
        # Adjusting the top and left coords to the centroid coords (a shift of 0.5m)
        transform = rasterio.transform.from_origin(west=min_x + pixel_size / 2, north=max_y + pixel_size / 2, xsize=pixel_size, ysize=pixel_size)
        
        w_px = math.ceil((max_x - min_x) / pixel_size)                                  # Calculating the height and width of the output raster (in pixels)
        h_px = math.ceil((max_y - min_y) / pixel_size)
        
        #
        # Get the larger of the shape dimensions
        if w_px < h_px: shape = h_px, h_px
        else: shape = w_px, w_px
        #shape = 1000 , 1000
        #shape = w_px, w_px
        #shape = w_px, w_px # test 0
        #shape = w_px, h_px # test 1
        #shape = h_px, w_px # test 2
        #shape = h_px, h_px
        #shape = 1000 , 1000
        
        
        # Change the GDAL defaul config to speed up this slow part of theprocessing from 30x2 to 20 + 10sec
        with rasterio.Env(GDAL_CACHEMAX=2048000000, GDAL_NUM_THREADS="ALL_CPUS"):
            #1st confidg for rasterize(), 2nd config for writing to file
        
            print("Rasterising the vector... (~20 sec)")
            image = rasterize(
                geom_value,
                out_shape = shape,
                #out_shape = [w_px, h_px],
                transform = transform,
                all_touched = True,
                fill = -999)
            
            #print("Writing the raster to file... (~ 12 sec)")
            #dst_crs = str(src_gdf.crs).split(":")[1] # The CRS of the gdf2 as a EPSG string
            #spt_res = (str(int(pixel_size)) + "m") # The resolution of the rasterised data
            
            
            print("Writing raster to file...")
            dst_rst = os.path.join(rst_dir, dst_nom) # full path for vector files   
            
            with rasterio.open(dst_rst + ".tif", 'w',
                driver='GTiff',
                dtype=rasterio.float32,
                count=1,
                compress='lzw',
                crs= src_gdf.crs,
                width=shape[0],
                height=shape[1],
                transform=transform,
                nodata=-999
            ) as dst:
                dst.write(image, indexes=1)
    return dst
    print("Telos/Fin!")



### USER INPUT: run the below function
csv2raster(src_fil, src_crs, dst_crs, sub_str)


##################
### USER INPUT ### FINISH
##################

# For debugging only 
# sourceCSV = r"E:\DWER_LIDAR\Working\Elverdton_Mine_Oct_2022_1m_LiDAR_DEM_GDA2020\Elverdton_Mine_Oct_2022_1m_LiDAR_DEM_GDA2020.asc"
# sourceCRS = src_crs
# destinationCRS = dst_crs
# substringCRS = sub_str

##################
### SCRIPT END ###
##################

















"""
import dask_geopandas
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y)) # Dataframe to geodataframe # sec 7 sec
gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df['x'], df['y']))



print("Read csv n rows at a time...") # working
    
    # Fails to read csv at 425000000 of 2864877059 due to "memory error"

    print("Dataframe to Geodataframe...")        
    gdf0 = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y)) # Dataframe to geodataframe # sec 7 sec

    print("Defining   crs to gdf as gda 2020 mga 50... (1 secs)")
    gdf1 = gdf0.set_crs(7850, allow_override=True) # Define crs as gda2020 zone 50
    print("Projecting crs to gdf as gda 1940 mga 50... (1 secs)")
    gdf2 = gdf1.to_crs(28350) # Transform crs to gda94 z50

    
    print("Writing gdf to file... (~30 secs")
    dst_fil = os.path.join(dst_dir, os.path.basename(src_fil)[:-11] + str(counter) + "_gda94_mga50")
    #gdf2.to_file(dst_fil + ".gpkg", layer = "points", driver="GPKG") # time 11 sec


   
    #########################
    ### Vector to raster  ###
    #########################  
    
    # https://gis.stackexchange.com/questions/422146/specify-spatial-resolution-using-rasterio-rasterize
    # NEED TO RUN FOR HERE
    print("Calcuating the spatial parameters for the rasterised vector...")
    geom_value = ((geom,value) for geom, value in zip(gdf2.geometry, gdf2['z']))    # Calculating the geometry and values
    min_x, min_y, max_x, max_y = gdf2['geometry'].total_bounds                      # Calculating the xy coordinates
    
    pixel_size = 1.0 # USER INPUT                                                  # Calculating the transform and determining the pixel size 
    transform = rasterio.transform.from_origin(west=min_x, north=max_y, xsize=pixel_size, ysize=pixel_size)
    
    w_px = math.ceil((max_x - min_x) / pixel_size)                                  # Calculating the height and width of the output raster (in pixels)
    h_px = math.ceil((max_y - min_y) / pixel_size)
                                                                                    # Get the larger of the shape dimensions
    if w_px < h_px: shape = h_px, h_px
    else: shape = w_px, w_px
    #shape = 1000 , 1000
    
    print("Rasterising the vector... (~7 secs)")
    image = rasterize(
        geom_value,
        out_shape = shape,
        transform = transform,
        all_touched = True,
        fill = -999)
    
    
    
    print("Writing the raster to file...")
    dst_crs = str(gdf2.crs).split(":")[1] # The CRS of the gdf2 as a EPSG string
    spt_res = (str(int(pixel_size)) + "m") # The resolution of the rasterised data
    
    dst_fil = os.path.join(dst_dir, os.path.basename(src_fil)[:-11]  + "gda94_mga50_" + spt_res + "_" + str(counter))
    # Writting to file
    with rasterio.open(dst_fil + ".tif", 'w',
        driver='GTiff',
        dtype=rasterio.float32,
        count=1,
        compress='lzw',
        crs= gdf2.crs,
        width=shape[0],
        height=shape[1],
        transform=transform,
        nodata=-999
    ) as dst:
        dst.write(image, indexes=1)
    
"""
    
print("Telos/Fin!")

#525000000 of 2864877059

#Reading... (5 secs)
#Assigning columns [x,y,z]
#Dataframe to Geodataframe...
#Defining   crs to gdf as gda 2020 mga 50... (1 secs)
#Projecting crs to gdf as gda 1940 mga 50... (1 secs)
#Writing gdf to file... (~30 secs
#Calcuating the spatial parameters for the rasterised vector...
#Rasterising the vector... (~7 secs)
#Writing the raster to file...

#550000000 of 2864877059
# MemoryError


