import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Union, List, Dict
from enum import Enum
from optimalportfolios import (compute_joint_alphas,
                               rolling_maximise_alpha_over_tre,
                               Constraints,
                               run_rolling_covar_report)

from mac_portfolio_optimizer import (get_prod_covar_estimator,
                                     load_mac_portfolio_universe,
                                     SaaPortfolio,
                                     MacRangeConstraints,
                                     TaaPortfolio,
                                     RiskModel,
                                     generate_report,
                                     get_meta_params,
                                     create_benchmark_portfolio_from_universe_returns,
                                     load_risk_model_factor_prices,
                                     generate_report_vs_static_benchmark,
                                     AssetClasses,
                                     MAC_ASSET_CLASS_LOADINGS_COLUMNS,
                                     UniverseColumns
                                     )


def run_backtest(prices: pd.DataFrame,
                 universe_df: pd.DataFrame,
                 risk_factor_prices: pd.DataFrame,
                 time_period: qis.TimePeriod,
                 rebalancing_freq: str = 'QE',
                 local_path_out: str = None
                 ) -> None:

    benchmark_price = prices.iloc[:, 0]
    covar_estimator = get_prod_covar_estimator(rebalancing_freq=rebalancing_freq,
                                               apply_unsmoothing_for_pe=False,
                                               returns_freqs='ME',
                                               nonneg=False)

    # 1. estimate covar
    taa_covar_data = covar_estimator.fit_rolling_covars(risk_factor_prices=risk_factor_prices,
                                                        prices=prices,
                                                        time_period=time_period)

    covar_dict = taa_covar_data.y_covars
    group_data_alphas = universe_df['Asset Class']

    # estimate alphas
    alpha_beta_type = pd.Series('Beta', index=prices.columns)
    manager_alphas = compute_joint_alphas(prices=prices.iloc[:, 1:],
                                          benchmark_price=benchmark_price,
                                          risk_factors_prices=risk_factor_prices,
                                          alpha_beta_type=alpha_beta_type.iloc[1:],
                                          rebalancing_freq=rebalancing_freq,
                                          estimated_betas=taa_covar_data.asset_last_betas_t,
                                          group_data_alphas=group_data_alphas.iloc[1:],
                                          return_annualisation_freq_dict={'ME': 12.0, 'QE': 4.0, 'YE': 1.0})

    taa_alphas = manager_alphas.alpha_scores
    alphas_joint = taa_alphas.reindex(index=list(covar_dict.keys()), columns=prices.columns).ffill().fillna(0.0).clip(-3.0, 3.0)

    # reindex at covar frequency and joint prices columns
    benchmark_rolling_weights = qis.df_to_equal_weight_allocation(df=prices, freq=rebalancing_freq)
    #benchmark_rolling_weights = pd.DataFrame(0.0, index=list(covar_dict.keys()), columns=prices.columns)
    #benchmark_rolling_weights.iloc[:, 0] = 1.0
    min_weights = pd.Series(0.0, index=prices.columns)
    max_weights = pd.Series(0.10, index=prices.columns)
    max_weights.iloc[0] = 0.0  # exclude benchmark
    taa_constraints = Constraints(min_weights=min_weights,
                                  max_weights=max_weights,
                                  apply_total_to_good_ratio_for_constraints=True,
                                  tracking_err_vol_constraint=0.2,
                                  turnover_constraint=0.25)

    taa_rolling_weights = rolling_maximise_alpha_over_tre(prices=prices,
                                                          alphas=alphas_joint,
                                                          constraints=taa_constraints,
                                                          benchmark_weights=benchmark_rolling_weights,
                                                          covar_dict=covar_dict,
                                                          time_period=time_period,
                                                          apply_total_to_good_ratio=True,
                                                          is_apply_tre_utility_objective=False)
    print(taa_rolling_weights)

    taa_portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                      weights=taa_rolling_weights,
                                                      management_fee=0.0,
                                                      rebalancing_costs=0.0,
                                                      ticker='Optimal HF Portfolio')

    saa_portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                      weights=benchmark_rolling_weights,
                                                      management_fee=0.0,
                                                      ticker='60/40 Portfolio')

    multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[taa_portfolio_data, saa_portfolio_data],
                                                  benchmark_prices=benchmark_price,
                                                  covar_dict=covar_dict)
    group_order = ['Equities', 'Commodities', 'FX', 'Rates', 'Credit', 'Cross Asset']
    [x.set_group_data(group_data=group_data_alphas, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]

    kwargs = qis.fetch_factsheet_config_kwargs(factsheet_config=qis.FACTSHEET_CONFIG_QUARTERLY_DATA_LONG_PERIOD,
                                                   add_rates_data=False)
    """
    figs = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                         strategy_idx=0,
                                                         # strategy is multi_portfolio_data[strategy_idx]
                                                         benchmark_idx=1,
                                                         add_benchmarks_to_navs=True,
                                                         add_exposures_comp=False,
                                                         add_strategy_factsheet=False,
                                                         add_joint_instrument_history_report=False,
                                                         time_period=time_period,
                                                         **kwargs)
    qis.save_figs_to_pdf(figs=figs,
                         file_name=f"db_qis_portfolio", orientation='landscape',
                         local_path=local_path_out
                         )
    """
    ac_group_data, ac_group_order = group_data_alphas, group_order
    sub_ac_group_data = ac_group_data
    sub_ac_group_order = ac_group_order
    turnover_groups, turnover_order = group_data_alphas, group_order

    risk_model = taa_covar_data.get_linear_factor_model(x_factors=risk_factor_prices,
                                                        y_assets=prices)

    generate_report(multi_portfolio_data=multi_portfolio_data,
                    manager_alphas=manager_alphas,
                    taa_covar_data=taa_covar_data,
                    risk_model=risk_model,
                    time_period=time_period,
                    ac_group_data=ac_group_data,
                    ac_group_order=ac_group_order,
                    sub_ac_group_data=sub_ac_group_data,
                    sub_ac_group_order=sub_ac_group_order,
                    turnover_groups=turnover_groups,
                    turnover_order=turnover_order,
                    file_name=f"db_qis",
                    save_excel=False,
                    save_figures_png=False,
                    local_path=local_path_out)


class LocalTests(Enum):
    CREATE_BBG_DATA = 1
    CHECK = 2
    RUN_OPTIMISER = 3
    COVAR_REPORT = 4


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    import mac_portfolio_optimizer.local_path as lp
    local_path = lp.get_resource_path()

    if local_test == LocalTests.CREATE_BBG_DATA:
        from bbg_fetch import fetch_field_timeseries_per_tickers
        universe_df = qis.load_df_from_excel(file_name='db_qis', local_path=local_path)
        tickers = ['SPTGGUT Index'] + universe_df.index.to_list()
        prices = fetch_field_timeseries_per_tickers(tickers=tickers)
        prices = prices.dropna(axis=0, how='all').dropna(axis=1, how='all')
        universe_df.loc['SPTGGUT Index', :] = pd.Series({'Strategy Name': '60/40', 'Asset Class': '60/40'})
        universe_df = universe_df.reindex(index=prices.columns)
        qis.save_df_to_csv(df=prices, file_name='db_qis_prices', local_path=local_path)
        qis.save_df_to_csv(df=universe_df, file_name='db_qis_universe', local_path=local_path)
        print(universe_df)

    elif local_test == LocalTests.CHECK:
        db_qis_prices = qis.load_df_from_csv(file_name='db_qis_prices', local_path=local_path)
        qis.plot_ra_perf_table(prices=db_qis_prices)

    elif local_test == LocalTests.RUN_OPTIMISER:
        risk_factor_prices = load_risk_model_factor_prices(local_path=local_path, risk_model=RiskModel.FUTURES_RISK_FACTORS)
        db_qis_prices = qis.load_df_from_csv(file_name='db_qis_prices', local_path=local_path)
        universe_df = qis.load_df_from_csv(file_name='db_qis_universe', local_path=local_path)
        time_period = qis.TimePeriod('31Dec2006', '30Sep2025')
        db_qis_prices = db_qis_prices.loc['31Dec2000': , :].ffill()
        run_backtest(prices=db_qis_prices,
                     universe_df=universe_df,
                     risk_factor_prices=risk_factor_prices,
                     time_period=time_period,
                     local_path_out=lp.get_output_path()
                     )

    elif local_test == LocalTests.COVAR_REPORT:
        risk_factor_prices = load_risk_model_factor_prices(local_path=local_path, risk_model=RiskModel.FUTURES_RISK_FACTORS)
        db_qis_prices = qis.load_df_from_csv(file_name='db_qis_prices', local_path=local_path)
        universe_df = qis.load_df_from_csv(file_name='db_qis_universe', local_path=local_path)
        time_period = qis.TimePeriod('31Dec2024', '30Sep2025')
        db_qis_prices = db_qis_prices.loc['31Dec2000': , :].ffill()

        covar_estimator = get_prod_covar_estimator(rebalancing_freq='YE',
                                                   apply_unsmoothing_for_pe=False,
                                                   returns_freqs='ME',
                                                   nonneg=False)

        figs, dfs = run_rolling_covar_report(risk_factor_prices=risk_factor_prices,
                                        prices=db_qis_prices,
                                        covar_estimator=covar_estimator,
                                        time_period=time_period, is_plot=True)
        print(f"saved")
        qis.save_df_to_excel(dfs, file_name='db_covar_report_data', local_path=lp.get_output_path())
        qis.save_figs_to_pdf(figs, file_name='db_covar_report', local_path=lp.get_output_path())
        plt.close('all')

    plt.close('all')


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.COVAR_REPORT)
