import os
import warnings

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.style
import pandas as pd

from colors import colors as cor

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


def distance_to_tops(ap, name, dist_parameter=50):
    # 1% of top APs
    how_many = int(len(ap)/dist_parameter)
    if how_many < 3:
        how_many = 3
    ap = ap.sort_values(by='num_firms_', ascending=False).reset_index(drop=True)
    cols = list()
    for i in range(how_many):
        col = f'd_top{i + 1}'
        cols.append(col)
        ap[col] = ap.geometry.centroid.distance(ap.loc[i].geometry.centroid)
    ap['closest'] = ap[cols].min(axis=1)
    top, div, labels = get_range(ap, 'closest')
    try:
        ap['closest_q'] = pd.cut(ap.closest, range(0, top, div), right=False, labels=labels)
    except ValueError:
        ap['closest_q'] = pd.cut(ap.closest, range(0, top + 1, div), right=False, labels=labels)
        print(top, div, name)
    ap.closest_q = ap.closest_q.astype(str)
    out = ap.groupby(by='closest_q').agg('mean')['cres_17_10']
    out.name = name
    # ap.to_file(f'results/{name}.shp')
    return ap, out


def main():
    shps = load_shapes()
    out_shps = dict()
    classification = pd.DataFrame()
    for key in shps:
        out_shps[key], out = distance_to_tops(shps[key], name=key)
        classification = pd.merge(classification, out, right_index=True, left_index=True, how='outer')
    # classification.to_csv('results/output.csv', sep=';')
    return classification


def plotting(data, mean_color='red', many=False, ax=None):
    matplotlib.style.use('seaborn')
    try:
        data.index = data.closest_q
        data = data.drop('closest_q', axis=1)
    except AttributeError:
        pass
    if not many:
        fig, ax = plt.subplots()
        for i, col in enumerate(data.columns):
            ax.plot(data.index, data[col], color=cor[i], label=col[:2])
        ax.legend(frameon=False, ncol=5)
        plt.show()
        fig, ax = plt.subplots()
    ax.plot(data.index, data.mean(axis=1), color=mean_color, linewidth=3, alpha=.8, label='mean')
    ax.plot(data.index, data.mean(axis=1) + data.std(axis=1), color='red', linewidth=3, alpha=.4)
    ax.plot(data.index, data.mean(axis=1) - data.std(axis=1), color='red', linewidth=3, alpha=.4)
    ax.legend(frameon=False)


if __name__ == '__main__':
    values_dist = [10, 25, 50, 100]
    cs = ['violet', 'red', 'grey', 'black']
    fig, axes = plt.subplots()
    for i, v in enumerate(values_dist):
        d = main()
        plotting(d, mean_color=cs[i], many=True, ax=axes)


