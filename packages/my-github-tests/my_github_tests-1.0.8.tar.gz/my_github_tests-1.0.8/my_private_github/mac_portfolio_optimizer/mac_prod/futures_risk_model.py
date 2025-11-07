"""
each factor is constructed as portfolio with long-term vol factor of 10%
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import qis as qis
from typing import Tuple, Union
from qis import TimePeriod
from enum import Enum

import mac_portfolio_optimizer.local_path as lp

TIME_PERIOD = qis.TimePeriod('31Dec2004', '30Sep2025')


class RiskFactors(str, Enum):
    EQUITY = 'Equity'
    RATES = 'Rates'
    CREDIT = 'Credit'
    PE = 'PE premia'
    CARRY = 'Carry premia'
    INFLATION = 'Inflation premia'


def compute_equity_factor(futures_prices: pd.DataFrame,
                          is_portfolio_vol_target: bool = True,
                          rebalancing_freq: str = 'QE',
                          portfolio_vol_target: float = 0.15,
                          vol_span: int = 3*52,
                          verbose: bool = False
                          ) -> pd.Series:
    prices = futures_prices[['NDDUWI']]
    strategic_weights = np.array([1.0])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.EQUITY.value)
    factor = portfolio_data.get_portfolio_nav()
    if verbose:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return factor


def compute_bond_factor(futures_prices: pd.DataFrame,
                        is_portfolio_vol_target: bool = True,
                        rebalancing_freq: str = 'ME',
                        portfolio_vol_target: float = 0.15,
                        vol_span: int = 3*52,
                        verbose: bool = False
                        ) -> pd.Series:

    prices = futures_prices[['TY1', 'RX1', 'G1', 'JB1', 'CN1', 'XM1']]
    strategic_weights = np.array([0.6, 0.1, 0.1, 0.1, 0.05, 0.05])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.RATES.value)
    factor = portfolio_data.get_portfolio_nav()
    if verbose:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return factor


def compute_credit_factor(futures_prices: pd.DataFrame,
                          is_portfolio_vol_target: bool = True,
                          rebalancing_freq: str = 'ME',
                          portfolio_vol_target: float = 0.15,
                          vol_span: int = 3*52,
                          verbose: bool = False
                          ) -> pd.Series:
    prices = futures_prices[['IG', 'CDX']]
    strategic_weights = np.array([0.66, 0.34])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.CREDIT.value)
    factor = portfolio_data.get_portfolio_nav()
    if verbose:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return factor


def compute_pe_premia_factor(futures_prices: pd.DataFrame,
                             is_portfolio_vol_target: bool = True,
                             rebalancing_freq: str = 'ME',
                             portfolio_vol_target: float = 0.15,
                             vol_span: int = 3*52,
                             verbose: bool = False
                             ) -> pd.Series:
    #futures_prices = load_base_futures_prices()[['NQ1 Index', 'ES1 Index']].dropna()
    #strategic_weights = np.array([1.0, -1.0])
    # futures_prices = load_base_futures_prices()[['NQ1', 'RTY1', 'SPW']].dropna()
    # strategic_weights = np.array([0.5, 0.5, -1.0])
    #prices = futures_prices[['NQ1', 'RTY', 'CDX', 'ES1']]
    #strategic_weights = np.array([0.5, 0.5, 1.0, -1.0])
    #prices = futures_prices[['NQ1', 'RTY',  'ES1']]
    #strategic_weights = np.array([0.5, 0.5, -1.0])
    #prices = futures_prices[['NQ1', 'CDX', 'ES1']] #best so far
    #strategic_weights = np.array([1.0, 1.0, -1.0])
    # prices = futures_prices[['NQ1', 'RTY', 'CDX', 'NDDUWI']]
    #prices = futures_prices[['NQ1', 'RTY', 'CDX', 'ES1']]
    #strategic_weights = np.array([0.5, 0.5, 1.0, -1.0])
    prices = futures_prices[['NQ1', 'RTY', 'CDX', 'NDDUWI']]
    strategic_weights = np.array([0.4, 0.4, 0.4, -1.0])

    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.PE.value)
    factor = portfolio_data.get_portfolio_nav()
    #if verbose:
    #qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return factor


def compute_carry_premia_factor(futures_prices: pd.DataFrame,
                                    verbose: bool = True,
                                    is_portfolio_vol_target: bool = True,
                                    rebalancing_freq: str = 'ME',
                                    portfolio_vol_target: float = 0.15,
                                    vol_span: int = 3*52
                                    ) -> pd.Series:

    # prices = futures_prices[['FF1', 'SFR1', 'JPY', 'AUD', 'IG', 'CDX', 'GLD']]
    # strategic_weights = np.array([10.0, -10.0, 0.5, -0.5, -4.0, -1.0, 0.33])
    # strategic_weights = -1.0*strategic_weights
    prices = futures_prices[['JPY', 'AUD', 'NZD']]
    strategic_weights = np.array([-1.0, 0.5, 0.5])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.CARRY.value)
    factor = portfolio_data.get_portfolio_nav()
    if verbose:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
        figs = qis.generate_strategy_factsheet(portfolio_data=portfolio_data,
                                               benchmark_prices=futures_prices['ES1'],
                                               time_period=TIME_PERIOD,
                                               add_current_position_var_risk_sheet=True,
                                               **qis.fetch_default_report_kwargs(time_period=TIME_PERIOD))
        qis.save_figs_to_pdf(figs=figs,
                             file_name=f"{RiskFactors.CARRY.value}_portfolio",
                             local_path=lp.get_output_path())
    return factor


def compute_inflation_premia_factor(futures_prices: pd.DataFrame,
                                    verbose: bool = True,
                                    is_portfolio_vol_target: bool = True,
                                    rebalancing_freq: str = 'ME',
                                    portfolio_vol_target: float = 0.15,
                                    vol_span: int = 3*52
                                    ) -> pd.Series:

    prices = futures_prices[['I10Y']] # cry
    strategic_weights = np.array([1.0])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.INFLATION.value)    
    factor = portfolio_data.get_portfolio_nav()
    if verbose:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)

        figs = qis.generate_strategy_factsheet(portfolio_data=portfolio_data,
                                               benchmark_prices=futures_prices['ES1'],
                                               time_period=TIME_PERIOD,
                                               add_current_position_var_risk_sheet=True,
                                               **qis.fetch_default_report_kwargs(time_period=TIME_PERIOD))
        qis.save_figs_to_pdf(figs=figs,
                             file_name=f"{RiskFactors.INFLATION.value}_portfolio",
                             local_path=lp.get_output_path())

    return portfolio_data.get_portfolio_nav()


def load_base_futures_prices() -> pd.DataFrame:
    """
    Load risk prices data. Data is generated only once and cached for subsequent calls.
    Returns the same DataFrame instance on every call after the first.
    """
    if not hasattr(load_base_futures_prices, '_cache'):
        load_base_futures_prices._cache = qis.load_df_from_csv(file_name='futures_prices',
                                                               local_path=lp.get_resource_path()).loc['31Dec1999': ]
    return load_base_futures_prices._cache


def load_mac_prices() -> Tuple[pd.DataFrame, pd.DataFrame]:
    local_path = lp.get_resource_path()
    prices = qis.load_df_from_excel(file_name="mac_prices", sheet_name="prices", local_path=local_path)
    prices_unsmoothed = qis.load_df_from_excel(file_name="mac_prices", sheet_name="prices_unsmoothed", local_path=local_path)
    return prices, prices_unsmoothed


def load_rates() -> pd.Series:
    rate = qis.load_df_from_csv(file_name="rate", local_path=lp.get_resource_path())
    return rate.iloc[:, 0]


def compute_risk_factor_portfolio(prices: pd.DataFrame,
                                  strategic_weights: np.ndarray,
                                  rebalancing_freq: str = 'QE',
                                  portfolio_vol_target: float = 0.15,
                                  vol_span: int = 3*52,
                                  is_portfolio_vol_target: bool = True,
                                  ticker: str = 'factor'
                                  ) -> qis.PortfolioData:
    if is_portfolio_vol_target:
        risk_weights = compute_volatility_targeted_portfolio(prices=prices,
                                                             strategic_weights=strategic_weights,
                                                             rebalancing_freq=rebalancing_freq,
                                                             portfolio_vol_target=portfolio_vol_target,
                                                             vol_span=vol_span)
    else:
        risk_weights = strategic_weights
    portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                  weights=risk_weights,
                                                  ticker=ticker,
                                                  rebalancing_freq=rebalancing_freq)
    return portfolio_data


def compute_volatility_targeted_portfolio(prices: pd.DataFrame,
                                          strategic_weights: np.ndarray,
                                          returns_freq: str = 'W-WED',
                                          vol_span: int = 3*52,
                                          portfolio_vol_target: float = 0.15,
                                          rebalancing_freq: str = 'ME'
                                          ) -> pd.DataFrame:
    returns = qis.to_returns(prices=prices, freq=returns_freq, is_log_returns=True)
    strategic_weights = pd.DataFrame(qis.np_array_to_df_index(strategic_weights, n_index=len(returns.index)),
                                     index=returns.index, columns=returns.columns)
    portfolio_vol = qis.compute_portfolio_vol(returns=returns,
                                              weights=strategic_weights,
                                              span=vol_span,
                                              annualize=True)
    instrument_portfolio_leverages = portfolio_vol_target * qis.to_finite_reciprocal(data=portfolio_vol)
    risk_weights = strategic_weights.multiply(instrument_portfolio_leverages, axis=0)
    risk_weights = risk_weights.resample(rebalancing_freq).last()
    return risk_weights


def compute_benchmarks_beta_attribution_from_returns(portfolio_returns: pd.Series,
                                                    benchmark_returns: pd.DataFrame,
                                                    portfolio_benchmark_betas: pd.DataFrame,
                                                    residual_name: str = 'Alpha',
                                                    time_period: TimePeriod = None
                                                    ) -> pd.DataFrame:
    # to be replaced with qis
    if isinstance(benchmark_returns, pd.Series):
        benchmark_returns = benchmark_returns.to_frame()
    benchmark_returns = benchmark_returns.reindex(index=portfolio_returns.index)
    x_attribution = (portfolio_benchmark_betas.shift(1)).multiply(benchmark_returns)
    total_attrib = x_attribution.sum(axis=1)
    residual = np.subtract(portfolio_returns, total_attrib)
    joint_attrib = pd.concat([x_attribution, residual.rename(residual_name)], axis=1)
    if time_period is not None:
        joint_attrib = time_period.locate(joint_attrib)
        joint_attrib.iloc[0, :] = 0.0
    return joint_attrib


def compute_excess_return_navs(prices: Union[pd.Series, pd.DataFrame],
                               rates_data: pd.Series,
                               first_date: pd.Timestamp = None
                               ) -> Union[pd.Series, pd.DataFrame]:
    # to be replaced with qis
    returns = qis.to_returns(prices=prices, is_first_zero=True)
    excess_returns = qis.compute_excess_returns(returns=returns, rates_data=rates_data)
    navs = qis.returns_to_nav(returns=excess_returns, first_date=first_date)
    return navs


@qis.timer
def compute_risk_factors(is_portfolio_vol_target: bool = True,
                         rebalancing_freq: str = 'ME',
                         portfolio_vol_target: float = 0.15,
                         vol_span: int = 3*52,
                         verbose: bool = True
                         ) -> pd.DataFrame:
    futures_prices = load_base_futures_prices()
    kwargs = dict(is_portfolio_vol_target=is_portfolio_vol_target,
                  rebalancing_freq=rebalancing_freq,
                  portfolio_vol_target=portfolio_vol_target,
                  vol_span=vol_span,
                  verbose=verbose)
    risk_factors = pd.concat([compute_equity_factor(futures_prices=futures_prices, **kwargs),
                              compute_bond_factor(futures_prices=futures_prices, **kwargs),
                              compute_credit_factor(futures_prices=futures_prices, **kwargs),
                              compute_pe_premia_factor(futures_prices=futures_prices, **kwargs),
                              compute_carry_premia_factor(futures_prices=futures_prices, **kwargs),
                              compute_inflation_premia_factor(futures_prices=futures_prices, **kwargs)
                              ], axis=1)
    return risk_factors


class LocalTests(Enum):
    GENERATE_BBG_PRICES = 1
    MAC_PRICES = 2
    LIQUIDITY_PREMIA = 3
    FACTOR_PRICES = 4


def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """

    # print(futures_prices)
    if local_test == LocalTests.GENERATE_BBG_PRICES:
        from bbg_fetch import fetch_field_timeseries_per_tickers

        # 1. generate rates data
        rate = fetch_field_timeseries_per_tickers(tickers={'USGG3M Index': '3m_rate'}, freq='B').ffill().iloc[:, 0] / 100.0

        # SPW is LWE1 Index
        tickers = {# equity indices
                   'SPW Index': 'SPW',  # ew s&p500
                   'NDDUWI Index': 'NDDUWI',
                   'RTY Index': 'RTY',
                   # equity futures
                   'ES1 Index': 'ES1',
                   'NQ1 Index': 'NQ1',
                   'ZWP1 Index': 'ZWP1',  # NDDUWI # need backfill
                   'LWE1 Index': 'LWE1',  # ew s&p500 # need backfill
                   'RTY1 Index': 'RTY1',
                   # bond futures
                   'TY1 Comdty': 'TY1',
                   'RX1 Comdty': 'RX1',
                   'G 1 Comdty': 'G1',
                   'JB1 Comdty': 'JB1',
                   'CN1 Comdty': 'CN1',
                   'XM1 Comdty': 'XM1',
                   # rates
                   'SFR1 Comdty': 'SFR1',
                   'ED5 Comdty': 'ED1',
                   'FF1 Comdty': 'FF1',
                   # credit trackers
                   'LBUSTRUU Index': 'IG cash',
                   'LF98TRUU Index': 'HY cash',
                   'UISYMI5S Index': 'IG',  # ubs shortable
                   'UISYMH5S Index': 'CDX',  # ubs shortable
                   # fx
                   'JY1 Curncy': 'JPY',
                   'AD1 Curncy': 'AUD',
                    'NV1 Curncy': 'NZD',
                   # commodities
                   'GC1 Comdty': 'GLD',
                   'CRY Index': 'CRY',
                   'BCOM Index': 'BCOM',
                    # inflaion
                    #'IBXXUBF1 Index': 'I10Y',
                    'BUINTRUU Index': 'B10Y',
                    'DBBNU05Y Index': 'DB5Y',
                   }
        prices = fetch_field_timeseries_per_tickers(tickers=tickers, freq='B').ffill()

        # backfill SPW
        prices['SPW'] = qis.bfill_timeseries(df_newer=prices['LWE1'].loc['2024':],
                                              df_older=compute_excess_return_navs(prices=prices['SPW'], rates_data=rate),
                                              is_prices=True)

        # backfill NDDUWI
        prices['NDDUWI'] = qis.bfill_timeseries(df_newer=prices['ZWP1'],
                                              df_older=compute_excess_return_navs(prices=prices['NDDUWI'], rates_data=rate),
                                              is_prices=True)
        # backfill rty
        prices['RTY'] = qis.bfill_timeseries(df_newer=prices['RTY1'],
                                              df_older=compute_excess_return_navs(prices=prices['RTY'], rates_data=rate),
                                              is_prices=True)
        # backfill sofr
        prices['SFR1'] = qis.bfill_timeseries(df_newer=prices['SFR1'], df_older=prices['ED1'], is_prices=True)

        # backfill IG
        prices['IG'] = qis.bfill_timeseries(df_newer=prices['IG'],
                                              df_older=compute_excess_return_navs(prices=prices['IG cash'], rates_data=rate),
                                              is_prices=True)

        # backfill CDX
        prices['CDX'] = qis.bfill_timeseries(df_newer=prices['CDX'],
                                              df_older=compute_excess_return_navs(prices=prices['HY cash'], rates_data=rate),
                                              is_prices=True)

        # inflaion
        prices['I10Y'] = qis.bfill_timeseries(df_newer=prices['DB5Y'],
                                              df_older=compute_excess_return_navs(prices=prices['B10Y'], rates_data=rate),
                                              is_prices=True)
        prices = prices.drop(['ED1', 'LWE1', 'ZWP1', 'RTY1', 'IG cash', 'HY cash', 'B10Y'], axis=1)

        # backfill cdx and ig
        #prices['CDX'] = prices['CDX'].ffill().bfill()
        #prices['IG'] = prices['IG'].ffill().bfill()

        qis.plot_prices_with_dd(prices.loc['31Dec1999':, :], framealpha=0.9)

        qis.save_df_to_csv(df=prices, file_name='futures_prices', local_path=lp.get_resource_path())
        qis.save_df_to_csv(df=rate.to_frame(), file_name='rate', local_path=lp.get_resource_path())

    elif local_test == LocalTests.MAC_PRICES:
        prices, prices_unsmoothed = load_mac_prices()
        print(prices)
        print(prices.columns)

    elif local_test == LocalTests.LIQUIDITY_PREMIA:
        # get_pe_performance()
        futures_prices = load_base_futures_prices()
        compute_carry_premia_factor(futures_prices=futures_prices, verbose=True)

    elif local_test == LocalTests.FACTOR_PRICES:
        factors = compute_risk_factors()
        print(factors)
        fig = qis.generate_multi_asset_factsheet(prices=factors,
                                                 benchmark='Equity',
                                                 time_period=TIME_PERIOD,
                                                 **qis.fetch_default_report_kwargs(time_period=TIME_PERIOD, add_rates_data=False))
        qis.save_figs_to_pdf(figs=[fig],
                             file_name=f"risk_factors",
                             local_path=lp.get_output_path())
        qis.save_df_to_csv(df=factors, file_name='futures_risk_factors', local_path=lp.get_resource_path())

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.FACTOR_PRICES)

"""
IBXXUBF1 Index: INFU LN Equity
USGGBE05 Index: 5y rate
DBCUU05Y Index: db ask for access
BUINTRUU Index: bbg 10YR plus TIP Index: 
short UXYU5 COMB Comdty
"""