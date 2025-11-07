"""
run prod backtest for funds portfolio
"""
# packages
import matplotlib.pyplot as plt
import pandas as pd
import qis as qis
from enum import Enum
from typing import List, Tuple, Dict, Any

# project
import mac_portfolio_optimizer.local_path as lp
from mac_portfolio_optimizer import (get_prod_covar_estimator,
                                     load_mac_portfolio_universe,
                                     MacUniverseData,
                                     SaaPortfolio,
                                     MacRangeConstraints,
                                     TaaPortfolio,
                                     backtest_joint_saa_taa_portfolios,
                                     range_backtest_lasso_portfolio_with_alphas,
                                     tre_range_backtest_lasso_portfolio_with_alphas,
                                     RiskModel,
                                     generate_report,
                                     get_meta_params,
                                     create_benchmark_portfolio_from_universe_returns,
                                     load_risk_model_factor_prices,
                                     generate_report_vs_static_benchmark,
                                     AssetClasses,
                                     MAC_ASSET_CLASS_LOADINGS_COLUMNS)


def run_mac_universe_vs_index_funds_backtest(local_path: str,
                                             time_period: qis.TimePeriod,
                                             meta_params: Dict,
                                             report_kwargs: Dict,
                                             apply_unsmoothing_for_pe: bool = True
                                             ) -> Tuple[List[plt.Figure], Dict[str, pd.DataFrame]]:
    # load universe
    funds_universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                      saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                      taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC)
    index_universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                      saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                      taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER)


    # funds
    funds_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                     apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                     returns_freqs=funds_universe_data.get_joint_rebalancing_freqs())
    funds_multi_portfolio_data, funds_manager_alphas, taa_covar_data = backtest_joint_saa_taa_portfolios(universe_data=funds_universe_data,
                                                                                                         time_period=time_period,
                                                                                                         covar_estimator=funds_covar_estimator,
                                                                                                         **meta_params)
    taa_funds_portfolio = funds_multi_portfolio_data.portfolio_datas[0].set_ticker('TAA Funds MAC')
    saa_portfolio = funds_multi_portfolio_data.portfolio_datas[1]

    # index
    index_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                     apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                     returns_freqs=index_universe_data.get_joint_rebalancing_freqs())
    index_multi_portfolio_data, index_manager_alphas, taa_covar_data = backtest_joint_saa_taa_portfolios(universe_data=index_universe_data,
                                                                                                         time_period=time_period,
                                                                                                         covar_estimator=index_covar_estimator,
                                                                                                         **meta_params)
    taa_index_portfolio = index_multi_portfolio_data.portfolio_datas[0].set_ticker('TAA Index MAC')

    multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[taa_funds_portfolio, taa_index_portfolio, saa_portfolio],
                                                  benchmark_prices=funds_universe_data.benchmarks)

    figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=multi_portfolio_data,
                                                  backtest_name='SAA Funds & Index MAC Portfolios',
                                                  add_benchmarks_to_navs=True,
                                                  time_period=time_period,
                                                  **report_kwargs)

    # excel outputs
    navs = multi_portfolio_data.get_navs(add_benchmarks_to_navs=True, time_period=time_period)
    navs = navs.asfreq('ME', method='ffill').ffill()
    monthly_returns = qis.to_returns(prices=navs)
    perf_table = multi_portfolio_data.get_ra_perf_table(benchmark=funds_universe_data.benchmarks.columns[0],
                                                        time_period=time_period,
                                                        is_convert_to_str=False,
                                                        **report_kwargs)

    data = dict(perf_table=perf_table,
                navs=navs,
                monthly_returns=monthly_returns,
                taa_fund_weights=taa_funds_portfolio.get_input_weights()[funds_universe_data.taa_prices.columns],
                taa_index_weights=taa_index_portfolio.get_input_weights()[index_universe_data.taa_prices.columns],
                saa_weights=saa_portfolio.get_input_weights())

    return figs, data


def run_mac_pe_smoothed_vs_newey(universe_data: MacUniverseData,
                                 time_period: qis.TimePeriod,
                                 meta_params: Dict[str, Any]
                                 ) -> None:

    # PE unmoothing
    un_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                  apply_unsmoothing_for_pe=True,
                                                  returns_freqs=universe_data.get_joint_rebalancing_freqs())
    unmoothing_multi_portfolio_data, unmoothing_funds_manager_alphas, taa_covar_data = backtest_joint_saa_taa_portfolios(universe_data=universe_data,
                                                                                                                         time_period=time_period,
                                                                                                                         covar_estimator=un_covar_estimator,
                                                                                                                         **meta_params)
    unmoothing_taa_portfolio = unmoothing_multi_portfolio_data.portfolio_datas[0].set_ticker('MAC with PE unmoothing')
    unmoothing_saa_portfolio = unmoothing_multi_portfolio_data.portfolio_datas[1].set_ticker('SAA with PE unmoothing')

    # Newey-West
    nw_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                     apply_unsmoothing_for_pe=False,
                                                     returns_freqs=universe_data.get_joint_rebalancing_freqs())
    nw_multi_portfolio_data, nw_manager_alphas, nw_covar_data = backtest_joint_saa_taa_portfolios(universe_data=universe_data,
                                                                                                  time_period=time_period,
                                                                                                  covar_estimator=nw_covar_estimator,
                                                                                                  **meta_params)
    nw_taa_portfolio = nw_multi_portfolio_data.portfolio_datas[0].set_ticker('MAC with Newey-West')
    nw_saa_portfolio = nw_multi_portfolio_data.portfolio_datas[1].set_ticker('SAA with Newey-West')

    saa_portfolio_datas = qis.MultiPortfolioData(portfolio_datas=[unmoothing_saa_portfolio, nw_saa_portfolio],
                                                 benchmark_prices=universe_data.benchmarks,
                                                 covar_dict=unmoothing_multi_portfolio_data.covar_dict)

    taa_portfolio_datas = qis.MultiPortfolioData(portfolio_datas=[unmoothing_taa_portfolio, nw_taa_portfolio],
                                                 benchmark_prices=universe_data.benchmarks,
                                                 covar_dict=unmoothing_multi_portfolio_data.covar_dict)

    generate_report(multi_portfolio_data=taa_portfolio_datas,
                    manager_alphas=None,
                    taa_covar_data=nw_covar_data,
                    universe_data=universe_data,
                    time_period=time_period,
                    file_name=f"mac_pe_unsmoothed_vs_nw",
                    save_excel=False,
                    local_path=lp.get_output_path())

    generate_report(multi_portfolio_data=saa_portfolio_datas,
                    manager_alphas=None,
                    taa_covar_data=nw_covar_data,
                    universe_data=universe_data,
                    time_period=time_period,
                    file_name=f"saa_pe_unsmoothed_vs_nw",
                    save_excel=False,
                    local_path=lp.get_output_path())


def run_risk_model_futures_vs_funds_backtest(local_path: str,
                                             universe_data: MacUniverseData,
                                             time_period: qis.TimePeriod,
                                             meta_params: Dict,
                                             apply_unsmoothing_for_pe: bool = True
                                             ) -> None:
    # load risk models
    risk_model1 = load_risk_model_factor_prices(local_path=local_path, risk_model=RiskModel.FUTURES_RISK_FACTORS)
    risk_model2 = load_risk_model_factor_prices(local_path=local_path, risk_model=RiskModel.PRICE_FACTORS_FROM_MAC_PAPER)

    # load universe
    universe_data1 = universe_data.copy(kwargs=dict(risk_factor_prices=risk_model1))
    universe_data2 = universe_data.copy(kwargs=dict(risk_factor_prices=risk_model2))

    funds_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                     apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                     returns_freqs=universe_data1.get_joint_rebalancing_freqs())

    # 1
    funds_multi_portfolio_data1, funds_manager_alphas1, taa_covar_data1 = backtest_joint_saa_taa_portfolios(universe_data=universe_data1,
                                                                                                            time_period=time_period,
                                                                                                            covar_estimator=funds_covar_estimator,
                                                                                                            **meta_params)
    taa_portfolio1 = funds_multi_portfolio_data1.portfolio_datas[0].set_ticker('MAC FuturesRisk')
    saa_portfolio1 = funds_multi_portfolio_data1.portfolio_datas[1].set_ticker('SAA FuturesRisk')

    # 2
    funds_multi_portfolio_data2, funds_manager_alphas2, taa_covar_data2 = backtest_joint_saa_taa_portfolios(universe_data=universe_data2,
                                                                                                            time_period=time_period,
                                                                                                            covar_estimator=funds_covar_estimator,
                                                                                                            **meta_params)
    taa_portfolio2 = funds_multi_portfolio_data2.portfolio_datas[0].set_ticker('MAC IndexRisk')
    saa_portfolio2 = funds_multi_portfolio_data2.portfolio_datas[1].set_ticker('SAA IndexRisk')

    saa_portfolio_datas = qis.MultiPortfolioData(portfolio_datas=[saa_portfolio1, saa_portfolio2],
                                                 benchmark_prices=universe_data1.benchmarks,
                                                 covar_dict=funds_multi_portfolio_data1.covar_dict)

    taa_portfolio_datas = qis.MultiPortfolioData(portfolio_datas=[taa_portfolio1, taa_portfolio2],
                                                 benchmark_prices=universe_data1.benchmarks,
                                                 covar_dict=funds_multi_portfolio_data1.covar_dict)

    generate_report(multi_portfolio_data=taa_portfolio_datas,
                    manager_alphas=None,
                    taa_covar_data=taa_covar_data1,
                    universe_data=universe_data1,
                    time_period=time_period,
                    file_name=f"mac_risk_model",
                    save_excel=False,
                    local_path=lp.get_output_path())

    generate_report(multi_portfolio_data=saa_portfolio_datas,
                    manager_alphas=None,
                    taa_covar_data=taa_covar_data1,
                    universe_data=universe_data1,
                    time_period=time_period,
                    file_name=f"saa_risk_model",
                    save_excel=False,
                    local_path=lp.get_output_path())


class InvestmentUniverse(Enum):
    MAC_PROD = 1
    MAC_PAPER = 2
    EQ_BESPOKE = 3


class LocalTests(Enum):
    UNIVERSE_REPORT = 1
    SAA_TAA_BACKTEST_REPORT = 2 # standard backtest report
    SAA_TAA_BACKTEST_RANGE = 4
    SAA_TAA_BACKTEST_TRE_RANGE = 4
    INDEX_FUNDS_BACKTEST = 5  # backtest mac taa funds vs paper taa indices
    PE_SMOOTHING_VS_NEWEY_WEST = 6
    RISK_MODEL_FUTURES_VS_FUNDS_BACKTEST = 7


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # time_period = qis.TimePeriod('31Dec2022', '23Dec2024')
    # time_period = qis.TimePeriod('31Dec2022', '28Feb2025')
    # time_period = qis.TimePeriod('31Dec2004', '31May2025')
    # time_period = qis.TimePeriod('31Dec2004', '31Jul2025')
    # time_period = qis.TimePeriod('30Jun2004', '31Jul2025')
    # time_period = qis.TimePeriod('31Dec2004', '31Aug2025')
    time_period = qis.TimePeriod('31Dec2004', '30Sep2025')

    local_path = f"{lp.get_resource_path()}"

    local_path_out = lp.get_output_path()
    # local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//New Figures//"

    # load universe
    investment_universe = InvestmentUniverse.MAC_PROD
    static_benchmark = None
    if investment_universe == InvestmentUniverse.MAC_PROD:
        mac_constraints = MacRangeConstraints.UNCONSTRAINT.value
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                    sub_asset_class_ranges_sheet_name=mac_constraints,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS,
                                                    sub_asset_class_columns=MAC_ASSET_CLASS_LOADINGS_COLUMNS)
        meta_params = get_meta_params()
        file_name = 'mac_unconstraint' if mac_constraints is None else  f"mac_{mac_constraints}"

    elif investment_universe == InvestmentUniverse.MAC_PAPER:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)
        universe_data.benchmarks = universe_data.compute_static_weight_saa_benchmark(management_fee=0.0).to_frame()

        group_max_turnover_constraint = pd.Series({0: 1.0,
                                                   1: 0.20,
                                                   2: 0.10,
                                                   3: 0.10})
        tracking_err_vol_constraint = 0.03  # in paper = 0.03
        group_tracking_err_vol_constraint = universe_data.set_group_uniform_tracking_error_constraint(
            tracking_err_vol_constraint=tracking_err_vol_constraint)
        meta_params = dict(group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                           group_max_turnover_constraint=group_max_turnover_constraint,
                           global_max_turnover_constraint=None,
                           management_fee=0.0,
                           is_saa_benchmark_for_betas=True,
                           rebalancing_costs=0.0020,
                           saa_rebalancing_freq='QE')
        file_name = 'index_saa_taa_portfolio'

    elif investment_universe == InvestmentUniverse.EQ_BESPOKE:

        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio="saa_index_customport",
                                                    taa_portfolio="taa_fund_customport",
                                                    saa_range_constraints="saa_asset_class_customport",
                                                    risk_model=RiskModel.PRICE_FACTORS_FROM_MAC_PAPER)

        static_benchmark = create_benchmark_portfolio_from_universe_returns(local_path=local_path,
                                                                        benchmark_weights={'LUATTRUU': 0.45, 'NDUEACWF': 0.55},
                                                                        rebalancing_freq='YE',
                                                                        ticker='45/55 Agg/MSCI')
        static_benchmark.set_group_data(group_data=pd.Series({'LUATTRUU': AssetClasses.FI.value, 'NDUEACWF': AssetClasses.EQ.value}))
        universe_data.benchmarks = static_benchmark.get_portfolio_nav(freq='ME').to_frame()
        group_max_turnover_constraint = pd.Series({0: 1.0,
                                                   1: 0.2,
                                                   2: 0.1,
                                                   3: 0.1,
                                                   4: 0.1,
                                                   5: 0.1})
        tracking_err_vol_constraint = 0.04
        group_tracking_err_vol_constraint = pd.Series({AssetClasses.LIQUIDITY.value: tracking_err_vol_constraint,
                                                       AssetClasses.FI.value: tracking_err_vol_constraint,
                                                       AssetClasses.EQ.value: tracking_err_vol_constraint,
                                                       AssetClasses.ALTS.value: tracking_err_vol_constraint})

        meta_params = dict(global_tracking_err_vol_constraint=None,
                           group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                           global_max_turnover_constraint=None,
                           group_max_turnover_constraint=group_max_turnover_constraint,
                           management_fee=0.0,
                           is_saa_benchmark_for_betas=True,
                           is_joint_saa_taa_covar=True,
                           rebalancing_costs=0.0,
                           saa_rebalancing_freq='QE')
        file_name = 'customport'

    else:
        raise NotImplementedError(f"{investment_universe}")

    # set model params
    apply_unsmoothing_for_pe = True
    covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                               apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                               returns_freqs=universe_data.get_joint_rebalancing_freqs(),
                                               nonneg=False)

    # set report kwargs
    report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                    reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                    add_rates_data=False)
    report_kwargs = qis.update_kwargs(report_kwargs, dict(ytd_attribution_time_period=qis.TimePeriod('30Jun2024', '31Aug2025')))



    if local_test == LocalTests.UNIVERSE_REPORT:
        time_period = qis.TimePeriod('30Jun2024', '31Jul2025')
        taa_prices = universe_data.get_taa_prices(time_period=time_period)
        ac = universe_data.get_taa_asset_class_data()
        equities = ac.loc[ac == AssetClasses.EQ.value].index.to_list()
        static_benchmark = create_benchmark_portfolio_from_universe_returns(local_path=local_path,
                                                                        benchmark_weights={'LUATTRUU': 0.0, 'NDUEACWF': 1.00},
                                                                        rebalancing_freq='YE',
                                                                        ticker='MSCI ACWF')
        perf_columns = [qis.PerfStat.TOTAL_RETURN,
                        qis.PerfStat.VOL,
                        qis.PerfStat.SHARPE_RF0,
                        qis.PerfStat.MAX_DD,
                        qis.PerfStat.SKEWNESS,
                        qis.PerfStat.ALPHA_AN,
                        qis.PerfStat.BETA,
                        qis.PerfStat.R2,
                        qis.PerfStat.ALPHA_PVALUE]
        fig, _ = qis.plot_ra_perf_table_benchmark(prices=taa_prices[equities],
                                         perf_columns=perf_columns,
                                         benchmark_price=static_benchmark.get_portfolio_nav(),
                                         perf_params=qis.PerfParams(freq='ME', freq_reg='ME', alpha_an_factor=12),
                                         heatmap_columns=[1, 3],
                                         title=f"Perfromance over {time_period.to_str()}")
        qis.save_fig(fig=fig, file_name='universe_retirns', local_path=lp.get_output_path())


    elif local_test == LocalTests.SAA_TAA_BACKTEST_REPORT:
        multi_portfolio_data, manager_alphas, taa_covar_data = backtest_joint_saa_taa_portfolios(universe_data=universe_data,
                                                                                                 time_period=time_period,
                                                                                                 covar_estimator=covar_estimator,
                                                                                                 is_apply_tre_utility_objective=False,
                                                                                                 **meta_params)
        generate_report(multi_portfolio_data=multi_portfolio_data,
                        manager_alphas=manager_alphas,
                        taa_covar_data=taa_covar_data,
                        universe_data=universe_data,
                        time_period=time_period,
                        file_name=f"{file_name}",
                        save_figures_png=False,
                        local_path=local_path_out)

        if static_benchmark is not None:
            generate_report_vs_static_benchmark(multi_portfolio_data=multi_portfolio_data,
                                                static_benchmark=static_benchmark,
                                                universe_data=universe_data,
                                                time_period=time_period,
                                                file_name=f"{file_name}_vs_static_benchmark",
                                                local_path=lp.get_output_path())

    elif local_test == LocalTests.SAA_TAA_BACKTEST_RANGE:
        saa_multi_portfolio_data, taa_multi_portfolio_data = \
            range_backtest_lasso_portfolio_with_alphas(universe_data=universe_data,
                                                       time_period=time_period,
                                                       covar_estimator=covar_estimator,
                                                       **meta_params)

        figs1 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=saa_multi_portfolio_data,
                                                       backtest_name='SAA Portfolios',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name='saa_lasso_portfolio_range', local_path=lp.get_output_path())

        figs2 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=taa_multi_portfolio_data,
                                                       backtest_name='TAA Portfolios',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs2, file_name='taa_lasso_portfolio_range', local_path=lp.get_output_path())

    elif local_test == LocalTests.SAA_TAA_BACKTEST_TRE_RANGE:
        saa_multi_portfolio_data, taa_multi_portfolio_data = \
            tre_range_backtest_lasso_portfolio_with_alphas(universe_data=universe_data,
                                                           time_period=time_period,
                                                           covar_estimator=covar_estimator,
                                                           **meta_params)
        figs1 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=saa_multi_portfolio_data,
                                                       backtest_name='SAA Portfolios',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name='saa_tre_portfolio_range', local_path=lp.get_output_path())

        figs2 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=taa_multi_portfolio_data,
                                                       backtest_name='TAA Portfolios for tracking error and turnover ranges',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs2, file_name='taa_tre_portfolio_range', local_path=lp.get_output_path())

    elif local_test == LocalTests.INDEX_FUNDS_BACKTEST:
        # backtest mac taa funds vs paper taa indices
        figs, data = run_mac_universe_vs_index_funds_backtest(local_path=local_path,
                                              time_period=time_period,
                                              apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                              meta_params=meta_params,
                                              report_kwargs=report_kwargs)
        qis.save_figs_to_pdf(figs, file_name=f"funds_index_taa", local_path=lp.get_output_path())
        qis.save_df_to_excel(data=data,
                             file_name=f"{file_name}_with_returns",
                             add_current_date=True, local_path=lp.get_output_path())

    elif local_test == LocalTests.PE_SMOOTHING_VS_NEWEY_WEST:
        # backtest mac taa funds vs paper taa indices
        run_mac_pe_smoothed_vs_newey(universe_data=universe_data,
                                     time_period=time_period,
                                     meta_params=meta_params)

    elif local_test == LocalTests.RISK_MODEL_FUTURES_VS_FUNDS_BACKTEST:
        # backtest mac taa funds vs paper taa indices
        run_risk_model_futures_vs_funds_backtest(local_path=local_path,
                                                 universe_data=universe_data,
                                                 time_period=time_period,
                                                 apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                 meta_params=meta_params)

if __name__ == '__main__':

    run_local_test(local_test=LocalTests.SAA_TAA_BACKTEST_REPORT)
