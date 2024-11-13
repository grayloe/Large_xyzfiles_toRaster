# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 10:23:00 2024

@author: GrahamLoewenthal
"""

import os
import rasterio
import rasterio.mask
import geopandas as gpd

#src_til = r"E:\DWER_LIDAR\Source\Landgate_25k_topo_maps\Landgate_25k_topo_maps_gda1994mga50.geojson"
#mannual selction of the tiles that overlap the Denamrk raster
src_til = r"E:\DWER_LIDAR\Working\Shire_of_Denmark_Feb_2023_1m_LiDAR_DEM_GDA2020\tiles\Landgate_25k_topo_maps_gda94mga50_DemarkTilesOnly.geojson"
src_rst = r"E:\DWER_LIDAR\Working\Shire_of_Denmark_Feb_2023_1m_LiDAR_DEM_GDA2020\raster/Shire_of_Denmark_Feb_2023_1m_LiDAR_DEM_GDA1994_MGA50.tif"
dst_dir = r"E:\DWER_LIDAR\Working\Shire_of_Denmark_Feb_2023_1m_LiDAR_DEM_GDA2020\tiles"

print("Lire les vectors...\n", src_til)
src_gdf = gpd.read_file(src_til)


tot_row = src_gdf.index.max() # counting only

for index, row in src_gdf.iterrows(): 
    #print(index, row) 
    print("\nTile ", index, " of ", tot_row) 
    
    print("Cleaning the name variable...")
    suf_fix = row["Map_Name"].split("-")[0].lower().title().replace(" ", "_") + "_" + row["Map_Name"].split("-")[1]
    #print(suf_fix)
    print("Preparing the destination path name...")
    dst_fil = os.path.basename(src_rst)[:-4] + "_tile_" + str(index) 
    dst_fil = os.path.basename(src_rst)[:-4] + "_tile_" + suf_fix
    dst_rst = os.path.join(dst_dir, dst_fil)
    print(os.path.dirname(dst_rst))
    print(os.path.basename(dst_rst))
    
    print("Extracting the geometry of the vector tile...")
    geometry = row['geometry']
    #geom = shapely.to_geojson(geometry)

    # rasterio.mask  cannot process the variable geometry because
    # "TypeError: 'MultiPolygon' object is not iterable"
    # replace geometry with [geometry], as a list to be iterable


    print("Masking out data bjeyound the vector tile geometry...")
    # https://rasterio.readthedocs.io/en/stable/topics/masking-by-shapefile.html
    with rasterio.open(src_rst) as src:
        out_image, out_transform = rasterio.mask.mask(src, [geometry], crop=True)
        out_meta = src.meta
    
    print("Updating the raster profile to that of the new mask...")
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform,
                     "compression" : "lzw"})
    
    print("Writting the mask to file...")
    with rasterio.open(dst_rst + ".tif", "w", **out_meta) as dest:
        dest.write(out_image)
    



