from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from backtrader.dataseries import TimeFrame
from backtrader.cerebro import OptReturn

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0], safediv=True) # - zero div error
        bt.indicators.MACDHisto(self.datas[0]) 
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    # cerebro.addstrategy(TestStrategy)
    strats = cerebro.optstrategy(
        TestStrategy,
        maperiod=range(10, 31))

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../datas/orcl-1995-2014.txt')
    # datapath = 'datas/orcl-1995-2014.txt'

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        # fromdate=datetime.datetime(2000, 1, 1),
        # Do not pass values before this date
        # todate=datetime.datetime(2000, 12, 31),
        # Do not pass values after this date
        reverse=False)

    # firstrate_path = '/Users/jinchaolin/FirstRateReady/futures-active_adjusted_1min_8sjor/'
    # firstrate_file = params.product + '_continuous_adjusted_1min.txt'
    # dataname = firstrate_path + firstrate_file
    # data = bt.feeds.GenericCSVData(
    #     dataname = '/Users/jinchaolin/FirstRateReady/futures-active_adjusted_1min_8sjor/ES_continuous_adjusted_1min.txt',
    #     fromdate = datetime.datetime(2017, 1, 1), 
    #     todate = datetime.datetime(2019, 1, 1), 
    #     # nullvalue = 0.0, 
    #     dtformat = ('%Y-%m-%d %H:%M:%S'),
    #     openinterest = -1
    # )
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Add analyzer 
    import backtrader.analyzers as btanalyzers
    # cerebro.addanalyzer(btanalyzers.Returns, _name='return')
    # cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual_return')
    # log_return_analyzer = btanalyzers.LogReturnsRolling(timeframe=bt.TimeFrame.Months) # 这样不行，为什么？
    # cerebro.addanalyzer(log_return_analyzer, _name='log_returns_rolling')
    cerebro.addanalyzer(btanalyzers.LogReturnsRolling, 
                        _name='annual_return', 
                        timeframe=bt.TimeFrame.Months
                        ) # Good! 
    
    # cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe') # 不懂为什么加一个analyzer整个代码都不对了
    # cerebro.addanalyzer(btanalyzers.Calmar, _name='trade_analyzer')  # 有问题\
    
    # cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trade_analyzer')
    # cerebro.addanalyzer(btanalyzers.DrawDown, _name='draw_down')
    # cerebro.addanalyzer(btanalyzers.TimeDrawDown, _name='time_draw_down')
    # cerebro.addanalyzer(btanalyzers.GrossLeverage, _name='gross_leverage')

    # cerebro.addanalyzer(btanalyzers.PeriodStats, _name='period_stats')  # 有问题
    # cerebro.addanalyzer(btanalyzers.PositionsValue, _name='position_value')# 有问题
    # cerebro.addanalyzer(btanalyzers.PyFolio, _name='pyfolio')# 有问题
    # cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
    cerebro.addanalyzer(btanalyzers.TimeReturn, _name='time_return', timeframe=bt.TimeFrame.Months)
    # cerebro.addanalyzer(btanalyzers.Transactions, _name='transactions')
    # cerebro.addanalyzer(btanalyzers.VWR, _name='variability_weighted_return')


    # Set our desired cash start
    cerebro.broker.setcash(1_000_000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Define commission
    commES = bt.CommissionInfo(commission=2.0, margin=5000.0, mult=50.0)

    # Set the commission
    # cerebro.broker.setcommission(commission=0.001)
    # cerebro.broker.setcommission(commission=2.0, margin=5000.0, mult=50.0, name='ES')
    cerebro.broker.addcommissioninfo(commES, name='ES')

    # Add a writer 
    cerebro.addwriter(bt.WriterFile, out='bt_res_2', csv=True)
    cerebro.addwriter(bt.WriterFile, out='bt_res', log_dir='/Users/jinchaolin/TradingBT/log/tmp/', csv=True)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    # res = cerebro.run()
    # res = cerebro.run(maxcpus=8, OptReturn=False) # 为什么True和False返回的结果一样？？
    res = cerebro.run(OptReturn=False)
    # True and False 都无法plot？

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    import pdb; pdb.set_trace();

    # Plot the result
    cerebro.plot()