import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import qis as qis
from enum import Enum

from optimalportfolios import run_rolling_covar_report


class LocalTests(Enum):
    RUN_REPORT = 1


@qis.timer
def run_local_test(local_test: LocalTests):
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    time_period = qis.TimePeriod('31Dec2024', '31Mar2025')
    # time_period = qis.TimePeriod('31Dec2024', '31Aug2025')

    import mac_portfolio_optimizer.local_path as lp
    local_path = f"{lp.get_resource_path()}"

    from mac_portfolio_optimizer import (get_prod_covar_estimator,
                                         load_mac_portfolio_universe,
                                         SaaPortfolio,
                                         TaaPortfolio,
                                         RiskModel)

    # load universe
    is_funds_universe = False
    if is_funds_universe:

        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)
        """
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio="saa_index_customport",
                                                    taa_portfolio="taa_fund_customport",
                                                    saa_range_constraints="saa_asset_class_customport",
                                                    risk_model=RiskModel.PRICE_FACTORS_FROM_MAC_PAPER)
        """
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)

    # set lasso model params
    saa_rebalancing_freq = 'YE'
    apply_unsmoothing_for_pe = True
    returns_freqs = universe_data.get_joint_rebalancing_freqs()
    covar_estimator = get_prod_covar_estimator(rebalancing_freq=saa_rebalancing_freq,
                                               apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                               returns_freqs=returns_freqs,
                                               nonneg=False)

    if local_test == LocalTests.RUN_REPORT:
        figs, dfs = run_rolling_covar_report(risk_factor_prices=universe_data.get_risk_factors(),
                                        prices=universe_data.get_joint_prices(apply_unsmoothing_for_pe=apply_unsmoothing_for_pe),
                                        covar_estimator=covar_estimator,
                                        time_period=time_period,
                                             is_plot=True)
        print(f"saved")
        qis.save_df_to_excel(dfs, file_name='covar_report_data', local_path=lp.get_output_path())
        qis.save_figs_to_pdf(figs, file_name='covar_report', local_path=lp.get_output_path())
        plt.close('all')


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.RUN_REPORT)
