"""
analysis of PE inclusion
"""
# packages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import qis as qis
from qis import PerfStat
from enum import Enum
from typing import Tuple, Dict
from optimalportfolios import  rolling_maximize_cara_mixture, compute_ar1_unsmoothed_prices
import optimalportfolios.utils.gaussian_mixture as gm

# project
import mac_portfolio_optimizer.local_path as lp
from mac_portfolio_optimizer import (get_prod_covar_estimator,
                                     load_mac_portfolio_universe,
                                     SaaPortfolio,
                                     TaaPortfolio,
                                     backtest_saa_risk_budget_portfolio,
                                     backtest_saa_maximum_diversification_portfolio,
                                     RiskModel,
                                     UniverseColumns,
                                     MAC_ASSET_CLASS_LOADINGS_COLUMNS)
from mac_portfolio_optimizer.mac_prod.futures_risk_model import (load_mac_prices,
                                                                 load_base_futures_prices,
                                                                 load_rates,
                                                                 compute_pe_premia_factor,
                                                                 compute_benchmarks_beta_attribution_from_returns)


def plot_mixures(prices: pd.DataFrame,
                 time_period: qis.TimePeriod,
                 freq: str = 'QE',
                 n_components: int = 3,
                 idx: int = None
                 ) -> Tuple[plt.Figure, plt.Figure]:
    rets = qis.to_returns(prices=prices, is_log_returns=True, drop_first=True, freq=freq)

    kwargs = dict(fontsize=12, digits_to_show=1, sharpe_digits=2)
    asset = prices.columns[idx]
    print(rets)
    with sns.axes_style('white'):
        fig1, ax = plt.subplots(1, 1, figsize=(15, 5), constrained_layout=True)
        params = gm.fit_gaussian_mixture(x=time_period.locate(rets).to_numpy(),
                                         n_components=n_components,
                                         idx=None)
        print(params)
        params_df = params.get_params(idx=idx)

        gm.plot_mixure2(x=time_period.locate(rets).to_numpy(),
                        n_components=n_components,
                        columns=prices.columns,
                        title=f"Returns and ellipsoids of Gaussian clusters for period {time_period.to_str()}",
                        idx=None,
                        x_column='North America',
                        y_column='Private Equity',
                        ax=ax,
                        **kwargs)

        fig2, ax = plt.subplots(1, 1, figsize=(15, 1.5), constrained_layout=True)
        df = qis.df_to_str(params_df, var_format='{:.0%}')
        qis.plot_df_table(df=df,
                          add_index_as_column=True,
                          index_column_name='Cluster',
                          ax=ax,
                          # heatmap_columns=[2],
                          title=f"Cluster parameters for {asset}: {time_period.to_str()}",
                          **kwargs)
        return fig1, fig2


def compute_pe_replica():
    # compute pe premia
    from bbg_fetch import fetch_field_timeseries_per_tickers
    futures_prices = load_base_futures_prices()
    pe_premia_nav = compute_pe_premia_factor(futures_prices=futures_prices, portfolio_vol_target=0.1,
                                             rebalancing_freq='YE').rename('PE premia')
    eq_prices = fetch_field_timeseries_per_tickers(tickers={'NDDUWI Index': 'NDDUWI'}, freq='B',
                                                   field='PX_LAST').ffill()
    joint_returns = qis.to_returns(pd.concat([pe_premia_nav, eq_prices], axis=1), freq='W-WED')
    replica = qis.returns_to_nav(joint_returns.sum(axis=1)).rename('PE replica')
    return eq_prices, pe_premia_nav, replica


def plot_annual_tables(price: pd.Series,
                       perf_params: qis.PerfParams,
                       date_format: str = '%b%Y'
                       ) -> plt.Figure:

    kwargs = dict(fontsize=9, date_format=date_format, cmap='YlGn')
    dfs_out = {}
    with sns.axes_style("white"):
        fig, axs = plt.subplots(2, 1, figsize=(14, 6))
        qis.plot_ra_perf_annual_matrix(price=price,
                                       perf_column=PerfStat.SHARPE_RF0,
                                       perf_params=perf_params,
                                       ax=axs[0],
                                       title='(A) Sharpe Ratio',
                                       is_fig_out=True,
                                       **kwargs)

        qis.plot_ra_perf_annual_matrix(price=price,
                                       perf_column=PerfStat.SKEWNESS,
                                       perf_params=perf_params,
                                       title='(B) Skewness of quarterly returns',
                                       ax=axs[1],
                                       is_fig_out=True,
                                       **kwargs)

    return fig

class LocalTests(Enum):
    CONSTRAINTS = 1
    MAX_CARRA = 2
    PLOT_MIXURE = 3
    PE_PERFORMANCE = 4
    PE_REPLICA_JOINT = 5
    MSCI_PE_RETURNS = 6
    PE_REPLICA_JOINT_EXTENDED = 7
    SKEW = 8


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.
    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # time_period = qis.TimePeriod('31Dec2004', '31Aug2025')
    time_period = qis.TimePeriod('31Dec2004', '30Sep2025')
    rebalancing_freq = 'YE'
    local_path = f"{lp.get_resource_path()}"
    local_path_out = lp.get_output_path()
    # local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//New Figures//"

    # load universe
    universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                sub_asset_class_ranges_sheet_name=None,
                                                risk_model=RiskModel.FUTURES_RISK_FACTORS,
                                                sub_asset_class_columns=MAC_ASSET_CLASS_LOADINGS_COLUMNS)
    # set model params
    apply_unsmoothing_for_pe = True
    covar_estimator = get_prod_covar_estimator(rebalancing_freq=rebalancing_freq,
                                               apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                               returns_freqs=universe_data.get_joint_rebalancing_freqs(),
                                               nonneg=False)

    # set report kwargs
    report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                    reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                    add_rates_data=False)
    report_kwargs = qis.update_kwargs(report_kwargs, dict(ytd_attribution_time_period=qis.TimePeriod('30Jun2024', '31Aug2025')))

    management_fee = 0.02
    meta_params = dict(management_fee=management_fee, saa_rebalancing_freq=rebalancing_freq)

    saa_constraints = universe_data.get_saa_constraints(drop_min_ac_constraints=False)

    analysis_type = 1
    if analysis_type == 0:
        file_name = 'saa_min_constraint'
        ticker_rb = 'Risk-Budget'
        ticker_md = 'MaximumDiver'

    elif analysis_type == 1:
        file_name = 'saa_min_unconstraint'
        ticker_rb = 'Risk-Budget'
        ticker_md = 'MaximumDiver'
        saa_constraints.min_weights = pd.Series(0.0, index=saa_constraints.min_weights.index)
        saa_constraints.max_weights = pd.Series(1.0, index=saa_constraints.max_weights.index)

    elif analysis_type == 2:
        file_name = 'saa_no_pe_pd'
        ticker_rb = 'Risk-Budget'
        ticker_md = 'MaximumDiver'

        saa_constraints = universe_data.get_saa_constraints(drop_min_ac_constraints=True)
        saa_constraints.group_lower_upper_constraints.group_max_allocation['Equity'] = 0.65
        risk_budget = pd.Series({
            'Global IG Bonds': 0.0050,
            'Government Bonds': 0.0025,
            'Global HY Bonds': 0.0100,
            'EM Bonds': 0.0100,
            'Other Fixed Income': 0.0100,
            'North America': 0.3823,
            'Europe': 0.1726,
            'Japan': 0.1726,
            'Asia Ex-Japan': 0.1233,
            'EM ex-Asia': 0.0617,
            'Hedge Funds': 0.0300,
            'Private Equity': 0.0000,
            'Private Debt': 0.0000,
            'Commodities EX-Precious': 0.0025,
            'Commodities Precious': 0.0050,
            'REITs': 0.0025,
            'Insurance-Linked': 0.0100
        })
        saa_constraints.min_weights.loc['Private Equity'] = 0.0
        saa_constraints.min_weights.loc['Private Debt'] = 0.0
        saa_constraints.max_weights.loc['Private Equity'] = 0.0
        saa_constraints.max_weights.loc['Private Debt'] = 0.0
        universe_data.saa_universe_df[UniverseColumns.RISK_BUDGET.value] = risk_budget

    else:
        raise NotImplementedError

    if local_test in [LocalTests.CONSTRAINTS, LocalTests.MAX_CARRA]:
        rolling_covar_data = covar_estimator.fit_rolling_covars(
            prices=universe_data.get_saa_prices(apply_unsmoothing_for_pe=apply_unsmoothing_for_pe),
            risk_factor_prices=universe_data.get_risk_factors(),
            time_period=time_period)
        saa_taa_covar = rolling_covar_data.y_covars

    if local_test == LocalTests.CONSTRAINTS:

        saa_rolling_weights_md, saa_portfolio_data_md = backtest_saa_maximum_diversification_portfolio(universe_data=universe_data,
                                                                                                       time_period=time_period,
                                                                                                       saa_taa_covar=saa_taa_covar,
                                                                                                       saa_constraints=saa_constraints,
                                                                                                       **meta_params)

        saa_rolling_weights_rb, saa_portfolio_data_rb = backtest_saa_risk_budget_portfolio(universe_data=universe_data,
                                                                                           time_period=time_period,
                                                                                           saa_taa_covar=saa_taa_covar,
                                                                                           saa_constraints=saa_constraints,
                                                                                           **meta_params)

        multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[saa_portfolio_data_rb.set_ticker(ticker=ticker_rb),
                                                                       saa_portfolio_data_md.set_ticker(ticker=ticker_md)],
                                                      benchmark_prices=universe_data.benchmarks,
                                                      covar_dict=saa_taa_covar)
        group_data, group_order = universe_data.get_joint_sub_ac_group_data()
        [x.set_group_data(group_data=group_data, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]

        figs1 = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                              strategy_idx=0,
                                                              benchmark_idx=1,
                                                              add_benchmarks_to_navs=True,
                                                              add_exposures_comp=False,
                                                              add_strategy_factsheet=False,
                                                              time_period=time_period,
                                                              **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name=file_name, local_path=local_path_out)
        plt.close('all')

    elif local_test == LocalTests.MAX_CARRA:
        time_period = qis.TimePeriod('31Dec2009', '30Sep2025')
        weights = rolling_maximize_cara_mixture(prices=universe_data.get_saa_prices(apply_unsmoothing_for_pe=True),
                                                constraints=saa_constraints,
                                                time_period=time_period,
                                                rebalancing_freq=rebalancing_freq,
                                                returns_freq='QE',
                                                roll_window=10)
        print(weights)
        saa_portfolio_data_mc = qis.backtest_model_portfolio(prices=universe_data.get_saa_prices(),
                                                          weights=weights,
                                                          management_fee=management_fee,
                                                          ticker='MaxCarra3')
        saa_rolling_weights_rb, saa_portfolio_data_rb = backtest_saa_risk_budget_portfolio(universe_data=universe_data,
                                                                                           time_period=time_period,
                                                                                           saa_taa_covar=saa_taa_covar,
                                                                                           saa_constraints=saa_constraints,
                                                                                           **meta_params)
        multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[saa_portfolio_data_rb.set_ticker(ticker=ticker_rb),
                                                                       saa_portfolio_data_mc],
                                                      benchmark_prices=universe_data.benchmarks,
                                                      covar_dict=saa_taa_covar)
        group_data, group_order = universe_data.get_joint_sub_ac_group_data()
        [x.set_group_data(group_data=group_data, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]

        figs1 = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                              strategy_idx=0,
                                                              benchmark_idx=1,
                                                              add_benchmarks_to_navs=True,
                                                              add_exposures_comp=False,
                                                              add_strategy_factsheet=False,
                                                              time_period=time_period,
                                                              **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name=file_name, local_path=local_path_out)
        plt.close('all')

    elif local_test == LocalTests.PLOT_MIXURE:
        prices = universe_data.get_saa_prices(apply_unsmoothing_for_pe=True)
        asset_classes = [
            "Private Equity",
            "Private Debt",
            "Global IG Bonds",
            "Government Bonds",
            "Global HY Bonds",
            "EM Bonds",
            "Other Fixed Income",
            "North America",
            "Europe",
            "Japan",
            "Asia Ex-Japan",
            "EM ex-Asia",
            "Hedge Funds",
            "Commodities EX-Precious",
            "Commodities Precious",
            "REITs",
            "Insurance-Linked"
        ]
        prices = prices[asset_classes]
        # time_period = qis.TimePeriod('30Sep2015', '30Sep2025')
        time_period = qis.TimePeriod('30Sep2005', '30Sep2025')
        fig1, fig2 = plot_mixures(prices=prices, time_period=time_period, freq='QE', n_components=3, idx=1)

        plt.show()

    elif local_test == LocalTests.PE_PERFORMANCE:

        prices0 = universe_data.get_saa_prices(apply_unsmoothing_for_pe=False)
        pe_reported = prices0[["Private Equity", "Private Debt"]].rename({"Private Equity": 'PE reported', "Private Debt": 'PD reported'}, axis=1)
        benchmark_price = prices0["North America"].rename("S&P500")

        prices1 = universe_data.get_saa_prices(apply_unsmoothing_for_pe=True)
        pe_unsmoothed = prices1[["Private Equity", "Private Debt"]].rename({"Private Equity": 'PE unsmoothed', "Private Debt": 'PD unsmoothed'}, axis=1)

        prices = pd.concat([pe_reported.iloc[:, 0], pe_unsmoothed.iloc[:, 0],
                             pe_reported.iloc[:, 1], pe_unsmoothed.iloc[:, 1]], axis=1)

        perf_columns = [PerfStat.PA_RETURN,
                        PerfStat.VOL,
                        PerfStat.SHARPE_RF0,
                        PerfStat.MAX_DD,
                        PerfStat.SKEWNESS,
                        PerfStat.KURTOSIS,
                        PerfStat.ALPHA_AN,
                        PerfStat.BETA,
                        PerfStat.R2,
                        PerfStat.ALPHA_PVALUE]

        prices = prices.loc['31Dec2004':, :]
        qis.plot_ra_perf_table_benchmark(prices=prices, benchmark_price=benchmark_price,
                                         perf_params=qis.PerfParams(freq='QE', alpha_an_factor=4),
                                         perf_columns=perf_columns)
        df = qis.to_returns(prices=pd.concat([benchmark_price,prices], axis=1).dropna(), freq='QE')
        with sns.axes_style("darkgrid"):
            qis.plot_histogram(df, legend_stats=qis.LegendStats.AVG_STD,
                               xvar_format='{:.1%}',
                               title='QUarterly returns',
                               add_data_std_pdf=True)

    elif local_test == LocalTests.PE_REPLICA_JOINT:

        from bbg_fetch import fetch_field_timeseries_per_tickers
        eq_prices, pe_premia_nav, replica = compute_pe_replica()
        prices = pd.concat([eq_prices, pe_premia_nav.rename('PE premia'), replica], axis=1).ffill()

        time_period = qis.TimePeriod('31Dec2009', '30Sep2023')
        prices = time_period.locate(prices)
        # get
        tickers = {'PGGLVRU LX Equity': 'Partners Group'}
        pe_fund_prices = fetch_field_timeseries_per_tickers(tickers=tickers, freq='B', field='PX_LAST').ffill()
        prices0 = universe_data.get_saa_prices(apply_unsmoothing_for_pe=False)
        benchmark_prices = prices0["North America"].rename("S&P500")
        msci_pe = prices0['Private Equity'].rename('MSCI PE')

        # get het navs
        navs = qis.load_df_from_excel(file_name='LGPE_track_record_-_Q3_2023__non-US_', sheet_name='perf', local_path=local_path)
        #qis.plot_prices(navs)
        returns = qis.to_returns(navs) - 0.042 / 4.0
        net_navs = qis.returns_to_nav(returns)

        reported_prices = pd.concat([msci_pe, net_navs, pe_fund_prices], axis=1)

        net_navs_unsmoothed, _, _, _ = compute_ar1_unsmoothed_prices(prices=reported_prices, freq='QE', span=20)
        net_navs_unsmoothed = pd.concat([net_navs_unsmoothed, pe_premia_nav.rename('PE premia'), replica], axis=1)
        net_navs_unsmoothed = net_navs_unsmoothed.asfreq('B').ffill()
        kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                 reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                 add_rates_data=False,
                                                 override=dict(digits_to_show=1))
        qis.plot_prices_with_dd(prices, **kwargs)
        qis.plot_returns_corr_table(prices, freq='QE')


        fig = qis.generate_multi_asset_factsheet(prices=net_navs_unsmoothed,
                                                 benchmark_prices=benchmark_prices,
                                                 time_period=time_period,
                                                 **kwargs)
        qis.save_figs_to_pdf(figs=[fig], file_name=f"pe_report", local_path=local_path_out)

    elif local_test == LocalTests.MSCI_PE_RETURNS:
        from bbg_fetch import fetch_field_timeseries_per_tickers
        prices0 = universe_data.get_saa_prices(apply_unsmoothing_for_pe=False)
        msci_pe = prices0['Private Equity'].rename('MSCI PE')
        tickers = {'LGTPREB LE Equity': 'LGTPREB'}
        pe_fund_prices = fetch_field_timeseries_per_tickers(tickers=tickers, freq='B', field='PX_LAST').ffill()
        prices = pd.concat([msci_pe, pe_fund_prices], axis=1)
        returns = qis.to_returns(prices, freq='QE')
        navs = qis.load_df_from_excel(file_name='LGPE_track_record_-_Q3_2023__non-US_', sheet_name='perf', local_path=local_path)
        #qis.plot_prices(navs)
        pro_returns = qis.to_returns(navs) - 0.042 / 4.0
        returns = pd.concat([pro_returns, returns], axis=1)
        returns.to_clipboard()

    elif local_test == LocalTests.PE_REPLICA_JOINT_EXTENDED:
        from bbg_fetch import fetch_field_timeseries_per_tickers
        eq_prices, pe_premia_nav, replica = compute_pe_replica()

        time_period = qis.TimePeriod('31Dec2000', '30Sep2025')
        prices0 = universe_data.get_saa_prices(apply_unsmoothing_for_pe=False)
        benchmark_prices = prices0["North America"].rename("S&P500")

        # get het navs
        returns = qis.load_df_from_excel(file_name='LGPE_track_record_-_Q3_2023__non-US_', sheet_name='perf_bf', local_path=local_path)
        returns = returns[['LGPE BF', 'MSCI PE']]
        reported_prices = qis.returns_to_nav(returns)

        net_navs_unsmoothed, _, _, _ = compute_ar1_unsmoothed_prices(prices=reported_prices, freq='QE', span=20)
        net_navs_unsmoothed = pd.concat([net_navs_unsmoothed, pe_premia_nav, replica], axis=1)
        net_navs_unsmoothed = net_navs_unsmoothed.asfreq('B').ffill()
        kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                 reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                 add_rates_data=False,
                                                 override=dict(digits_to_show=1))

        fig = qis.generate_multi_asset_factsheet(prices=net_navs_unsmoothed,
                                                 benchmark_prices=benchmark_prices,
                                                 time_period=time_period,
                                                 **kwargs)
        qis.save_figs_to_pdf(figs=[fig], file_name=f"lgpe_report", local_path=local_path_out)

    elif local_test == LocalTests.SKEW:
        assets = ['LGPE BF', 'MSCI PE']
        returns0 = qis.load_df_from_excel(file_name='LGPE_track_record_-_Q3_2023__non-US_', sheet_name='perf_bf', local_path=local_path)
        for asset in assets:
            returns = returns0[asset].dropna()
            reported_prices = qis.returns_to_nav(returns)
            net_navs_unsmoothed, _, _, _ = compute_ar1_unsmoothed_prices(prices=reported_prices.to_frame(), freq='QE', span=20)
            net_navs_unsmoothed = net_navs_unsmoothed.loc['31Dec2000':, :]
            print(net_navs_unsmoothed)

            fig = plot_annual_tables(price=net_navs_unsmoothed.iloc[:, 0], perf_params=qis.PerfParams(freq='QE'))
            qis.set_suptitle(fig, title=f"{asset}")

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.SKEW)
