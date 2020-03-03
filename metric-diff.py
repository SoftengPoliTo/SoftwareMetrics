#!/usr/bin/env python3

"""metric-diff

Find differences in metrics produced by different tools
"""

import argparse
import enum
import json
import logging
import os
import sys
import typing as T

from exit_codes import ExitCode, log_conf, log_debug, log_err


class Metrics(enum.Enum):
    """List of metrics."""

    def __str__(self) -> str:
        return self.value

    CC = "CC"
    SLOC = "SLOC"
    LLOC = "LLOC"
    CLOC = "CLOC"
    HALSTEAD = "HALSTEAD"
    CK = "CK"


class CompareMetrics:
    """Compare metrics."""

    def __init__(
        self,
        first_json_filename: str,
        second_json_filename: str,
        first_json_data: T.Dict[str, T.Any],
        second_json_data: T.Dict[str, T.Any],
    ) -> None:

        self.first_json_filename = first_json_filename
        self.second_json_filename = second_json_filename
        self.first_json_data = first_json_data
        self.second_json_data = second_json_data

        self.metrics_json = {
            Metrics.CC: "CC",
            Metrics.SLOC: "Lines",
            Metrics.LLOC: "LOC",
            Metrics.CLOC: "CLOC",
            Metrics.HALSTEAD: "Halstead",
            Metrics.CK: "C&K",
        }

    def compare(self, metrics: T.List[Metrics]) -> None:
        for m in metrics:
            metric_as_string = str(m)
            json_metric = self.metrics_json.get(m)
            metric_first_file = self.first_json_data.get(json_metric, None)
            metric_second_file = self.second_json_data.get(json_metric, None)

            if not metric_first_file:
                log_err(
                    "\t{} metric not found in {}",
                    ExitCode.METRIC_NOT_FOUND,
                    metric_as_string,
                    self.first_json_filename,
                )

            if not metric_second_file:
                log_err(
                    "\t{} metric not found in {}",
                    ExitCode.METRIC_NOT_FOUND,
                    metric_as_string,
                    self.second_json_filename,
                )

            if metric_first_file != metric_second_file:
                log_err(
                    "\n\n{} metric is different\n\n"
                    "First file: {}\n"
                    "Second file: {}",
                    ExitCode.DIFFERENT_METRIC_VALUE,
                    metric_as_string,
                    metric_first_file,
                    metric_second_file,
                )


def check_metrics(metrics: T.Optional[T.List[str]]) -> T.List[Metrics]:
    """Check metrics inserted by the user."""

    if not metrics:
        return [m for m in Metrics]

    metrics_as_str = [str(m) for m in Metrics]
    check = [Metrics(metric) for metric in metrics if metric in metrics_as_str]
    if check:
        return check

    return [m for m in Metrics]


def run_comparison(
    first_json_file: str, second_json_file: str, metrics: T.List[Metrics]
) -> None:
    """Run metrics comparison."""

    with open(first_json_file, "r") as first_json:
        first_json_data = json.load(first_json)

    with open(second_json_file, "r") as second_json:
        second_json_data = json.load(second_json)

    diff = CompareMetrics(
        first_json_file, second_json_file, first_json_data, second_json_data
    )

    diff.compare(metrics)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="This tool compares metrics produced by others software "
        "and saved as json files",
        epilog="The manual and the source code of this program can be found on"
        " GitHub at https://github.com/SoftengPoliTo/SoftwareMetrics",
    )

    # Optional args
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store_true",
        help="Increase output verbosity, useful for debugging purposes",
    )

    # Args
    parser.add_argument(
        "-m",
        "--metrics",
        type=str,
        nargs="*",
        required=True,
        help="List of metrics to be compared",
    )

    parser.add_argument(
        "-f",
        "--files",
        metavar="FILE.json",
        type=str,
        nargs=2,
        required=True,
        help="Json files to compare",
    )

    args = parser.parse_args()

    # If the -v option is enabled, the program is in debug mode
    log_conf(args.verbosity)
    log_debug("\targs={}", vars(args))

    # Check json files inserted by the user
    def check_json_name(name):
        if not os.path.isfile(name):
            log_err("\t{} is not a valid file.", ExitCode.WRONG_FILES, name)

    check_json_name(args.files[0])
    check_json_name(args.files[1])

    # Check metrics inserted by the user
    metrics = check_metrics(args.metrics)

    # Run comparison
    run_comparison(args.files[0], args.files[1], metrics)


if __name__ == "__main__":
    main()
