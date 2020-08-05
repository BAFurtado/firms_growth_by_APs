# Processing of data for NT
import os
import warnings
from typing import List

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from pyproj import CRS

warnings.filterwarnings("ignore", "Only Polygon objects", UserWarning)


def load_data():
    # r02 = pd.read_csv('../PolicySpace2/input/firms_by_APs2000_dados2002_full.csv', sep=';')
    r10 = pd.read_csv('../PolicySpace2/input/firms_by_APs2010_dados2010_full.csv', sep=';')
    # r12 = pd.read_csv('../PolicySpace2/input/firms_by_APs2000_dados2012_full.csv', sep=';')
    r17 = pd.read_csv('../PolicySpace2/input/firms_by_APs2010_dados2017_full.csv', sep=';')
    # return r02, r10, r12, r17
    return r10, r17


def load_shapes():
    path_2010 = '../censo2010/data/areas'
    ap_2010: List[str] = os.listdir(path_2010)
    shps = dict()
    aps = list(set(ap[:2] for ap in ap_2010 if 'all_muns' in ap))
    for key in aps:
        shps[key] = gpd.read_file(f'{path_2010}/{key}_all_muns.shp')
        # Lines below were run just once
    #     shps[key] = check_crs(shps[key])
    #     shps[key].to_file(f'{path_2010}/{key}_all_muns.shp')
    return shps


def join_by_ap_year(df1, df2, col):
    df2 = df2.rename(columns={'num_firms': 'num_firms_2'})
    df_joined = pd.merge(df1, df2, on=col)
    return df_joined


def check_crs(dado):
    return dado.to_crs(CRS.from_epsg(31983))


def merge_growth(df, aps, col):
    df['cres_17_10'] = (df['num_firms_2'] - df['num_firms'])/df['num_firms']
    result = dict()
    for ap in aps:
        temp = df[df[col].astype(str).str[:2] == ap]
        result[ap] = pd.merge(aps[ap], temp, on=col)
    return result


def plt_hist(*args):
    fig, ax = plt.subplots()
    for each in args:
        ax.hist(each['num_firms'], bins=20, alpha=.4)
    ax.set_xlim(0, 10000)
    plt.show()


def main():
    col = 'AREAP'
    # r02, r10, r12, r17 = load_data()
    r10, r17 = load_data()
    # plt_hist(r02, r12)
    # plt_hist(r10, r17)
    # r2_12 = join_by_ap_year(r02, r12, 'AP')
    r10_17 = join_by_ap_year(r10, r17, col)
    # return r2_12, r10_17
    shps = load_shapes()
    result = merge_growth(r10_17, shps, col)
    return result


if __name__ == '__main__':
    # TODO: Produce Area bin and count the average per area bin?
    # TODO: Calculate distance to nearest larger pole of the state (percentage of AREAPs).
    #  Divide distance in bins and average growth?
    # a, b = main()
    # shps = load_shapes()
    a = main()
    [a[key].to_file(f'aps_2010_rais_10_17_ufs/{key}.shp') for key in a]
