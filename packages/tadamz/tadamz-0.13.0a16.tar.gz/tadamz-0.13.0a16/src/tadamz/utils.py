# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 08:17:17 2023

@author: pkiefer
"""

import numpy as np
from emzed import quantification
from emzed import RtType, MzType, PeakMap
from emzed.ms_data.peak_map import MSChromatogram, Chromatogram, ImmutablePeakMap
from scipy.signal import savgol_filter


def integrate_table(
    t, ms_data_type, ms_level=None, in_place=True, peak_shape_model="linear"
):
    assert ms_data_type in ["Spectra", "MS_Chromatogram"]

    if ms_data_type == "Spectra":
        t1 = quantification.integrate(
            t, peak_shape_model, ms_level=ms_level, in_place=in_place
        )
    else:
        t1 = quantification.integrate_chromatograms(
            t, peak_shape_model, ms_level=ms_level, in_place=in_place
        )
    return t1


def color_column_by_value(t, colname, value2color, default_color="#FFFFF"):
    """
    Adds color column `colname` where column values assign colors by dict `value2keys`

    Parameters
    ----------
    t : emzed.Table
        Table with column with requrired column 'colname' .
    colname : str
        Name of the column containing keys of dictionary.If the value is not
        key it retu
    value2color : dict
        Dictionary whith possble `colname` values as keys and
        color codes as corresponding dictionary values.
        The default is None.
    default_color : str, optional
        if column_value is not a dictionary key. the default color_color is
        applied to the cell. The defaukt is '#FFFFF' (white)
    Returns
    -------
    None.

    """
    if not "color" in t.col_names:
        t.add_column("color", [{}] * len(t), object, format_=None)
    t.add_or_replace_column(
        "color",
        t.apply(
            _update_color, colname, t[colname], t.color, value2color, default_color
        ),
        object,
        format_=None,
    )


def _update_color(key, value, colname2color, value2color, default_color="#FFFFF"):
    value = value2color.get(value)
    value = value if value is not None else default_color
    colname2color[key] = value
    return colname2color


# def update_filename(t):
#     t.add_or_replace_column(
#         "filename",
#         t.apply(lambda v: v.meta_data["filename"], t.peakmap),
#         str,
#         insert_after="peakmap",
#     )


def get_group_cols(t, group_col, sample_wise):
    if sample_wise:
        msg = "column `filename` is missing"
        assert "filename" in t.col_names, msg
        # update_filename(t)
        return (group_col, "filename")
    return (group_col,)


def get_smoothed(values):
    try:
        smoothed = savgol_filter(values, 7, 3)
        # we exclude negative intensity values
        smoothed[smoothed < 0] = 0
        return smoothed
    except:
        return values


def cleanup_join(t):
    """
    removes columns with same prefix and identical content after join in place.

    Parameters
    ----------
    t : Table
        DESCRIPTION.

    Returns
    -------
    None.

    """
    drop_cols = []
    common2index = _find_common_columns(t)
    for col, index in common2index:
        pstfx_col = col + "__" + index
        if set(zip(t[col], t[pstfx_col])) - set(zip(t[pstfx_col], t[col])) == set([]):
            drop_cols.append(pstfx_col)
    t.drop_columns(*drop_cols)
    _rename(t)


def _find_common_columns(t):
    with_pstfx = [name for name in t.col_names if "__" in name]
    wo_pstfx = set(t.col_names) - set(with_pstfx)
    common = set([name.split("__")[0] for name in with_pstfx]).intersection(wo_pstfx)
    return [name.split("__") for name in with_pstfx if name.split("__")[0] in common]


def _rename(t):
    for colname in t.col_names:
        name = colname.split("__")[0]
        postfixes = t.supported_postfixes([name])
        if len(postfixes) == 1 and postfixes[0]:
            t.rename_columns(**{colname: name})


def cleanup_last_join(t, keep_pstfx_cols_values=False):
    pstfx = _get_max_postfix(t)
    drop_cols = []
    common_prfx_cols = _find_common_pstfx_columns(t, pstfx)
    name2type = dict(zip(t.col_names, t.col_types))
    for col in common_prfx_cols:
        pstfx_col = col + pstfx
        type_ = name2type[col]
        if _compare_values(t, col, pstfx, type_):
            if keep_pstfx_cols_values:
                t.replace_column(col, t[pstfx_col], type_)
            drop_cols.append(pstfx_col)
    t.drop_columns(*drop_cols)
    _remove_pstfx(t, pstfx, common_prfx_cols)


def _find_common_pstfx_columns(t, pstfx):
    with_pstfx = [name for name in t.col_names if name.endswith(pstfx)]
    wo_pstfx = [name for name in t.col_names if not "__" in name]
    return set([name.split("__")[0] for name in with_pstfx]).intersection(wo_pstfx)
    # return [name.split("__") for name in with_pstfx if name.split("__")[0] in common]


def _get_max_postfix(t):
    pstfxs = set([name.split("__")[-1] for name in t.col_names if "__" in name])
    if len(pstfxs):
        return "__" + max(pstfxs, key=lambda v: int(v))


def _remove_pstfx(t, pstfx, common_cols):
    for col in t.col_names:
        if col.endswith(pstfx):
            new = col.split(pstfx)[0]
            if not new in common_cols:
                t.rename_columns(**{col: new})


def _compare_values(t, col, pstfx, type_):
    pstfx_col = col + pstfx
    simple_types = (float, int, str, RtType, MzType)
    if type_ in simple_types:
        return set(zip(t[col], t[pstfx_col])) - set(zip(t[pstfx_col], t[col])) == set(
            []
        )
    t.add_column(
        "comparison", t.apply(_compare, t[col], t[pstfx_col], ignore_nones=False), bool
    )
    equal = all(t.comparison.to_list())
    t.drop_columns("comparison")
    return equal


def _compare(item1, item2):
    # NOTE: OTHER DATA TYPES MIGHT BE REQUIRED!
    if item1 is None and item2 is None:
        return True
    if isinstance(item1, PeakMap) and isinstance(item2, PeakMap):
        return int(item1.unique_id == item2.unique_id)
    if isinstance(item1, ImmutablePeakMap) and isinstance(item2, ImmutablePeakMap):
        return int(item1.unique_id == item2.unique_id)
    if isinstance(item1, Chromatogram) and isinstance(item2, Chromatogram):
        c1 = np.all(item1.intensities == item2.intensities)
        c2 = np.all(item1.rts == item2.rts)
        return int(c1 and c2)
    if isinstance(item1, MSChromatogram) and isinstance(item2, MSChromatogram):
        c1 = np.all(item1.intensities == item2.intensities)
        c2 = np.all(item1.rts == item2.rts)
        c3 = item1.mz == item2.mz
        c4 = item1.precursor_mz == item2.precursor_mz
        return int(c1 and c2 and c3 and c4)
    return False


def format_result_table(
    t,
    compound_col="compound",
    amount_col="amount",
    unit_col="unit",
    ordered_columns=None,
    hided_columns=[],
):
    """
    returns result table in default column order with options for column order
    ansd hided columns

    Parameters
    ----------
    t : table
        DESCRIPTION.
    compound_col : str, optional
        Name of the compound column. The default is "compound".
    amount_col : TYPE, optional
        Name of the amount column. The default is "amount".
    unit_col : TYPE, optional
        Name of the unit column. The default is "unit".
    ordered_columns :iterable, optional
        a list of n first column names determining their order. All other
        columnas will be added after keeping current order. If ordered columns
        is None, the default column order is applied:
            [
               "id",
               compound_col,
               "sample_type",
               "sample_name",
               "precursor_mz_chromatogram",
               "mz_chromatogram",
               "rt_chromatogram",
               "peak_quality_score",
               "peak_coelutes",
               "area_chromatogram",
               "normalized_area_chromatogram",
               amount_nominal,
               amount_std,
               unit_col,
           ]
            The default is None.
    hided_columns : iterable, optional
        list of column names that will be hided when the table is expected
        with the table exploter. The default is [].

    Returns
    -------
    tabble
        edited result table.

    """
    if ordered_columns is None:
        ordered_columns = _default_columns_order(compound_col, amount_col, unit_col)
    _check_presence(
        t, "id", compound_col, "mz_chromatogram", "rt_chromatogram", "area_chromatogram"
    )
    _hide_columns(t, hided_columns)
    extract_cols = [col for col in ordered_columns if col in t.col_names]
    others = [col for col in t.col_names if col not in extract_cols]
    extract_cols.extend(others)
    return t.extract_columns(*extract_cols)


def _hide_columns(t, hided_columns):
    for column in hided_columns:
        t.set_col_format(column, None)


def _check_presence(t, *colnames):
    for colname in colnames:
        msg = f"column {colname} is missing in result_table"
        assert colname in t.col_names, msg


def _default_columns_order(compound_col, amount_col, unit_col):
    amount_nominal = amount_col + "_nominal"
    amount_std = amount_col + "_std"
    columns = [
        "id",
        compound_col,
        "sample_type",
        "sample_name",
        "precursor_mz_chromatogram",
        "mz_chromatogram",
        "rt_chromatogram",
        "peak_quality_score",
        "peak_coelutes",
        "area_chromatogram",
        "normalized_area_chromatogram",
        amount_nominal,
        amount_std,
        unit_col,
    ]
    return columns
