# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 08:58:37 2023

@author: pkiefer
"""

import os
import pytest
import emzed
from src.tadamz import extract_peaks_from_chromatograms as epc
from src.tadamz import extract_peaks as ep
from src.tadamz import in_out

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def config_srm():
    config = {
        "integration_algorithm": "linear",
        "precursor_column": "precursor_mz",
        "precursor_mz_tol": 0.5,
        "mz_tol_abs": 0.5,
        "mz_tol_rel": 0.0,
        "ms_data_type": "MS_Chromatogram",
        "peak_search_window_size": 25.0,
    }
    return config


@pytest.fixture
def srm():
    path = os.path.join(here, "data/mrm_data_large.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def pt_srm():
    path = os.path.join(here, "data/peptide_table.xlsx")
    pt = in_out.load_targets_table(path)
    kwargs = {"ms_data_type": "MS_Chromatogram", "peak_search_window_size": 25.0}
    pt = ep.setup_targets_table(pt, kwargs)
    return pt


def test_extract_peaks_from_chromatogram_0(pt_srm, srm, config_srm, regtest):
    print(pt_srm.col_names)
    t = epc.add_chromatograms_to_targets_table(pt_srm, srm, config_srm)
    print(t, file=regtest)


def test_extract_peaks_from_chromatogram_1(pt_srm, srm, config_srm):
    t = epc.add_chromatograms_to_targets_table(pt_srm, srm, config_srm)
    assert len(set(t.id)) == len(t.id.to_list())


def test_extract_peaks_from_chromatogram_2(pt_srm, srm, config_srm):
    t = epc.add_chromatograms_to_targets_table(pt_srm, srm, config_srm)
    assert len(t) == len(pt_srm)
