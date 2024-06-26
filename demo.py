"""
demo.py
Spring 2022 PJW

Demonstrate intersecting polygons and allocating populations in
proportion to area.
"""

import geopandas as gpd
import matplotlib.pyplot as plt

#%%
#
#  Set up file names
#

demo_file = 'demo.gpkg'
out_file = 'demo-output.gpkg'

#
#  Read the layers; already projected to UTM 18n
#

county = gpd.read_file(demo_file,layer='county')
zips   = gpd.read_file(demo_file,layer='zips')

#
#  Compute the area of zips
#

zips['z_area'] = zips.area

#%%
#
#  Now overlay the county on the zips.
#
#  The "how" keyword determines which slices are returned when the two layers
#  don't overlap exactly: "union" returns all slices (essentially an outer
#  join), "intersection" only returns slices that are part of both layers
#  (essentially an inner join), "symmetric difference" returns slices that
#  are part of one layer but not the other, and "difference" returns slices
#  that are part of the left dataframe but not part of the right.
#

print( '\nCounty:', len(county) )
print( '\nZips:', len(zips) )

slices = zips.overlay(county,how='union',keep_geom_type=True)

print( '\nSlice results:' )
print( slices['COUNTYFP'].value_counts(dropna=False) )

#
#  Remove slice that corresponds to large lakes that don't have zip codes
#

print( '\nSlice with no zip:' )
print( slices[ slices['ZCTA5CE10'].isna() ] )

slices = slices.dropna(subset='ZCTA5CE10')

#%%
#
#  For convenience when plotting, fill in the county field with a
#  placeholder string for the slices that didn't match
#

slices['COUNTYFP'] = slices['COUNTYFP'].fillna('outside')

#
#  Now plot what matched and what didn't
#

fig1,ax1 = plt.subplots(dpi=300)
slices.plot('COUNTYFP',edgecolor='yellow',linewidth=0.2,ax=ax1)
ax1.axis('off')

#%%
#
#  Now compute the area of each slice and its share of its corresponding
#  zip code
#

slices['s_area'] = slices.area
slices['s_shareof_z'] = slices['s_area']/slices['z_area']

print( '\nChecking zips, expect 1:')
print( slices.groupby('ZCTA5CE10')['s_shareof_z'].sum() )

#
#  Split up each zip code's population according to the slice shares
#

slices['s_pop'] = slices['s_shareof_z']*slices['pop_total']

#%%
#
#  Make sure everything worked OK
#

print( '\nChecking total population:' )
print( zips['pop_total'].sum() )
print( slices['s_pop'].sum() )

print( '\nPopulations in and outside county:')
print( slices.groupby('COUNTYFP')['s_pop'].sum() )

#%%
#
#  Plot populations by slice to see where people live
#

fig1,ax1 = plt.subplots(dpi=300)
slices.plot('s_pop',edgecolor='yellow',linewidth=0.2,legend=True,ax=ax1)
county.boundary.plot(color='yellow',linewidth=1,ax=ax1)
ax1.axis('off')

#%%
#
#  Save everything for use with QGIS
#

zips.to_file('demo-output.gpkg',layer='zips')
county.to_file('demo-output.gpkg',layer='county')
slices.to_file('demo-output.gpkg',layer='slices')
