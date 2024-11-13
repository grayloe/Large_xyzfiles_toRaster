# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 13:31:00 2024

@author: GrahamLoewenthal
"""


import os
from dask import dataframe as dd

################################################
### READING CSV FILES AS PARTITIONS VIA DASK ###
################################################

src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\200968_Pilbara_Rivers_Area1_DEM_1m_GDA2020_Area1.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Ashburton_LiDAR_1m_DSM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Burrup_Lidar_30Oct2018_50cm_DSM_Final_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Elverdton_Mine_Oct_2022_1m_LiDAR_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Irwin_River_50cm_DEM_Apr_2023_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Oakajee_LiDAR_Jan_2021_1m_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Perth_1m_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Shire_of_Denmark_Feb_2023_1m_LiDAR_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\South_Metro_Jan_2023_1m_DEM_GDA2020.asc"
#src_fil = r"E:\DWER_LIDAR\Source\838580 DBCA lidar\Town_of_Bassendean_1m_DEM_LiDAR_GDA2020.asc"

### determining the data structure on a subset ###
import pandas as pd
df = pd.read_csv(src_fil, nrows=7)
df = pd.read_csv(src_fil).sample(n=10)
###

wrk_dir = os.path.join("E:\DWER_LIDAR\Working", os.path.splitext(os.path.basename(src_fil))[0])
csv_dir = os.path.join(wrk_dir, "csv")

def read_csv_dask(fcsv):
    """ https://www.coiled.io/blog/dask-read-csv-to-dataframe"""

    print("Reading file via dask (parallel processing) as partitions...")
    print(fcsv)    
    ddf = dd.read_csv(fcsv, delim_whitespace=True, names=["x","y","z"]) # default chunks are based on available memory
    
    ddf.index = ddf.index + 1 # Start the index value at 1 not at 0
    ddf = ddf.reset_index() # Create a new index, retaining the old index as the first column
    ddf.columns =['id', 'x', 'y', 'z'] # rename the columns 
    
    print("Creating a csv folder, if not already existing...")
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    else:
        pass
    
    
    print("Writing the partitions to csv files to:")
    csv_fil = os.path.join(wrk_dir, "csv",  os.path.basename(fcsv)[:-4] + "_*.csv") # file name was wildcard for partitions
    print(csv_fil)
    
    ddf.to_csv(csv_fil, index=False) # 1 hours to write all the partitions to file (Denmark csv took 1 hour to process)
    return ddf
    
    print("Les files csv sont completes... Telos/Fin!")

# Execute the function:    
read_csv_dask(src_fil) # a path as a string
