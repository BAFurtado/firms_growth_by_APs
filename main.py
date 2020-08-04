# Processing of data for NT
import os
import pandas as pd
import geopandas as gpd
from pyproj import CRS


def load_data():
    r02 = pd.read_csv('../PolicySpace2/input/firms_by_APs2000_dados2002_full.csv', sep=';')
    r10 = pd.read_csv('../PolicySpace2/input/firms_by_APs2010_dados2010_full.csv', sep=';')
    r12 = pd.read_csv('../PolicySpace2/input/firms_by_APs2000_dados2012_full.csv', sep=';')
    r17 = pd.read_csv('../PolicySpace2/input/firms_by_APs2010_dados2017_full.csv', sep=';')
    return r02, r10, r12, r17


def load_shapes():
    path_2010 = '../censo2010/data/areas'
    ap_2010 = os.listdir(path_2010)
    poly = gpd.read_file(f'{path_2010}/11_all_muns.shp')
    aps = list(set(ap[:2] for ap in ap_2010 if 'all_muns' in ap))
    for key in aps:
        if key != '11':
            poly = pd.concat([poly, gpd.read_file(f'{path_2010}/{key}_all_muns.shp')])


def join_by_AP_year(df1, df2):
    df2 = df2.rename(columns={'num_firms': 'num_firms_2'})
    df_joined = pd.merge(df1, df2, on='AREAP')
    return df_joined


def check_crs(dado):
    dado.to_crs(CRS.from_epsg(31983))
    return dado


def merge_growth(df1, df2, ap):
    ntpre = pd.merge(df1, df2, on='AREAP')
    ntpre['cres_17_10'] = (ntpre['num_firms_2'] - ntpre['num_firms'])/ntpre['num_firms']
    nt = pd.merge(ap, ntpre, on='AREAP')
    # nt.to_file('/home/furtadobb/Downloads/nt.shp')


if __name__ == '__main__':
    r02, r10, r12, r17 = load_data()
