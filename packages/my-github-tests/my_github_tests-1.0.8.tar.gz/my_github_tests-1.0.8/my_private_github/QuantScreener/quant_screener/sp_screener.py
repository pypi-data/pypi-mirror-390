"""
bond universe screener
"""
import pandas as pd
import numpy as np
import qis as qis
import scipy.cluster.hierarchy as sch
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
from enum import Enum


FILE_NAME = 'PBA EQ'


class Universe(Enum):
    GLOBAL = 'global'
    SAMPLE = 'sample'
    NOV19 = 'NOV19'


@dataclass
class UniverseScreener:
    """
    data container for bond universe
    """
    prices: pd.DataFrame
    fundamentals: pd.DataFrame
    benchmarks: pd.DataFrame

    def __post_init__(self):
        self.prices = self.prices.asfreq('B', method='ffill')
        self.benchmarks = self.benchmarks.reindex(index=self.prices.index, method='ffill')

    def get_implied_vols(self) -> pd.Series:
        return self.fundamentals['implied_vol'].astype(float) / 100.0

    def compute_realised_volatility(self, span: int = 13, freq: str = 'W-WED', af: float = 52.0) -> pd.Series:
        # quarterly span for vol
        returns = qis.to_returns(prices=self.prices, freq=freq, drop_first=True, is_log_returns=True)
        vol = qis.compute_ewm_vol(data=returns, span=span, af=af)
        return vol.iloc[-1, :]

    def get_volatility(self, span: int = 52, freq: str = 'W-WED') -> pd.Series:
        implied = self.get_implied_vols()
        realised = self.compute_realised_volatility(span=span, freq=freq)
        realised = realised.reindex(index=implied.index)
        vol = pd.Series(np.where(np.isnan(implied.to_numpy()) == False, implied, realised), index=implied.index)
        return vol

    def estimate_r2_and_resid_corr(self, span: int = 52, freq: str = 'W-WED',
                                   cluster_threshold: float = 5.0
                                   ) -> pd.DataFrame:
        y = qis.to_returns(prices=self.prices, freq=freq, drop_first=True, is_log_returns=True)
        x = qis.to_returns(prices=self.benchmarks, freq=freq, drop_first=True, is_log_returns=True)
        ewm_linear_model = qis.EwmLinearModel(x=x, y=y)
        ewm_linear_model.fit(span=span, is_x_correlated=True)

        loadings = {}
        for factor in x.columns:
            loadings[factor] = ewm_linear_model.loadings[factor].iloc[-1, :]
        loadings = pd.DataFrame.from_dict(loadings, orient='columns')

        # estimate R^2
        r2_t = ewm_linear_model.get_model_ewm_r2(span=span)
        # qis.plot_time_series(df=r_2)
        r2 = r2_t.iloc[-1, :]  # .sort_values()
        residual_corr_pd, residual_avg_corr = ewm_linear_model.get_model_residuals_corrs(span=span)
        residual_corr_pd[np.isfinite(residual_corr_pd.to_numpy()) == False] = 0.0
        # sns.clustermap(residual_corr_pd)

        X = residual_corr_pd.to_numpy()
        Z = sch.ward(sch.distance.pdist(X))
        # sch.dendrogram(Z)
        clusters = sch.fcluster(Z, t=cluster_threshold, criterion='distance')
        clusters = pd.Series(clusters, index=self.prices.columns)
        print(f"number of clusters: {len(clusters.unique())}")

        df = pd.concat([loadings, r2.rename('r2'), residual_avg_corr.rename('resid corr'), clusters.rename('clusters')
                        ], axis=1)
        df = df.sort_values(by='r2')
        return df

    def compute_correlations(self, tickers: List[str], span: int = 52, freq: str = 'W-WED') -> pd.DataFrame:
        returns = qis.to_returns(prices=self.prices[tickers], freq=freq, drop_first=True, is_log_returns=True)
        corrs = qis.compute_ewm_covar(a=returns.to_numpy(), span=span, is_corr=True)
        corrs = pd.DataFrame(corrs, index=tickers, columns=tickers)
        return corrs

    def compute_top_stocks(self,
                           span: int = 52,
                           freq: str = 'W-WED',
                           vol_span: int = 13,
                           cluster_threshold: float = 5.0,
                           top_quantile: Optional[float] = 0.75
                           ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        compute correlation factors and vol factor
        take integrated scores on low rs, resid correlation and high vol vol
        """
        correlation_factors = self.estimate_r2_and_resid_corr(span=span, freq=freq, cluster_threshold=cluster_threshold)
        vols = self.get_volatility(span=vol_span, freq=freq).rename('implied_vol')

        # compute scores for all universe
        r2_score = qis.df_to_cross_sectional_score(1.0 - correlation_factors['r2'], is_sorted=True).rename('r2 score') # the more the better
        resid_corr = qis.df_to_cross_sectional_score(1.0 - correlation_factors['resid corr'], is_sorted=True).rename('resid corr score')  # the more the better
        vol = qis.df_to_cross_sectional_score(vols, is_sorted=True).rename('vol score')
        scores = pd.concat([r2_score, resid_corr, vol], axis=1)
        # select top subset
        if top_quantile is not None:
            top_scores = qis.select_top_integrated_scores(scores=scores, top_quantile=top_quantile).copy()
        else:
            top_scores = scores
        # merge outputs
        all_scores = pd.concat([correlation_factors, vols], axis=1).reindex(index=top_scores.index)
        top_scores = pd.concat([top_scores, all_scores], axis=1)
        # add correlations
        corrs = self.compute_correlations(tickers=top_scores.index.to_list(), span=span, freq=freq)
        return top_scores, corrs

    def compute_top_baskets(self, span: int = 52, freq: str = 'W-WED',
                            vol_span: int = 13,
                            cluster_threshold: float = 5.0,
                            top_quantile: Optional[float] = 0.75,
                            basket_size: int = 3
                            ) -> Tuple[Dict[int, List[str]], pd.DataFrame, pd.DataFrame]:
        top_scores, corrs = self.compute_top_stocks(span=span, freq=freq, vol_span=vol_span,
                                                    cluster_threshold=cluster_threshold, top_quantile=top_quantile)
        assets = corrs.columns.to_list()
        n_assets = len(assets)
        available_indices = np.full(n_assets, True)
        corrs_np = corrs.to_numpy()
        selected_baskets = {}
        for idx, asset in enumerate(corrs.columns):
            selected_assets_basket = []
            if available_indices[idx]:  # select it first to the basket
                selected_assets_basket.append(asset)
                available_indices[idx] = False
            #array_rank = np.argsort(corrs_np[:, idx]).argsort()  # ranks by smalleest corr
            #array_idx_rank = {array_rank[n]: n for n in np.arange(n_assets)}  # assign rank to idx
            #array_idx_rank = dict(sorted(array_idx_rank.items()))  # sort by rank
            array_idx_rank = np.argsort(corrs_np[:, idx])  # get indices of inreasing values
            # print(array_idx_rank)
            for ranked_idx in array_idx_rank:
                if available_indices[ranked_idx]:
                    selected_assets_basket.append(assets[ranked_idx])
                    available_indices[ranked_idx] = False
                if len(selected_assets_basket) == basket_size:
                    selected_baskets[idx+1] = selected_assets_basket
                    break
            if np.all(available_indices == False):  # all assets are taken
                break
            # print(f"idx={idx}: {selected_assets_basket}")

        return selected_baskets, top_scores, corrs

    def compute_top_baskets_min_pairs(self,
                                      span: int = 52,
                                      freq: str = 'W-WED',
                                      vol_span: int = 13,
                                      cluster_threshold: float = 5.0,
                                      top_quantile: Optional[float] = 0.75,
                                      basket_size: int = 3,
                                      max_number_inclusions: int = 3
                                      ) -> Tuple[Dict[int, List[str]], pd.DataFrame, pd.DataFrame]:
        """
        compute list of top stocks and their pairwise correlation
        """
        top_scores, corrs = self.compute_top_stocks(span=span, freq=freq, vol_span=vol_span,
                                                    cluster_threshold=cluster_threshold, top_quantile=top_quantile)
        corrs_np = corrs.to_numpy()
        corr_pairs = {}
        # collect corrs into a series
        for row, asset1 in enumerate(corrs.columns):
            for column, asset2 in enumerate(corrs.columns):
                if column > row:
                    corr_pairs[f"{asset1}-{asset2}"] = pd.Series((asset1, asset2,
                                                                  top_scores.loc[asset1, 'clusters'], top_scores.loc[asset2, 'clusters'],
                                                                  corrs_np[row, column]),
                                                                 index=['asset1', 'asset2', 'cluster1', 'cluster2', 'corr'])

        # sort on last value in tuple
        corr_pairs = pd.DataFrame.from_dict(corr_pairs, orient='index').sort_values(by='corr')
        # remove pairs of stocks from the same
        same_cluster = corr_pairs['cluster1'] == corr_pairs['cluster2']
        corr_pairs = corr_pairs.loc[same_cluster == False, :]

        selected_assets = {}  # we count selected assets and and how many times they are included
        n_assets = len(corrs.columns)
        n_pairs = len(corr_pairs.index)
        available_indices = np.full(n_pairs, True)
        selected_baskets = {}
        next_basket_idx = 1

        def check_inclusion_capacity(asset: str) -> bool:
            if asset not in selected_assets.keys():
                can_be_included = True
            else:
                if selected_assets[asset] < max_number_inclusions:
                    can_be_included = True
                else:
                    can_be_included = False
            return can_be_included

        def select_asset(asset: str) -> None:
            if asset in selected_assets.keys():
                selected_assets[asset] += 1
            else:
                selected_assets[asset] = 1

        for idx, record in enumerate(corr_pairs.to_dict('records')):  #  to_dict('records') generates list of dict
            selected_assets_basket = []
            selected_assets_clusters = [] # do not include stocks from the same cluster
            if available_indices[idx]:  # select the pair to the basket if both assets didn't enter existing baskets
                asset1, asset2, cluster1, cluster2 = record['asset1'], record['asset2'], record['cluster1'], record['cluster2']
                if check_inclusion_capacity(asset1) and check_inclusion_capacity(asset2):
                    selected_assets_basket.append(asset1)
                    select_asset(asset1)
                    selected_assets_clusters.append(cluster1)
                    selected_assets_basket.append(asset2)
                    select_asset(asset2)
                    selected_assets_clusters.append(cluster2)
                    available_indices[idx] = False

                # look for next fill
                for idx1 in np.arange(0, n_pairs):  # selet the tird asset if it didn't entered existing assets
                    if available_indices[idx1]:
                        asset1, asset2, cluster1, cluster2 = corr_pairs.iloc[idx1, 0], corr_pairs.iloc[idx1, 1],\
                                                             corr_pairs.iloc[idx1, 2], corr_pairs.iloc[idx1, 3]
                        if check_inclusion_capacity(asset1) and cluster1 not in selected_assets_clusters:
                            selected_assets_basket.append(asset1)
                            select_asset(asset1)
                            selected_assets_clusters.append(cluster1)
                            available_indices[idx1] = False
                            if len(selected_assets_basket) == basket_size:
                                selected_baskets[next_basket_idx] = selected_assets_basket
                                next_basket_idx += 1
                                break
                        if check_inclusion_capacity(asset2) and cluster2 not in selected_assets_clusters:
                            selected_assets_basket.append(asset2)
                            select_asset(asset2)
                            selected_assets_clusters.append(cluster2)
                            available_indices[idx1] = False
                            if len(selected_assets_basket) == basket_size:
                                selected_baskets[next_basket_idx] = selected_assets_basket
                                next_basket_idx += 1
                                break
            if len(selected_assets) == n_assets or np.all(available_indices == False):  # all assets are taken
                break
        return selected_baskets, top_scores, corrs

    def create_baskets_outputs(self, selected_baskets: Dict[int, List[str]],
                               top_scores: pd.DataFrame,
                               corrs: pd.DataFrame
                               ) -> pd.DataFrame:
        df_tickers = {}
        df_names = {}
        impled_vols = {}
        asset_corrs = {}
        industry_sector = {}
        id_isin = {}
        clusters = {}
        column_names = [f"Asset {n+1}" for n in np.arange(len(selected_baskets[list(selected_baskets.keys())[0]]))]
        for idx, basket in selected_baskets.items():
            df_tickers[f"basket {idx}"] = pd.Series(basket, index=column_names)
            rename_map = dict(zip(basket, column_names))
            df_names[f"basket {idx}"] = self.fundamentals.loc[basket, 'name'].rename(rename_map)
            impled_vols[f"basket {idx}"] = self.fundamentals.loc[basket, 'implied_vol'].rename(rename_map)
            industry_sector[f"basket {idx}"] = self.fundamentals.loc[basket, 'sector'].rename(rename_map)
            id_isin[f"basket {idx}"] = self.fundamentals.loc[basket, 'isin'].rename(rename_map)
            clusters[f"basket {idx}"] = top_scores.loc[basket, 'clusters'].rename(rename_map)
            asset_corrs[f"basket {idx}"] = pd.Series(dict(corr_1_2=corrs.loc[basket[0], basket[1]],
                                                          corr_1_3=corrs.loc[basket[0], basket[2]],
                                                          corr_2_3=corrs.loc[basket[1], basket[2]]))

        df_tickers = pd.DataFrame.from_dict(df_tickers, orient='index')
        df_names = pd.DataFrame.from_dict(df_names, orient='index')
        impled_vols = pd.DataFrame.from_dict(impled_vols, orient='index')
        asset_corrs = pd.DataFrame.from_dict(asset_corrs, orient='index')
        industry_sector = pd.DataFrame.from_dict(industry_sector, orient='index')
        id_isin = pd.DataFrame.from_dict(id_isin, orient='index')
        clusters = pd.DataFrame.from_dict(clusters, orient='index')
        dfs = {'BBG Tickers': df_tickers, 'Names': df_names, 'Implied vols': impled_vols,
               'Correlations': asset_corrs,
               'Sector': industry_sector, 'ISIN': id_isin, 'Clusters': clusters}
        dfs = pd.concat(dfs, axis=1)
        return dfs


def load_universe_screener(local_path: str,
                           universe: Universe = Universe.SAMPLE,
                           file_name: str = FILE_NAME
                           ) -> UniverseScreener:
    dataset_keys = [f"{universe.value}_price", f"{universe.value}_fundamentals", 'benchmark_prices']
    dfs = qis.load_df_dict_from_excel(file_name=file_name, dataset_keys=dataset_keys, local_path=local_path)

    prices = dfs[f"{universe.value}_price"].asfreq('B', method='ffill').ffill()
    fundamentals = dfs[f"{universe.value}_fundamentals"]
    benchmarks = dfs[f"benchmark_prices"].asfreq('B', method='ffill').ffill()

    fundamentals = fundamentals.reindex(index=prices.columns)
    universe_screener = UniverseScreener(prices=prices, fundamentals=fundamentals, benchmarks=benchmarks)
    return universe_screener


class UnitTests(Enum):
    RUN_UNIVERSE = 1
    CREATE_BASKETS = 2
    CREATE_BASKETS2 = 3


def run_unit_test(unit_test: UnitTests):

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    import matplotlib.pyplot as plt
    import seaborn as sns
    local_path = f"C://Users//artur//OneDrive//analytics//qdev//resources//basket_screener//"
    # local_path = f"C://Users//uarts//Python//quant_strats//resources//basket_screener//"

    screener = load_universe_screener(local_path=local_path, universe=Universe.NOV19)

    if unit_test == UnitTests.RUN_UNIVERSE:
        implied = screener.get_implied_vols().rename('Implied Vol')
        realised = screener.compute_realised_volatility().rename('Realised Vol')
        df = pd.concat([realised, implied], axis=1).dropna()
        with sns.axes_style('darkgrid'):
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            qis.plot_scatter(df=df,
                             full_sample_order=1,
                             fit_intercept=False,
                             title='Implied volatility vs Realised volatility',
                             alpha_format='{0:+0.2%}',
                             ax=ax)

    elif unit_test == UnitTests.CREATE_BASKETS:
        # selected_baskets, top_scores, corrs = screener.compute_top_baskets(top_quantile=0.50, cluster_threshold=7.0)
        selected_baskets, top_scores, corrs = screener.compute_top_baskets_min_pairs(top_quantile=0.44, cluster_threshold=7.0)
        for key, value in selected_baskets.items():
            print(f"basket {key}: {value}")

        baskets = screener.create_baskets_outputs(selected_baskets=selected_baskets, top_scores=top_scores, corrs=corrs)
        correlation_factors = screener.estimate_r2_and_resid_corr(cluster_threshold=7.0)
        data = dict(baskets=baskets, corrs=corrs, top_scores=top_scores, correlation_factors=correlation_factors)
        qis.save_df_to_excel(data=data, file_name='selected_baskets_3', local_path=local_path, add_current_date=True)

    elif unit_test == UnitTests.CREATE_BASKETS2:
        selected_baskets, top_scores, corrs = screener.compute_top_baskets_min_pairs(top_quantile=None, cluster_threshold=1)
        sample_baskets = screener.create_baskets_outputs(selected_baskets=selected_baskets, top_scores=top_scores, corrs=corrs)
        print(sample_baskets)
        qis.save_df_to_excel(sample_baskets, file_name='sample_baskets', local_path=local_path, add_current_date=True)

    plt.show()


if __name__ == '__main__':

    unit_test = UnitTests.CREATE_BASKETS2

    is_run_all_tests = False
    if is_run_all_tests:
        for unit_test in UnitTests:
            run_unit_test(unit_test=unit_test)
    else:
        run_unit_test(unit_test=unit_test)
