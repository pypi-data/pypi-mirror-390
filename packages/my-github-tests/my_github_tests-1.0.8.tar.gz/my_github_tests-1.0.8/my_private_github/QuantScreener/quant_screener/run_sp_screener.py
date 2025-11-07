"""
run screener on the fly
"""

import pandas as pd
import qis as qis
from typing import List, Tuple
from enum import Enum
from quant_screener.sp_screener import UniverseScreener
from create_universe_data import fetch_universe_data_for_tickers


class UnitTests(Enum):
    CREATE_BACKETS_FROM_LIST = 1


def run_unit_test(unit_test: UnitTests):

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    import matplotlib.pyplot as plt
    import seaborn as sns
    local_path = f"C://Users//artur//OneDrive//analytics//qdev//resources//basket_screener//"
    # local_path = f"C://Users//uarts//Python//quant_strats//resources//basket_screener//"

    if unit_test == UnitTests.CREATE_BACKETS_FROM_LIST:

        tickers = ['NVDA US Equity',
                   'ADBE US Equity',
                   'SMH US Equity',
                   'SOXX US Equity',
                   'XBI US Equity',
                   'META US Equity',
                   'MC FP Equity',
                   'AMZN US Equity',
                   'ELV US Equity',
                   'TMO US Equity',
                   'GOOG US Equity',
                   'HSY US Equity',
                   'MSFT US Equity',
                   'PEP US Equity']

        prices, fundamentals, benchmarks = fetch_universe_data_for_tickers(tickers=tickers)

        screener = UniverseScreener(prices=prices, fundamentals=fundamentals, benchmarks=benchmarks)

        selected_baskets, top_scores, corrs = screener.compute_top_baskets_min_pairs(span=104,
                                                                                     freq='W-WED',
                                                                                     vol_span=13,
                                                                                     top_quantile=None,
                                                                                     cluster_threshold=1,
                                                                                     max_number_inclusions=3
                                                                                     )

        sample_baskets = screener.create_baskets_outputs(selected_baskets=selected_baskets, top_scores=top_scores,
                                                         corrs=corrs)
        print(sample_baskets)
        sample_baskets.to_clipboard()
        qis.save_df_to_excel(sample_baskets, file_name='sample_baskets', local_path=local_path, add_current_date=True)

    plt.show()


if __name__ == '__main__':

    unit_test = UnitTests.CREATE_BACKETS_FROM_LIST

    is_run_all_tests = False
    if is_run_all_tests:
        for unit_test in UnitTests:
            run_unit_test(unit_test=unit_test)
    else:
        run_unit_test(unit_test=unit_test)
