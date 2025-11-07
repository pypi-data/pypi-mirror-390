# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 12:48:16 2023

@author: pkiefer
"""

from emzed import MzType, RtType


def setup_targets_table(targets_table, kwargs):
    targets_table = targets_table.copy()
    _update_id_column(targets_table)
    _update_integration_limits_col(targets_table, **kwargs)
    _update_precursor_column(targets_table)
    _update_rt_columns(targets_table, **kwargs)
    _update_postfixes(targets_table, **kwargs)
    _update_baseline_subtraction(targets_table, **kwargs)
    return targets_table


def _update_precursor_column(targets_table):
    """
    MS level 1 tables do not require column precursor_mz. However, we us the
    columns mz and precursor_mz foe mixed MS levels to distinguish ms levels
    1 and 2. In case the column is missing we add the column

    """
    if "precursor_mz" not in targets_table.col_names:
        targets_table.add_column_with_constant_value(
            "precursor_mz", None, MzType, insert_before="mz"
        )


def _update_integration_limits_col(
    t, integration_limits_col="reduce_integration_window_to_peak_width", **kwargs
):
    if not integration_limits_col in t.col_names:
        t.add_column_with_constant_value(integration_limits_col, True, bool)


def _update_postfixes(targets_table, ms_data_type, **kwargs):
    if ms_data_type == "MS_Chromatogram":
        name2new = _col_names(ms_data_type)
        required = ["mz", "rtmin", "rtmax"]
        for name in required:
            new_name = name2new[name]
            targets_table.rename_columns(**{name: new_name})
        # optional for ms level2
        optionals = ["precursor_mz", "rt"]
        for name in optionals:
            if name in targets_table.col_names:
                targets_table.rename_columns(**{name: name2new[name]})


def _update_rt_columns(
    t,
    peak_search_window_size,
    peak_search_lower_limit="peak_search_window_min",
    peak_search_upper_limit="peak_search_window_max",
    **kwargs,
):
    _update_limits(t, peak_search_lower_limit, peak_search_upper_limit)
    if any([v in t.col_names for v in ["rtmin", "rtmax"]]):
        _overwrite_warning(t)
    t.add_or_replace_column(
        "rtmax",
        t[peak_search_upper_limit].if_not_none_else(t.rt + peak_search_window_size / 2),
        RtType,
        insert_after="rt",
    )
    t.add_or_replace_column(
        "rtmin",
        t[peak_search_lower_limit].if_not_none_else(t.rt - peak_search_window_size / 2),
        RtType,
        insert_after="rt",
    )


def _update_baseline_subtraction(t, subtract_baseline=False, **kwargs):
    if not "subtract_baseline" in t.col_names:
        t.add_column_with_constant_value("subtract_baseline", subtract_baseline, bool)


def _update_limits(t, *limits):
    for limit in limits:
        if not limit in t.col_names:
            t.add_column_with_constant_value(limit, None, RtType)


def _overwrite_warning(
    t,
    peak_search_window_size,
    peak_search_lower_limit,
    peak_search_upper_limit,
    cols=["rtmin", "rtmax"],
):
    upper = (
        len(set((peak_search_lower_limit, peak_search_upper_limit) - wset(t.col_names)))
        == 0
    )
    if set(cols).intersection(set(t.col_names)) == set(cols):
        mag1 = f"{peak_search_lower_limit} and {peak_search_upper_limit}!"
        msg2 = f"`rt - 0.5 * {peak_search_window_size}` and `rt +  0.5 * {peak_search_window_size}"
        msg_ = msg1 if upper else msg2
        msg = f"columns {', '.join(cols)} will be replaced by "
        msg = msg + msg_
        print(msg)


def _update_id_column(t):
    if not "id" in t.col_names:
        t.add_enumeration()


def _col_names(ms_data_type):
    pstfx = "_chromatogram"
    condition = ms_data_type == "MS_Chromatogram"
    d = {}
    d["mz"] = "mz" + pstfx if condition else "mz"
    d["rt"] = "rt" + pstfx if condition else "rt"
    d["rtmin"] = "rtmin" + pstfx if condition else "rtmin"
    d["rtmax"] = "rtmax" + pstfx if condition else "rtmax"
    d["area"] = "area" + pstfx if condition else "area"
    d["model"] = "model" + pstfx if condition else "model"
    d["rmse"] = "rmse" + pstfx if condition else "rmse"
    d["precursor_mz"] = "precursor_mz" + pstfx if condition else "precursor_mz"
    d["valid_model"] = "valid_model" + pstfx if condition else "valid_model"
    return d
