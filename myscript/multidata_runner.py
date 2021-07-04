from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from backtrader.dataseries import TimeFrame
from backtrader.cerebro import OptReturn

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.analyzers as btanalyzers
from myscript.trend_follow_st import *


def multi_data_runner():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiDataStrategy)

    firstrate_path = '/Users/jinchaolin/FirstRateReady/futures-active_adjusted_1min_8sjor/'
    firstrate_file = 'ES' + '_continuous_adjusted_1min.txt'
    dataname = firstrate_path + firstrate_file
    data = bt.feeds.GenericCSVData(
        dataname = dataname,
        fromdate = datetime.datetime(2017, 1, 1), 
        todate = datetime.datetime(2019, 1, 1), 
        # nullvalue = 0.0, 
        dtformat = ('%Y-%m-%d %H:%M:%S'),
        openinterest = -1
    )
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    cerebro.addanalyzer(btanalyzers.TimeReturn, _name='time_return', timeframe=bt.TimeFrame.Months)
    cerebro.broker.setcash(500_000.0)

    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    commES = bt.CommissionInfo(commission=2.0, margin=5000.0, mult=50.0)
    cerebro.broker.addcommissioninfo(commES, name='ES')
    res = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    import pdb; pdb.set_trace();

    cerebro.plot()