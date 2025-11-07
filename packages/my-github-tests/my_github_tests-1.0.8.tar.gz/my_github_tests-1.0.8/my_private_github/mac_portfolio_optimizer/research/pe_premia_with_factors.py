import pandas as pd
import numpy as np
import qis as qis
import seaborn as sns
from matplotlib import pyplot as plt
from typing import Optional, Union
from enum import Enum
from optimalportfolios import compute_ar1_unsmoothed_prices
import mac_portfolio_optimizer.local_path as lp
from mac_portfolio_optimizer.mac_prod.futures_risk_model import (load_mac_prices,
                                                                 load_base_futures_prices,
                                                                 load_rates,
                                                                 compute_pe_premia_factor,
                                                                 compute_benchmarks_beta_attribution_from_returns)
from mac_portfolio_optimizer import (load_mac_portfolio_universe, SaaPortfolio, TaaPortfolio)


def compute_pe_excess_performance(pe_price: pd.Series) -> pd.Series:
    """
    compute excess performance of
    """
    pe_unsmoothed, unsmoothed_returns, betas, ewm_r2 = compute_ar1_unsmoothed_prices(prices=pe_price.to_frame(),
                                                                                     freq='QE',
                                                                                     span=20,
                                                                                     max_value_for_beta=None)
    # excess_returns = qis.compute_excess_returns(returns=unsmoothed_returns.iloc[:, 0], rates_data = load_rates())
    excess_returns = unsmoothed_returns.iloc[:, 0]
    return excess_returns


def plot_pe_performance(pe_price: pd.Series,
                        benchmark_price: pd.Series,
                        time_period: qis.TimePeriod,
                        unsmooth_span: int = 20
                        ) -> plt.Figure:
    pe_unsmoothed, unsmoothed_returns, betas, ewm_r2 = compute_ar1_unsmoothed_prices(prices=pe_price.to_frame(),
                                                                                     freq='QE',
                                                                                     span=unsmooth_span,
                                                                                     max_value_for_beta=None)
    pe_prices = pd.concat([pe_price.rename('reported'), pe_unsmoothed.iloc[:, 0].rename('unsmoothed')], axis=1)
    prices = pd.concat([pe_prices, benchmark_price], axis=1)

    with sns.axes_style('darkgrid'):
        kwargs = dict(framealpha=0.9)
        fig, axs = plt.subplots(2, 2, figsize=(14, 12), constrained_layout=True)

        qis.plot_prices_with_dd(prices=prices, perf_params=qis.PerfParams(freq='QE'),
                                title='(A) Performances',
                                dd_title='(C) Running Drawdowns',
                                axs=axs[:, 0],
                                **kwargs)

        # 2-betas
        linear_model = qis.estimate_ewm_factor_model(asset_prices=pe_prices, factor_prices=benchmark_price, freq='QE', span=12,
                                                     mean_adj_type=qis.MeanAdjType.EWMA)
        betas = linear_model.get_factor1_loadings()
        qis.plot_time_series(df=time_period.locate(betas),
                             var_format='{:,.2f}',
                             title='(B) EWMA Equity Betas',
                             ax=axs[0, 1],
                             **kwargs)

        # vol
        vols = qis.compute_ewm_vol(data=qis.to_returns(prices, is_log_returns=True, drop_first=True), span=12,
                                   annualization_factor=4.0)
        qis.plot_time_series(df=time_period.locate(vols),
                             var_format='{:,.1%}',
                             title='(D) EWMA Volatilities',
                             ax=axs[1, 1],
                             **kwargs)
    return fig


def analyse_pe_equity(pe_price: pd.Series,
                      time_period: qis.TimePeriod = None
                      ) -> plt.Figure:
    pe_excess_returns = compute_pe_excess_performance(pe_price=pe_price)
    futures_prices = load_base_futures_prices()
    # compute pe premia
    pe_premia_nav = compute_pe_premia_factor(futures_prices=futures_prices, portfolio_vol_target=0.15, rebalancing_freq='QE')

    # compute pe excluding returns
    equity_returns = futures_prices['ES1'].reindex(index=pe_excess_returns.index).ffill().pct_change()
    pe_ex_equity = pe_excess_returns.subtract(equity_returns)

    # compute y = beta*pe_excess_returns
    x = pe_premia_nav.rename('PE factor premia')
    x = qis.to_returns(prices=x, freq='QE', is_log_returns=True).reindex(index=pe_ex_equity.index)
    ewm_linear_model = qis.EwmLinearModel(x=x, y=pe_excess_returns) #np.log(1.0+pe_excess_returns))
    ewm_linear_model.fit(span=40, is_x_correlated=False, mean_adj_type=qis.MeanAdjType.EWMA)

    betas = ewm_linear_model.get_asset_factor_betas()
    betas[x.name] = 0.5 + 0.5*betas[x.name]
    joint_attrib = compute_benchmarks_beta_attribution_from_returns(portfolio_returns=pe_ex_equity,
                                                                    benchmark_returns=x,
                                                                    portfolio_benchmark_betas=betas,
                                                                    residual_name='residual',
                                                                    time_period=time_period)

    with sns.axes_style("darkgrid"):
        kwargs = dict(framealpha=0.9)

        fig, axs = plt.subplots(3, 1, figsize=(14, 12), tight_layout=True)
        returns = pd.concat([#pe_excess_returns.rename('PE excess return'),
                             pe_ex_equity.rename('PE ex-equity'),
                             x.rename('PE factor premia')
                             ], axis=1)
        returns = time_period.locate(returns)
        prices = qis.returns_to_nav(returns=returns)

        qis.plot_prices(prices=prices,
                        perf_params=qis.PerfParams(freq='QE'),
                        title='(A) Performances',
                        ax=axs[0],
                        **kwargs)

        qis.plot_time_series(df=time_period.locate(betas).iloc[:, 0].rename('beta'),
                             var_format='{:,.2f}',
                             legend_stats=qis.LegendStats.AVG_NONNAN_LAST,
                             title=f"(B) PE ex-equity beta to PE factor premia",
                             ax=axs[1])

        qis.plot_time_series(df=joint_attrib.cumsum(0),
                             var_format='{:,.0%}',
                             legend_stats=qis.LegendStats.LAST_NONNAN,
                             title=f"(C) Total return attribution",
                             ax=axs[2])
        axs[0].set_xticklabels('')
        axs[1].set_xticklabels('')
    return fig


class LocalTests(Enum):
    PLOT_AR1_BETAS = 1
    PE_PERFORMANCE = 2
    PE_PREMIA = 3


def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """

    import mac_portfolio_optimizer.local_path as lp
    local_path = f"{lp.get_resource_path()}"
    local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//Figures//"
    # local_path_out = lp.get_output_path()

    universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                taa_portfolio=SaaPortfolio.SAA_INDEX_PAPER)

    prices = universe_data.get_joint_prices()
    print(prices.columns)

    pe_price = prices['Private Equity'].asfreq('QE').dropna()
    # pe_price = prices['Private Debt'].asfreq('QE').dropna()
    benchmark_price = prices['Equity'].asfreq('QE').dropna().rename('MSCI Equity')
    # benchmark_price = prices['Government Bonds'].asfreq('QE').dropna().rename('Bonds')

    print(pe_price)

    time_period = qis.TimePeriod('31Dec2004', '31Mar2025')

    if local_test == LocalTests.PLOT_AR1_BETAS:
        pe_prices = prices[['Private Equity', 'Private Debt']].asfreq('QE').dropna()
        pe_unsmoothed, unsmoothed, betas, ewm_r2 = compute_ar1_unsmoothed_prices(prices=pe_prices,
                                                                                 freq='QE',
                                                                                 span=20,
                                                                                 max_value_for_beta=None)
        betas = time_period.locate(betas)
        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            kwargs = dict(framealpha=0.9, font_size=12)
            qis.plot_time_series(df=betas,
                                 title='AR-1 betas',
                                 ax=ax,
                                 **kwargs)
        qis.save_fig(fig=fig, file_name='ar1_betas', local_path=local_path_out)

    elif local_test == LocalTests.PE_PERFORMANCE:
        fig = plot_pe_performance(pe_price=pe_price, benchmark_price=benchmark_price,
                            time_period=time_period)
        qis.save_fig(fig=fig, file_name='pe_performance', local_path=local_path_out)


    elif local_test == LocalTests.PE_PREMIA:
        fig = analyse_pe_equity(pe_price=pe_price, time_period=time_period)
        # qis.save_fig(fig=fig, file_name='pe_analysis', local_path=local_path_out)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.PE_PREMIA)
