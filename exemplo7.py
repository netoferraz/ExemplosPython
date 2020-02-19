import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from cartopy.feature import NaturalEarthFeature, BORDERS
import cartopy.crs as ccrs
#from matplotlib.axes import Axes
#from cartopy.mpl.geoaxes import GeoAxes
#GeoAxes._pcolormesh_patched = Axes.pcolormesh

""" Calculo da diferenca sazonal entre a precipitacao e a 
ET0 para o Brasil utilizando os dados gradeados 
(periodo de 1980/01/01  a 2009/12/31)
"""

# pegando variavel
path_var = '/home/alexandre/Dropbox/ParaUbuntu/netcdfgrid3/'
ETo = xr.open_mfdataset(path_var + 'ETo_daily_UT_Brazil_v2*1.nc', combine='by_coords')
prec = xr.open_mfdataset(path_var + 'prec_daily_UT_Brazil_v2*1.nc', combine='by_coords')

# criando mascara para o continente e mar
mask_ocean = 2 * np.ones(prec['prec'].shape[1:]) * np.isnan(prec['prec'].isel(time=0))
mask_land = 1 * np.ones(prec['prec'].shape[1:]) * ~np.isnan(prec['prec'].isel(time=0))
mask_array = mask_ocean + mask_land

# incorporando mascara em ETo
ETo.coords['mask'] = (('latitude', 'longitude'), mask_array)

# definindo limites estaduais
states = NaturalEarthFeature(category='cultural', scale='50m',
                             facecolor='none',
                             name='admin_1_states_provinces_shp')

# intervalo da seria historica para os calculos e
# reamostrando para a media mensal diaria
date_start, date_end = '1980-01-01', '2009-12-31'

EToSlice = ETo['ETo'].loc[dict(time=slice(date_start, date_end))].resample(time='M').mean('time')
precSlice = prec['prec'].loc[dict(time=slice(date_start, date_end))].resample(time='M').mean('time')

# agrupando nas estacoes ('DJF', 'MAM', 'JJA', 'SON')
EToSeason = EToSlice.groupby('time.season').mean(dim='time')
precSeason = precSlice.groupby('time.season').mean(dim='time')

# calculando diferencas sazonais entre prec e ETo
diff = precSeason - EToSeason

# plotando
fig, axes = plt.subplots(nrows=4, ncols=3,
                         figsize=(12,10),
                         subplot_kw={'projection':ccrs.PlateCarree()})

for i, season in enumerate(('DJF', 'MAM', 'JJA', 'SON')):
    precSeason.where(ETo.mask == 1).sel(season=season).plot(
        ax=axes[i, 0], transform=ccrs.PlateCarree(), cmap='Spectral',
        vmin=0, vmax=10, extend='both',)

    EToSeason.where(ETo.mask == 1).sel(season=season).plot(
        ax=axes[i, 1],  transform=ccrs.PlateCarree(), cmap='Spectral_r',
        vmin=2, vmax=6, extend='both',)

    diff.where(ETo.mask == 1).sel(season=season).plot(
        ax=axes[i, 2],  transform=ccrs.PlateCarree(), cmap='RdBu',
        vmin=-5, vmax=5, extend='both',)

    axes[i, 0].text(-78, -15, season,
                    rotation='vertical',
                    rotation_mode='anchor',)
    axes[i, 1].set_ylabel('')
    axes[i, 2].set_ylabel('')

for ax in axes.flat:
    ax.axes.get_xaxis().set_ticklabels([])
    ax.axes.get_yaxis().set_ticklabels([])
    ax.axes.axis('tight')
    ax.set_xlabel('')
    ax.set_title('')
    ax.coastlines()
    ax.add_feature(states, edgecolor='gray', facecolor='none')
    ax.add_feature(BORDERS)
    ax.set_extent([-75, -33, -34, 6])

axes[0, 0].set_title('Prec (mm dia$^{-1}$)')
axes[0, 1].set_title('ETo (mm dia$^{-1}$)')
axes[0, 2].set_title('Prec - ETo')

fig.suptitle(u'Diferença sazonal entre precipitação e ETo',
             fontsize=16, y=.98)
