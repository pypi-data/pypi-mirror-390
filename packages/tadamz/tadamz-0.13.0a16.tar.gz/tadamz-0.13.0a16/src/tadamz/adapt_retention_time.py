# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:56:10 2023

@author: pkiefer
Concept
There are 2 approaches
1) via fit (in that case the alignment targets_table originates from a measurement)
2) from internal standard: The simplest approach: we select most important
peak based on internal standard: Problems of mass isomers;
-> solutions
The risk in case of several in

"""
import numpy as np
from emzed import RtType, Table
from emzed.quantification import integrate_chromatograms


######################################################
# Local adaptation


from scipy.signal import savgol_filter


def local_adjust(
    t,
    min_fwhm=2.0,
    integration_algorithm="linear",
    integration_limits_col="reduce_integration_window_to_peak_width",
):
    # _determine_shift(t)
    _set_windows(t, min_fwhm, "rt_chromatogram", integration_limits_col)
    integrate_chromatograms(t, integration_algorithm, in_place=True)
    t.add_or_replace_column(
        "rt_chromatogram",
        t.apply(determine_rt, t.model_chromatogram, t.rt_chromatogram),
        RtType,
    )


def _set_windows(
    t,
    min_fwhm=2.0,
    rt_value_column=None,
    integration_limits_col="reduce_integration_window_to_peak_width",
):
    integrate_chromatograms(t, "linear", in_place=True)
    params = [t.model_chromatogram, min_fwhm]
    params.append(t[rt_value_column]) if rt_value_column else params.append(None)
    t.add_column("temp", t.apply(adapt_window, *params), object)
    t.add_column("_rtmin", t.apply(lambda v: v[0], t.temp), RtType)
    t.add_column("_rtmax", t.apply(lambda v: v[1], t.temp), RtType)
    t.replace_column(
        "rtmin_chromatogram",
        (t._rtmin.is_not_none() & (t[integration_limits_col] == True)).then_else(
            t._rtmin, t.rtmin_chromatogram
        ),
        RtType,
    )
    t.replace_column(
        "rtmax_chromatogram",
        (t._rtmax.is_not_none() & (t[integration_limits_col] == True)).then_else(
            t._rtmax, t.rtmax_chromatogram
        ),
        RtType,
    )

    t.drop_columns("temp", "_rtmin", "_rtmax")


def adapt_window(model, min_fwhm, rt=None):
    rts, ints = model.graph()
    if not len(rts):
        return None, None
    smoothed = _get_smoothed(ints)
    rt_ = _determine_rt(rts, smoothed)
    rt = rt if rt_ is None else rt_
    if rt is None:
        return None, None
    fwhm = _determine_fwhm(rts, smoothed, rt, min_fwhm)
    f_asym = _determine_asymmetric_factor(rts, smoothed, rt)
    # factor 2.54 results from Gaussian distribution since 6 sigma cover 99.6 % of gaussiam peaka and
    # FWHM =2 * sqrt(2\ln 2) * sigma ~ 2.355 * sigma
    # 6/2.355 approx  2.54
    left_pos = np.argwhere(np.logical_and(rts >= rt - 2.54 * f_asym * fwhm, rts < rt))
    right_pos = np.argwhere(np.logical_and(rts <= rt + 2.54 / f_asym * fwhm, rts > rt))
    start = _min_value_pos(left_pos, smoothed, False)
    start = start if start else 0
    stop = _min_value_pos(right_pos, smoothed)
    stop = stop if stop else len(rts) - 1
    return rts[start], rts[stop]


def _min_value_pos(positions, intensities, rightside=True):

    if len(positions):
        i = np.where(intensities[positions] == min(intensities[positions]))
        index = 0 if rightside else -1
        return positions[i][index]


def determine_rt(model, rt):
    rts, ints = model.graph()
    if len(ints):
        smoothed = _get_smoothed(ints)
        rt = _determine_rt(rts, smoothed)
    return rt


def _get_smoothed(values):
    try:
        smoothed = savgol_filter(values, 7, 3)
        # we exclude negative intensity values
        smoothed[smoothed < 0] = 0
        return smoothed
    except:
        return values


def _determine_rt(rts, smoothed):
    i = np.where(smoothed == max(smoothed))[0]
    i = int((min(i) + max(i)) / 2)
    return rts[i]


def _determine_asymmetric_factor(rts, smoothed, rt):
    max_int = _determine_max_int(rt, rts, smoothed)
    pos = np.where(np.logical_and(smoothed >= 0.2 * max_int, smoothed <= max_int))[0]
    diff_pos = np.diff(pos)
    check = np.where(diff_pos > 1)[0] + 1
    blocks = np.split(pos, check)
    i = np.where(abs(rts - rt) == np.min(abs(rts - rt)))[0]
    for block in blocks:
        if i in block:
            left = len(block[block <= i])
            right = len(block[block >= i])
            # to avoid division by zero
            right = right if right else 1
            left = left if left else 1
            return left / right
    return 1.0


def _determine_fwhm(rts, smoothed, rt, min_fwhm=2.0):
    fwhm = min_fwhm
    max_int = _determine_max_int(rt, rts, smoothed)
    pos = np.where(np.logical_and(smoothed >= 0.5 * max_int, smoothed <= max_int))[0]
    diff_pos = np.diff(pos)
    check = np.where(diff_pos > 1)[0] + 1
    blocks = np.split(pos, check)
    i = np.where(abs(rts - rt) == np.min(abs(rts - rt)))[0]
    for block in blocks:
        if i in block:
            fwhm = rts[max(block)] - rts[min(block)]
    return fwhm if fwhm > min_fwhm else min_fwhm


def _determine_max_int(rt, rts, ints):
    diffs = abs(rts - rt)
    pos = np.where(diffs == min(diffs))
    return max(ints[pos])


def _determine_max_int(rt, rts, ints):
    diffs = abs(rts - rt)
    pos = np.where(diffs == min(diffs))
    return max(ints[pos])


# ___________________ coeluting peaks ____________________
# based on cosine similarity scoring


def adapt_rt_by_coeluting_peaks(
    t,
    group_id_column="compound",
    reference_column="is_coelution_reference_peak",
    only_use_ref_peaks=True,
    sample_wise=True,
    min_fwhm=2.0,
    **kwargs
):
    if len(t):
        t.add_enumeration("rowid")
        rid2algo = dict(zip(t.rowid, t.peak_shape_model_chromatogram))

        # integration_algorithm = t_.peak_shape_model_chromatogram.unique_value()
        temp_cols = "_rt_ref", "_fwhm_ref", "_ok", "_rtmin_ref", "_rtmax_ref", "rowid"
        _add_rt_ref_columns(
            t, reference_column, group_id_column, only_use_ref_peaks, sample_wise
        )
        t.add_column("_ok", (t.peak_coelutes == "ok").then_else(True, False), bool)
        t_ok = t.filter(t._ok)
        tables = [t_ok]
        t_crit = t.filter(t._ok == False)
        t.drop_columns(*temp_cols)
        _move_rt_windows(t_crit, "sgolay", min_fwhm)
        t_crit.replace_column(
            "peak_shape_model_chromatogram",
            t_crit.apply(rid2algo.get, t_crit.rowid),
            str,
        )
        for t_ in t_crit.split_by_iter("peak_shape_model_chromatogram"):
            algo = t_.peak_shape_model_chromatogram.unique_value()
            integrate_chromatograms(t_, algo, in_place=True)
            tables.append(t_)
        t = Table.stack_tables(tables)
        t.drop_columns(*temp_cols)
    return t


def _add_rt_ref_columns(
    t, reference_column, group_col, only_use_ref_peaks, sample_wise
):
    group_cols = [t[group_col]]
    if sample_wise:
        group_cols.append(t.filename)

    if only_use_ref_peaks:
        assert reference_column is not None
        t.add_column(
            "_rt_ref",
            t.group_by(*group_cols).aggregate(
                _get_ref_rt, t.rt_chromatogram, t[reference_column]
            ),
            RtType,
        )
        t.add_column(
            "_rtmin_ref",
            t.group_by(*group_cols).aggregate(
                _get_ref_rt, t.rtmin_chromatogram, t[reference_column]
            ),
            RtType,
        )
        t.add_column(
            "_rtmax_ref",
            t.group_by(*group_cols).aggregate(
                _get_ref_rt, t.rtmax_chromatogram, t[reference_column]
            ),
            RtType,
        )
    else:
        t.add_column(
            "_rt_ref", t.group_by(*group_cols).median(t.rt_chromatogram), RtType
        )
        t.add_column(
            "_rtmin_ref", t.group_by(*group_cols).median(t.rtmin_chromatogram), RtType
        )
        t.add_column(
            "_rtmax_ref", t.group_by(*group_cols).median(t.rtmax_chromatogram), RtType
        )
    t.add_column("_fwhm_ref", (t._rtmax_ref - t._rtmin_ref) / 4, float)


def _move_rt_windows(t, integration_algorithm, min_fwhm):
    t.replace_column(
        "rtmin_chromatogram",
        t.rtmin_chromatogram + t._rt_ref - t.rt_chromatogram,
        RtType,
    )
    t.replace_column(
        "rtmax_chromatogram",
        t.rtmax_chromatogram + t._rt_ref - t.rt_chromatogram,
        RtType,
    )

    integrate_chromatograms(t, "linear", in_place=True)
    _set_windows(t, min_fwhm, "_rt_ref")
    # bug fix
    # special case: zero len peaks: rmse calculation fails.
    # we apply linear instead
    try:
        integrate_chromatograms(t, integration_algorithm, in_place=True)
    except:
        integrate_chromatograms(t, "linear", in_place=True)
    t.add_or_replace_column(
        "rt_chromatogram",
        t.apply(determine_rt, t.model_chromatogram, t.rt_chromatogram),
        RtType,
    )


def _get_ref_rt(rts, references):
    rts_ = [rt for rt, ref in zip(rts, references) if ref]
    return np.mean(rts_)
