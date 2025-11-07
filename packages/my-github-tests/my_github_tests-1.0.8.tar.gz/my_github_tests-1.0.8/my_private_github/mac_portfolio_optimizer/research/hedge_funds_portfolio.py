"""
run backtest for funds portfolio
"""
# packages
import pandas as pd
import qis as qis
from enum import Enum
from typing import List, Tuple, Dict, Any
from optimalportfolios import (compute_joint_alphas,
                               rolling_maximise_alpha_over_tre,
                               Constraints)

# project
import mac_portfolio_optimizer.local_path as lp
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


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

time_period = qis.TimePeriod('31Dec2007', '30Sep2025')

local_path = f"{lp.get_resource_path()}"
local_path_out = lp.get_output_path()

# load universe
mac_constraints = MacRangeConstraints.UNCONSTRAINT.value
universe_data = load_mac_portfolio_universe(local_path=local_path,
                                            saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                            taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                            sub_asset_class_ranges_sheet_name=mac_constraints,
                                            risk_model=RiskModel.FUTURES_RISK_FACTORS,
                                            sub_asset_class_columns=MAC_ASSET_CLASS_LOADINGS_COLUMNS)
meta_params = get_meta_params()
file_name = 'mac_unconstraint' if mac_constraints is None else f"mac_{mac_constraints}"

hf_mask = universe_data.taa_universe_df.loc[universe_data.taa_universe_df[UniverseColumns.SUB_ASSET_CLASS.value] == 'Hedge Funds', :]
print(hf_mask)

hf_prices = universe_data.taa_prices[hf_mask.index]

benchmark_price = universe_data.taa_prices[['Vanguard S&P 500 UCITS ETF (VUSD LN) USD', 'iShares US Treasury 7-10yr Bond ETF']]
benchmark_price.columns = ['S&P500', '10Y UST']
kwargs = qis.fetch_factsheet_config_kwargs(factsheet_config=qis.FACTSHEET_CONFIG_QUARTERLY_DATA_LONG_PERIOD,
                                           add_rates_data=False)

"""
hf_prices.columns = hf_prices.columns.map(lambda x: x[:20])  # make column names shorter
fig = qis.generate_multi_asset_factsheet(prices=hf_prices,
                                         benchmark_prices=benchmark_price,
                                         time_period=time_period,
                                         **kwargs)
qis.save_figs_to_pdf(figs=[fig],
                     file_name=f"hf_mac_report", orientation='landscape',
                     local_path=local_path_out
                     )
"""

covar_estimator = get_prod_covar_estimator(rebalancing_freq='QE',
                                           apply_unsmoothing_for_pe=False,
                                           returns_freqs='QE',
                                           nonneg=False)

# 1. estimate covar
taa_covar_data = covar_estimator.fit_rolling_covars(risk_factor_prices=universe_data.get_risk_factors(),
                                                    prices=hf_prices,
                                                    time_period=time_period)
covar_dict = taa_covar_data.y_covars


# estimate alphas
group_data_alphas = universe_data.get_taa_alpha_group_data().loc[hf_prices.columns]
# compute alpha using reported prices
alpha_beta_type = universe_data.get_alpha_beta_type().loc[hf_prices.columns]
# alpha_beta_type = pd.Series('Beta', index=alpha_beta_type.index)
manager_alphas = compute_joint_alphas(prices=hf_prices,
                                      benchmark_price=benchmark_price,
                                      risk_factors_prices=universe_data.get_risk_factors(),
                                      alpha_beta_type=alpha_beta_type,
                                      rebalancing_freq='QE',
                                      estimated_betas=taa_covar_data.asset_last_betas_t,
                                      group_data_alphas=group_data_alphas,
                                      return_annualisation_freq_dict=universe_data.return_annualisation_freq_dict)

taa_alphas = manager_alphas.alpha_scores

# align alphas
alphas_joint = taa_alphas.reindex(index=list(covar_dict.keys()), method='ffill').ffill().fillna(0.0).clip(-3.0, 3.0)

# reindex at covar frequency and joint prices columns
benchmark_rolling_weights = qis.df_to_equal_weight_allocation(df=hf_prices, freq='QE')
benchmark_rolling_weights = benchmark_rolling_weights.reindex(index=list(covar_dict.keys()), method='ffill').ffill().fillna(0.0)
taa_constraints = Constraints(min_weights=pd.Series(0.0, index=hf_prices.columns),
                              max_weights=pd.Series(0.25, index=hf_prices.columns),
                              apply_total_to_good_ratio_for_constraints=True,
                              tracking_err_vol_constraint=0.03,
                              turnover_constraint=0.25)

taa_rolling_weights = rolling_maximise_alpha_over_tre(prices=hf_prices,
                                                      alphas=alphas_joint,
                                                      constraints=taa_constraints,
                                                      benchmark_weights=benchmark_rolling_weights,
                                                      covar_dict=covar_dict,
                                                      time_period=time_period,
                                                      apply_total_to_good_ratio=True,
                                                      is_apply_tre_utility_objective=False)


taa_portfolio_data = qis.backtest_model_portfolio(prices=hf_prices,
                                                  weights=taa_rolling_weights,
                                                  management_fee=0.0,
                                                  rebalancing_costs=0.0,
                                                  ticker='Optimal HF Portfolio')

saa_portfolio_data = qis.backtest_model_portfolio(prices=hf_prices,
                                            weights=benchmark_rolling_weights,
                                            management_fee=0.0,
                                            ticker='EW HF Portfolio')

multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[taa_portfolio_data, saa_portfolio_data],
                                              benchmark_prices=benchmark_price,
                                              covar_dict=covar_dict)
group_data, group_order = universe_data.get_joint_sub_ac_group_data()
[x.set_group_data(group_data=group_data, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]

figs = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                     strategy_idx=0,
                                                     # strategy is multi_portfolio_data[strategy_idx]
                                                     benchmark_idx=1,
                                                     add_benchmarks_to_navs=True,
                                                     add_exposures_comp=False,
                                                     add_strategy_factsheet=True,
                                                     add_joint_instrument_history_report=True,
                                                     time_period=time_period,
                                                     **kwargs)

qis.save_figs_to_pdf(figs=figs,
                     file_name=f"hf_portfolio", orientation='landscape',
                     local_path=local_path_out
                     )
