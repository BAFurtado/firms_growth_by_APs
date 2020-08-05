import pandas as pd
import geopandas as gpd
import warnings
import os


warnings.filterwarnings("ignore", "Only Polygon objects", UserWarning)


def set_area(aps: dict):
    for ap in aps:
        aps[ap]['area'] = aps[ap].area


def load_shapes():
    path = 'aps_2010_rais_10_17_ufs'
    aps = list(set(ap for ap in os.listdir(path) if 'shp' in ap))
    res = dict()
    for ap in aps:
        res[ap] = gpd.read_file(f'{path}/{ap}')
    return res


def get_range(ap, col='dist_to_top'):
    top = int(ap[col].max()) + 100
    div = int(top / 10)
    labels = [f"q.{i}-{i + 10}" for i in range(0, 100, 10)]
    return top, div, labels


def distance_to_largest(ap):
    ap = ap.sort_values(by='num_firms_', ascending=False).reset_index(drop=True)
    ap['dist_to_top'] = ap.geometry.centroid.distance(ap.loc[0].geometry.centroid)
    top, div, labels = get_range(ap)
    ap['d_to_top_q'] = pd.cut(ap.dist_to_top, range(0, top, div), right=False, labels=labels)
    ap.d_to_top_q = ap.dist_to_top_q.astype(str)
    print(ap.groupby(by='d_to_top_q').agg('mean')['cres_17_10'])


def distance_to_tops(ap):
    # 1% of top APs
    how_many = int(len(ap)/25)
    ap = ap.sort_values(by='num_firms_', ascending=False).reset_index(drop=True)
    cols = list()
    for i in range(how_many):
        col = f'd_top{i + 1}'
        cols.append(col)
        ap[col] = ap.geometry.centroid.distance(ap.loc[i].geometry.centroid)
    ap['closest'] = ap[cols].min(axis=1)
    top, div, labels = get_range(ap, 'closest')
    ap['closest_q'] = pd.cut(ap.closest, range(0, top, div), right=False, labels=labels)
    ap.closest_q = ap.closest_q.astype(str)
    print(ap.groupby(by='closest_q').agg('mean')['cres_17_10'])
    ap.to_file('ap.shp')
    return ap


if __name__ == '__main__':
    # shps = load_shapes()
    a = gpd.read_file('aps_2010_rais_10_17_ufs/52.shp')
    a = distance_to_tops(a)
