"""
Main driver to read and plot hpc trends data
"""
import os
import dateparser
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
from scipy.stats import linregress
from datetime import datetime
from pandas.plotting import register_matplotlib_converters
from xml.etree.ElementTree import parse

register_matplotlib_converters()
DPI = 150
MARKER = ["or", "ob", 'og', 'or']
LINE = ["r--", "b--", "g--", "r--"]
FIG_WIDTH = 34
FIG_HEIGHT = 20
TIMESTAMP = datetime.now().strftime("%H%M%S")
BAR_WIDTH = 0.35
FONT_SIZE = 40
COLOR_1 = 'tab:blue'
COLOR_2 = 'tab:orange'
COLOR_6 = 'tab:green'
COLOR_3 = 'tab:red'
COLOR_4 = 'tab:purple'
COLOR_5 = 'tab:brown'
COLORS = [COLOR_3, COLOR_6, COLOR_5, COLOR_4]

plt.rcParams.update({'font.size': 45})
plt.rcParams.update({'font.weight': 'bold'})
plt.rcParams['lines.linewidth'] = 4
plt.rcParams['lines.markersize'] = 20
plt.rcParams["font.family"] = "Times New Roman"


def get_tree():
    """
    reads the xml file in data and saves them to a dict
    :return: dict of data file with dates as keys
    """
    etrees = dict()
    _path = os.path.join(os.getcwd(), "data")
    for _filename in os.listdir(_path):
        items = _filename.split('_')
        date = dateparser.parse(items[1] + '01', date_formats=["%Y%m%d"])
        etree = parse("./data/" + _filename)
        etrees[date] = etree
    return etrees


def get_array_of_item_for_rank(_etrees, rank, item):
    """
    get a list of dates and items for a specific rank
    :param _etrees: input xml tree
    :param rank: input specific rank
    :param item: input value item to investigate
    :return: x as date and y as item value lists
    """
    _x = []
    _y = []
    for _k in sorted(_etrees.keys()):
        _x.append(_k)
        _tr = _etrees[_k].getroot()
        for _sc in _tr:
            if int(_sc.find(".//{http://www.top500.org/xml/top500/1.0}rank").
                   text) == rank:
                _y.append(_sc.find(
                    ".//{http://www.top500.org/xml/top500/1.0}" + item).text)
                pass
        pass
    return _x, _y


def regress(_x, _y, x_pred):
    _p = linregress(_x, _y)
    b1, b0, r, p_val, stderr = _p
    y_pred = np.polyval([b1, b0], x_pred)
    return y_pred, _p


if __name__ == "__main__":
    # read xml files
    _etrees = get_tree()
    fig, ax = plt.subplots(1, figsize=(FIG_WIDTH, FIG_HEIGHT))
    _ax = None
    extra_pts = 16

    _rank = [1, 10, 50, 500]
    for _i, _r in enumerate(_rank):
        x, y = get_array_of_item_for_rank(_etrees, _r, "r-max")
        _x_pred = x.copy()
        x_pred_lst = [x[-1] + relativedelta(months=+(_i+1)*6) for _i
                      in range(extra_pts)]
        _x_pred += x_pred_lst
        y = [float(i) for i in y]
        x = np.array(x)
        y = np.array(y)
        _y_pred, _ = regress(np.array([val.timestamp() for val in x]),
                             np.log(y),
                             np.array([val.timestamp() for val in _x_pred]))

        y_legend_list = ["rank #" + str(_rank)]
        ax.semilogy(x, y, MARKER[_i], color=COLORS[_i],
                    label="rank = "+str(_r))
        ax.plot(_x_pred, np.exp(_y_pred), LINE[_i], color=COLORS[_i])

    ax.set_xlabel("Date", fontsize=FONT_SIZE)
    ax.set_ylabel("Performance (GFlops/sec)", fontsize=FONT_SIZE)
    ax.grid()
    ax.legend(loc='upper left')
    fig.tight_layout()
    plt.savefig(TIMESTAMP + ".png", format='png', dpi=DPI)
    plt.show()

    pass
