from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime

# The above could be sent to an independent module
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind


class DonchianChannels(bt.Indicator):
    '''
    Params Note:
      - ``lookback`` (default: -1)

        If `-1`, the bars to consider will start 1 bar in the past and the
        current high/low may break through the channel.

        If `0`, the current prices will be considered for the Donchian
        Channel. This means that the price will **NEVER** break through the
        upper/lower channel bands.
    '''

    alias = ('DCH', 'DonchianChannel',)

    lines = ('dcm', 'dch', 'dcl',)  # dc middle, dc high, dc low
    params = dict(
        period=20,
        lookback=-1,  # consider current bar or not
    )

    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        dcm=dict(ls='--'),  # dashed line
        dch=dict(_samecolor=True),  # use same color as prev line (dcm)
        dcl=dict(_samecolor=True),  # use same color as prev line (dch)
    )

    def __init__(self):
        hi, lo = self.data.high, self.data.low
        if self.p.lookback:  # move backwards as needed
            hi, lo = hi(self.p.lookback), lo(self.p.lookback)

        self.l.dch = bt.ind.Highest(hi, period=self.p.period)
        self.l.dcl = bt.ind.Lowest(lo, period=self.p.period)
        self.l.dcm = (self.l.dch + self.l.dcl) / 2.0  # avg of the above


class MultiDataStrategy(bt.Strategy):
    '''
    '''
    params = dict(
        trend_filter_fast_period=50,
        trend_filter_slow_period=100,
        donchian_channel_period=25,
        trailing_stop_atr_period=25,
        trailing_stop_atr_distance=3,
        max_holding_product=5,
        individual_risk_factor=0.002,
        printout=True,
    )

    def __init__(self):
        self.inds = {} 

        for d in self.datas:
            self.inds[d] = {}
            self.inds[d]['fast_ema'] = btind.EMA(period=self.p.trend_filter_fast_period)
            self.inds[d]['slow_ema'] = btind.EMA(period=self.p.trend_filter_slow_period)
            self.inds[d]['long_filter'] = self.inds[d]['fast_ema'] > self.inds[d]['slow_ema']
            self.inds[d]['dc'] = DonchianChannels(period=self.p.donchian_channel_period)
            self.inds[d]['atr'] = btind.ATR(period=self.p.trailing_stop_atr_period)

    def permit_long(self, d):
        no_existing_position = self.getposition(d) == 0
        return no_existing_position and self.inds[d]['long_filter']

    def trigger_long(self, d, i):
        return self.datas[i] > self.inds[d]['dc']

    def open_long(self, d):
        self.buy(d)
        self.sell(exectype=bt.Order.StopTrail, 
                trailamount=self.inds[d]['atr'] * self.p.trailing_stop_atr_distance)

    def cal_global_risk(self):
        ''' Compute global risk 
        根据现在的ATR计算总的risk exposure占的百分比
        '''
        pass

    def notify_order(self):
        # do something...
        self.cal_global_risk() 

    def next(self):
        for i, d in enumerate(self.datas):
            if self.trigger_long(d, i) and self.permit_long(d):
                self.buy(d)
                self.sell(exectype=bt.Order.StopTrail, 
                        trailamount=self.inds[d]['atr'] * self.p.trailing_stop_atr_distance)
      
