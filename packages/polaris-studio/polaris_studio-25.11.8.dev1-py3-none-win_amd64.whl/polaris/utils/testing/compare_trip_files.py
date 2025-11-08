# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from polaris.analyze.demand_report import add_mode_names, vmts, time_distribution, trips_by_mode, trips_by_type


def demand_comparison(trips_base: pd.DataFrame, trips_new: pd.DataFrame):
    if min(trips_new.shape[0], trips_base.shape[0]) == 0:
        logging.error("One of the Trips dataframes is empty")
        return

    trips_base = add_mode_names(trips_base)
    trips_new = add_mode_names(trips_new)

    rows = 6
    fig, axs = plt.subplots(rows, 2, figsize=(20, rows * 6), sharey=False)

    # Compares trips by mode
    _ = trips_by_mode(trips_base, cname="Base", ax=axs[0, 0], ax_table=axs[1, 0])
    _ = trips_by_mode(trips_new, cname="New", ax=axs[0, 1], ax_table=axs[1, 1])

    # Compares VMTs
    _ = vmts(trips_base, gpd.GeoDataFrame([]), axs[2, 0], name=" (Base)")
    _ = vmts(trips_new, gpd.GeoDataFrame([]), axs[2, 1], name=" (NEW)")

    # Compares trips by type
    _ = trips_by_type(trips_base, cname="Base", ax=axs[3, 0], ax_table=axs[4, 0])
    _ = trips_by_type(trips_new, cname="New", ax=axs[3, 1], ax_table=axs[4, 1])

    # Compare time distributions
    _ = time_distribution(trips_base, field_name="Base", ax=axs[5, 0])
    _ = time_distribution(trips_new, field_name="New", ax=axs[5, 0])

    return fig
