import pandas as pd
import numpy as np
import qis as qis
import seaborn as sns
from matplotlib import pyplot as plt
from typing import Optional, Union, List
from enum import Enum
from qis import PerfStat
from qis import EwmLinearModel
from optimalportfolios import estimate_rolling_lasso_covar, LassoModel

def estimate_betas_alphas(cma_factors: pd.DataFrame,
                          derived_assets: pd.DataFrame,
                          time_period: qis.TimePeriod,
                          freq: str = 'ME',
                          span: int = 36,
                          warmup_period: int = 24
                          ) -> List[plt.Figure]:
    # compute x and y
    cma_factors = cma_factors.reindex(index=derived_assets.index)

    # estimate using demened
    x = qis.to_returns(cma_factors, is_log_returns=False, drop_first=True, freq=freq)
    y = qis.to_returns(derived_assets, is_log_returns=False, drop_first=True, freq=freq)

    # estimate without demean for total alphas
    ewm_linear_model = EwmLinearModel(x=x, y=y)
    ewm_linear_model.fit(span=span, is_x_correlated=True, mean_adj_type=qis.MeanAdjType.EWMA, warmup_period=warmup_period)

    # exlude negative betas
    lasso_model = LassoModel(span=span, reg_lambda=1e-10, nonneg=True, warmup_period=warmup_period, demean=False)
    lasso_covar = estimate_rolling_lasso_covar(risk_factor_prices=cma_factors,
                                               prices=derived_assets,
                                               time_period=time_period,
                                               lasso_model=lasso_model,
                                               returns_freq=freq,
                                               factor_returns_freq=freq,
                                               rebalancing_freq=freq,
                                               span=span)
    lasso_risk_model = lasso_covar.get_linear_factor_model(x_factors=x, y_assets=y, to_returns=False)

    # estimate without demean for total alphas
    ewm_alpha, _ = ewm_linear_model.get_factor_alpha(x=x, y=y, span=span, lag=1)
    lasso_alpha, _ = lasso_risk_model.get_factor_alpha(x=x, y=y, span=span, lag=1)

    ewm_r2 = ewm_linear_model.get_model_ewm_r2(span=span)
    lasso_r2 = lasso_risk_model.get_model_ewm_r2(span=span)

    figs = []
    perf_columns = [PerfStat.START_DATE,
                    PerfStat.PA_RETURN,
                    PerfStat.VOL,
                    PerfStat.SHARPE_RF0,
                    PerfStat.MAX_DD,
                    PerfStat.SKEWNESS,
                    PerfStat.ALPHA_AN,
                    PerfStat.BETA,
                    PerfStat.R2,
                    PerfStat.ALPHA_PVALUE]
    fig, _ = qis.plot_ra_perf_table_benchmark(prices=time_period.locate(derived_assets),
                                              benchmark_price=cma_factors.iloc[:, 0],
                                              perf_columns=perf_columns,
                                              perf_params=qis.PerfParams(freq='ME', alpha_an_factor=12))
    qis.set_suptitle(fig, title=f"Risk-adjusted table with ME-freq")
    figs.append(fig)
    for asset in derived_assets:
        ewma_betas = ewm_linear_model.get_asset_factor_betas(asset=asset)
        lasso_betas = lasso_risk_model.get_asset_factor_betas(asset=asset)
        annualised_alphas = 12.0*pd.concat([ewm_alpha[asset].rename('EWMA'), lasso_alpha[asset].rename('Lasso')
                                            ], axis=1).iloc[warmup_period:, :]
        r2 = pd.concat([ewm_r2[asset].rename('EWMA'), lasso_r2[asset].rename('Lasso')
                        ], axis=1).iloc[warmup_period:, :]

        with sns.axes_style("darkgrid"):
            fig, axs = plt.subplots(2, 2, figsize=(18, 10))
            qis.set_suptitle(fig, title=f"{asset}")
            figs.append(fig)
            qis.plot_time_series(df=time_period.locate(ewma_betas), title='EWMA Betas', ax=axs[0, 0])
            qis.plot_time_series(df=time_period.locate(lasso_betas), title='Lasso Betas', ax=axs[0, 1])
            qis.plot_time_series(df=time_period.locate(annualised_alphas), title='Annual Rolling Alphas', var_format='{:.2%}', ax=axs[1, 0])
            qis.plot_time_series(df=time_period.locate(r2), title='R2', var_format='{:.2%}', ax=axs[1, 1])
            axs[0, 0].set_xticklabels('')
            axs[0, 1].set_xticklabels('')

    return figs


class LocalTests(Enum):
    BBG_DATA = 1
    BETAS = 2


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
    local_path_out = lp.get_output_path()

    if local_test == LocalTests.BBG_DATA:
        from bbg_fetch import fetch_field_timeseries_per_tickers
        tickers = {'MXWO Index': 'DM World',
                   'LGTRTRUH Index': 'GB Global',
                   'LEGATRUH Index': 'IG Global',
                   'H23059US Index': 'HY Global'}

        dm_indices = {
            "MXWO000V Index": "DM Value",
            "MXWOMOM Index": "DM Momentum",
            "MXWO000G Index": "DM Growth",
            "MXWOSC Index": "DM Small Cap",
            "MXWOLC Index": "DM Large Cap",
            "MXWOMVOL Index": "DM Minimum Variance",
            "MXWOQU Index": "DM Quality",
            "MXWDHDVD Index": "DM High Dividend",
            "CCMP Index": "DM Technology"
        }

        hf_indices = {
            "HFRXGL Index": "HF UCITS",
            "HFRXEH Index": "HF UCITS Equity Long/Short",
            "HFRXED Index": "HF UCITS Event Driven",
            "HFRXM Index": "HF UCITS Macro",
            "HFRXRVA Index": "HF UCITS Relative Value",
            "NEIXCTAT Index": "HF Diversified Trend",
            "HFRIFWI Index": "HF",
            "HFRIEHI Index": "HF Equity Hedge",
            "HFRIEDI Index": "HF Event Driven",
            "HRIMI Index": "HF Macro",
            "HFRIRVA Index": "HF Relative Value",
            "SRGLTRR Index": "ILS1",
            "LGTIPBU LX Equity": "ILS2",
            "EHFI804 Index": "ILS3"
        }
        
        dd = dict(cma_factors=tickers, dm_indices=dm_indices, hf_indices=hf_indices)
        for key, tickers in dd.items():
            prices = fetch_field_timeseries_per_tickers(tickers=tickers)
            qis.save_df_to_csv(df=prices, file_name=key, local_path=local_path)

    elif local_test == LocalTests.BETAS:
        cma_factors = qis.load_df_from_csv(file_name='cma_factors', local_path=local_path).loc['1999':, :]
        dm_indices = qis.load_df_from_csv(file_name='dm_indices', local_path=local_path).loc['1999':, :]
        hf_indices = qis.load_df_from_csv(file_name='hf_indices', local_path=local_path).loc['1999':, :]

        cma_factors = cma_factors[['DM World', 'IG Global']]
        kwargs = dict(time_period=qis.TimePeriod('31Dec2004', '30Sep2025'), freq='ME', span=12*5)
        # dm
        figs = estimate_betas_alphas(cma_factors=cma_factors, derived_assets=dm_indices, **kwargs)
        qis.save_figs_to_pdf(figs, file_name='dm_betas', local_path=local_path_out)
        # hf
        figs = estimate_betas_alphas(cma_factors=cma_factors, derived_assets=hf_indices, **kwargs)
        qis.save_figs_to_pdf(figs, file_name='hf_betas', local_path=local_path_out)

    plt.close('all')


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.BETAS)
