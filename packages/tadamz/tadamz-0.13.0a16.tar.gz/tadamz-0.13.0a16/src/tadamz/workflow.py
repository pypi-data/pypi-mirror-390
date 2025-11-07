# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 09:56:27 2023

@author: pkiefer
"""

from .processing_steps import ProcessingSteps as _PS
from .processing_steps import PostProcessResult as _PPR

# suppress warnings in console output
import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")


def run_workflow(
    targets_table,
    samples,
    config,
    calibration_results=None,
    sample_table=None,
    std_isotop_dist_table=None,
):
    """
    main function of tadamz. Executes processing steps defined in config.

    Parameters
    ----------
    targets_table : Table
        table defining peaks amd peak specific parameters for different processing
        steps.
    samples : str, PeakMap
        iterable of absolute file paths or of PeakMaps.
    config : dict
        dictionary defining processing steps and processing step specific parametwer settings.
        Moreover it allows definition of user specific column names for provided samples
    calibration_results : table, optional
        Table containing calibration results from tadamt.run_calibration. The default is None.
    sample_table : table, optional
        Maps sample file name with sample name and the sample type (Blank, Sample, QC, Calibrant).
        The default is None.
    std_isotop_dist_table : table, optional
        Contains measured isotoppologue distruibution of the internal standard.  If provided and
        the isotopologue overly correction is applied, correction of natural isotoplogues and
        of the internal standard are taken into account for the correction
        The default is None.

    Returns
    -------
    table
        result table containing integrated and processes peaks of all samples.

    """
    wf = _PS(
        targets_table,
        samples,
        config,
        calibration_results,
        sample_table,
        std_isotop_dist_table,
    )
    for step in wf.config["processing_steps"]:
        try:
            process = wf.__getattribute__(step)
        except AttributeError:
            print(
                f"""
                  WARNING
                  processing step `{step}` does not exist!
                  STEP will be skipped"""
            )
        process()
    return wf.result


def postprocess_result_table(
    result,
    config,
    postprocess_id=0,
    calibration_results=None,
    std_isotop_dist_table=None,
    process_only_tracked_changes=False,
    splitting_cols=["filename", "compound"],
):
    """
    Executes re-/post- processing  of the tadamz result table.

    Parameters
    ----------
    result : TYPE
        DESCRIPTION.
    config : TYPE
        DESCRIPTION.
    postprocess_id, int
     index of the posprocessing step listed in config
    calibrants_table, Table
      tadamz calibration result table. It is required for absolute quantification-
      The default is None
    std_isotop_dist_table, Table
      The default is None
    process_only_tracked_changes, Bool
      If True only rows grouped by splitting_cols, which contain tracked changes
      will be posprocessed. The default value is None
     splitting_cols, iterable
         Subdivides the result table into subtables with same values for all
         splitting cols. The default value is ["filename", "compound"]

    Returns
    -------
    Table
        The post-processed result table

    """
    msg = f"{postprocess_id} exceeds number of postprocessings"
    assert postprocess_id < len(config["postprocessings"]), msg
    post = config["postprocessings"][postprocess_id]
    wf = _PPR(
        result,
        config,
        calibration_results,
        std_isotop_dist_table,
        process_only_tracked_changes,
        splitting_cols=splitting_cols,
    )
    processing_steps = wf.config[post]
    _track_change_applicable(process_only_tracked_changes, processing_steps)
    for step in processing_steps:
        try:
            process = wf.__getattribute__(step)
        except AttributeError:
            print(
                f"""
                  WARNING
                  processing step `{step}` does not exist!
                  STEP will be skipped"""
            )
        if process_only_tracked_changes:
            msg = f"""{step} cannot be processed as tracked_change only since
            subset reprocessing is only possible when the step has already 
            been applied to the table. To apply {step} to the result table
            set `process_only_tracked_changes` to False. 
            """
            assert step in result.meta_data["applied_processing_steps"], msg
        process()
    wf.merge_reprocessed()
    return wf.result


def run_calibration(result_table, calibrants_table, sample_table, config):
    """
    Determines calibration curves for all compounds defined in calibrants table

    Parameters
    ----------
    result_table : table
        table resulting tadamz processing.it
    calibrants_table : table
        Defines compound amounts of calibrants with
        mandatory column sample_name, amount_col, unit. Optional columns:
        - `calibration_model_name`: compound specific calibrartion models
        (linear, quadratic)
        - `calibration_weight` compound specific weights for least square fitting
        (none, 1/x, 1/x^2, 1/s^2)
    sample_table : table
        Maps sample file name with sample name and the sample type (Blank, Sample, QC, Calibrant).
    config : dict
        config['calibrate'] defines calibration parameters

    Returns
    -------
    table
        results table with compound specific calibration_models.

    """
    return _PS.calibrate(result_table, calibrants_table, sample_table, config)


def _track_change_applicable(process_only_tracked_changes, processing_steps):
    if "pq_normalize_peaks" in processing_steps and process_only_tracked_changes:
        msg = """Correct reprocessing of `pq_normalize peaks` requires 
        `process_only_tracked_changes` to be set to `False`. For correct 
        results apply separate processing step to the complete result table table"""
        assert False, msg
