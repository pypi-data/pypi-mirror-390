import pandas as pd
import numpy as np
import qis as qis
import seaborn as sns
from matplotlib import pyplot as plt
from typing import Optional, Union
from enum import Enum
from qis import PerfStat

from mac_portfolio_optimizer import (load_mac_portfolio_universe, SaaPortfolio, TaaPortfolio)



def plot_basket(prices: pd.DataFrame, benchmark_price: pd.Series, title: str):
    perf_columns = [PerfStat.PA_RETURN,
                    PerfStat.VOL,
                    PerfStat.SHARPE_RF0,
                    PerfStat.MAX_DD,
                    PerfStat.SKEWNESS,
                    PerfStat.ALPHA_AN,
                    PerfStat.BETA,
                    PerfStat.R2,
                    PerfStat.ALPHA_PVALUE]

    fig = qis.plot_ra_perf_table_benchmark(prices=prices,
                                           benchmark_price=benchmark_price,
                                           perf_params=qis.PerfParams(freq='QE', freq_drawdown='ME', alpha_an_factor=4.0),
                                           perf_columns=perf_columns,
                                           title=f"{title}: {qis.get_time_period(df=prices).to_str()}",
                                           digits_to_show=1,
                                           heatmap_columns=[3],
                                           rows_edge_lines=[1,2,3])
    return fig


class LocalTests(Enum):
    BBG_DATA = 1
    INSURANCE_LINKED = 2
    PRIVATE_EQUITY = 3
    HEDGE_FUNDS = 4
    REAL_ASSETS = 5


def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    import mac_portfolio_optimizer.local_path as lp
    local_path = f"{lp.get_resource_path()}"
    # local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//Figures//"
    local_path_out = lp.get_output_path()

    universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC)

    prices = universe_data.get_joint_prices(apply_unsmoothing_for_pe=True)
    [print(f"{x }") for x in prices.columns]
    cma_prices = qis.load_df_from_csv(file_name='cma_prices', local_path=lp.get_resource_path())
    benchmark_price = cma_prices['60/40'].asfreq('D').ffill()
    start_date = '31Dec2017'

    print(cma_prices['60/40'].dropna())
    if local_test == LocalTests.BBG_DATA:
        from bbg_fetch import fetch_field_timeseries_per_tickers
        tickers = {'HFRXGL Index': 'Hedge Funds UCITS',
                   'SRGLTRR Index': 'Insurance Linked Securities',
                   'NPPIODIV Index': 'Real Estate Direct',
                   'AOR US Equity': '60/40'}
        prices = fetch_field_timeseries_per_tickers(tickers=tickers)
        qis.save_df_to_csv(df=prices, file_name='cma_prices', local_path=lp.get_resource_path())
        qis.plot_prices_with_dd(prices=prices, perf_params=qis.PerfParams(freq='QE'))

    elif local_test == LocalTests.INSURANCE_LINKED:
        mac_tickers = ['Fermat CAT Bond Fund-F USD']
        ac_prices = pd.concat([cma_prices['Insurance Linked Securities'], prices[mac_tickers]], axis=1)
        ac_prices = ac_prices.dropna(axis=0, how='all').loc[start_date:, :]
        # qis.plot_prices_with_dd(prices=ac_prices, perf_params=qis.PerfParams(freq='QE'))
        plot_basket(prices=ac_prices, benchmark_price=benchmark_price, title='Insurance Linked Securities')

    elif local_test == LocalTests.PRIVATE_EQUITY:
        mac_tickers = ['Hamilton Lane Global Private Assets Fund USD',
                       'Franklin Lexington Private Markets Fund SICAV - Flex Feeder I USD']

        basket_prices = qis.backtest_model_portfolio(prices=prices[mac_tickers],
                                                     weights=np.ones(len(mac_tickers))/len(mac_tickers),
                                                     ticker='EqualWeightBasketFunds',
                                                     rebalancing_freq='YE').get_portfolio_nav()

        ac_prices = pd.concat([prices['Private Equity'].rename('MSCI PE Index'),
                               basket_prices, prices[mac_tickers],
                               ], axis=1).asfreq('QE', method='ffill')

        ac_prices = ac_prices.dropna(axis=0, how='all').loc[start_date:, :]
        print(ac_prices)
        # qis.plot_prices_with_dd(prices=ac_prices, perf_params=qis.PerfParams(freq='QE'))
        plot_basket(prices=ac_prices, benchmark_price=benchmark_price, title='Private Equity')

    elif local_test == LocalTests.HEDGE_FUNDS:
        mac_tickers = ['Brummer Multi-Strategy Fund USD',
                       'HSBC Portfolio Selection - HSBC GH Fund R - USD',
                       'Seligman Tech Spectrum Offshore Fund - Class A',
                       'Antarctica Alpha Access Portfolio FHE Fund Class B USD',
                       'Jupiter Asset Management Series PLC - Jupiter Merian Global Equity Absolute Return Fund ',
                       'Neuberger Berman US Equity Premium Fund',
                       'Neuberger Berman Uncorrelated Strategies Fund',
                       'LGT Crown Systematic Trading Strategy H USD'
                       ]

        basket_prices = qis.backtest_model_portfolio(prices=prices[mac_tickers],
                                                     weights=np.ones(len(mac_tickers)) / len(mac_tickers),
                                                     ticker='EqualWeightBasketFunds',
                                                     rebalancing_freq='YE').get_portfolio_nav()

        ac_prices = pd.concat([cma_prices['Hedge Funds UCITS'].rename('Hedge Funds UCITS'),
                               basket_prices,
                               prices[mac_tickers]
                               ], axis=1).asfreq('QE').ffill()

        ac_prices = ac_prices.dropna(axis=0, how='all').loc[start_date:, :]
        # qis.plot_prices_with_dd(prices=ac_prices, perf_params=qis.PerfParams(freq='QE'))
        plot_basket(prices=ac_prices, benchmark_price=benchmark_price, title='Hedge Funds')

    elif local_test == LocalTests.REAL_ASSETS:
        mac_tickers = ['L&G Multi Strategy Enhanced Commodities UCITS ETF',
                       'LGT PB Asian REITs Fund USD - IM',
                       'Vanguard Real Estate ETF',
                       'Janus Henderson Horizon Asia-Pacific Property Equities Fund',
                       'NORDEA 1 SICAV - Global Real Estate Fund '
                       ]

        basket_prices = qis.backtest_model_portfolio(prices=prices[mac_tickers],
                                                     weights=np.ones(len(mac_tickers)) / len(mac_tickers),
                                                     ticker='EqualWeightBasketFunds',
                                                     rebalancing_freq='YE').get_portfolio_nav()

        ac_prices = pd.concat([cma_prices['Real Estate Direct'].rename('Real Estate Direct: NPPIODIV'),
                               basket_prices,
                               prices[mac_tickers]
                               ], axis=1).asfreq('QE').ffill()

        ac_prices = ac_prices.dropna(axis=0, how='all').loc[start_date:, :]
        # qis.plot_prices_with_dd(prices=ac_prices, perf_params=qis.PerfParams(freq='QE'))
        plot_basket(prices=ac_prices, benchmark_price=benchmark_price, title='Real Estate / Assets')

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.INSURANCE_LINKED)
