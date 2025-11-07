import os
from .workflow import run_workflow, run_calibration, postprocess_result_table
from pathlib import Path
from .in_out import load_config, load_samples_from_folder, load_targets_table
from emzed import gui

#  folders
home = Path.home().as_posix()
here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


def run(show_description=True):
    show_workflow_description(show_description)
    targets_table, samples, config = _load_example_data()
    result = run_workflow(targets_table, samples, config)
    msg = "Do you want to inspect the results prior to processing steps"
    inspect = gui.ask_yes_no(msg)
    if inspect:
        gui.inspect(result)
    result = postprocess_result_table(result, config)
    samples_table, calibrants_table = _load_calibration_data()
    calibration_results = run_calibration(result, calibrants_table, samples_table)
    return postprocess_result_table(result, config, 1, calibration_results)


def _load_example_data():
    path = os.path.join(data_folder, "example.config.txt")
    config = load_config(path)
    samples = load_samples_from_folder(data_folder)
    path = os.path.join(data_folder, "example_peaks.table")
    targets_table = load_targets_table(path)
    return targets_table, samples, config


def _load_calibration_data():
    pass


def description(show_description):
    if not show_description:
        return
    # show decription
