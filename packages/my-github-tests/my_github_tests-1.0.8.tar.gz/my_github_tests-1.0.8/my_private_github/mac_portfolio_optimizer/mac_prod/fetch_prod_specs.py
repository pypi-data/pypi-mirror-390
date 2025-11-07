"""
specs of production covar estimator
"""
import numpy as np
import pandas as pd
from typing import Union, Dict, Any

from optimalportfolios import CovarEstimator, LassoModel, LassoModelType, CovarEstimatorType
from mac_portfolio_optimizer import AssetClasses


def get_meta_params(saa_rebalancing_freq: str = 'QE') -> Dict[str, Any]:
    # group_max_turnover_constraint = pd.Series({0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0})

    group_max_turnover_constraint = pd.Series({0: 1.0,
                                               1: 0.25,
                                               2: 0.1,
                                               3: 0.1,
                                               4: 0.1,
                                               5: 0.1})
    """
    tracking_err_vol_constraint = 0.1
    group_tracking_err_vol_constraint = pd.Series({AssetClasses.LIQUIDITY.value: np.nan,
                                                   AssetClasses.FI.value: tracking_err_vol_constraint,
                                                   AssetClasses.EQ.value: tracking_err_vol_constraint,
                                                   AssetClasses.ALTS.value: tracking_err_vol_constraint})
    """

    group_tracking_err_vol_constraint = pd.Series({AssetClasses.LIQUIDITY.value: np.nan,
                                                   AssetClasses.FI.value:0.07,
                                                   AssetClasses.EQ.value: 0.07,
                                                   AssetClasses.ALTS.value: 0.07})

    group_tracking_err_vol_constraint = pd.Series({AssetClasses.LIQUIDITY.value: np.nan,
                                                   AssetClasses.FI.value: 0.0175,
                                                   AssetClasses.EQ.value: 0.025,
                                                   AssetClasses.ALTS.value: 0.0325})

    group_tracking_err_vol_constraint = pd.Series({AssetClasses.LIQUIDITY.value: np.nan,
                                                   AssetClasses.FI.value: 0.015,
                                                   AssetClasses.EQ.value: 0.03,
                                                   AssetClasses.ALTS.value: 0.03})

    group_tracking_err_vol_constraint = pd.Series({AssetClasses.LIQUIDITY.value: np.nan,
                                                   AssetClasses.FI.value: 0.015,
                                                   AssetClasses.EQ.value: 0.05,
                                                   AssetClasses.ALTS.value: 0.05})

    meta_params = dict(global_tracking_err_vol_constraint=None,
                       group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                       global_max_turnover_constraint=None,
                       group_max_turnover_constraint=group_max_turnover_constraint,
                       management_fee=0.02,
                       is_saa_benchmark_for_betas=True,
                       is_joint_saa_taa_covar=True,
                       rebalancing_costs=0.0,
                       saa_rebalancing_freq=saa_rebalancing_freq)
    return meta_params


def get_prod_covar_estimator(rebalancing_freq: str = 'ME',
                             apply_unsmoothing_for_pe: bool = True,
                             returns_freqs: Union[str, pd.Series] = 'ME',
                             nonneg: bool = True
                             ) -> CovarEstimator:

    lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO_CLUSTERS,
                             group_data=None,
                             demean=True,
                             reg_lambda=1e-5,  # 2.5*1e-5
                             span=36,
                             solver='ECOS_BB',
                             warmup_period=12,
                             exclude_zero_betas=False,
                             nonneg=nonneg)

    # set covar estimator
    if apply_unsmoothing_for_pe:
        num_lags_newey_west_dict = None
    else:
        num_lags_newey_west_dict = {'ME': 0, 'QE': 2}
    covar_estimator = CovarEstimator(covar_estimator_type=CovarEstimatorType.LASSO,
                                     lasso_model=lasso_model,
                                     factor_returns_freq='ME',
                                     rebalancing_freq=rebalancing_freq,  # taa rebalancing
                                     returns_freqs=returns_freqs,
                                     span=lasso_model.span,
                                     is_apply_vol_normalised_returns=False,
                                     squeeze_factor=0.0,
                                     residual_var_weight=1.0,
                                     span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span / 4},
                                     num_lags_newey_west_dict=num_lags_newey_west_dict
                                     )
    return covar_estimator
