#!/usr/bin/env python3

"""metric-diff

Find differences in metrics produced by different tools
"""

import argparse
import enum
import json
import logging
import math
import os
import sys
import typing as T

from exit_codes import ExitCode, log_conf, log_debug, log_err

# Metric value type
M = T.TypeVar("M", int, float)


def check_missing_field(condition: T.Any, field: str, filename: str) -> None:
    """Check missing field"""

    if not condition:
        log_err(
            "\n\n{} does not have the '" + field + "' field",
            ExitCode.PROGRAMMING_ERROR,
            filename,
        )


class Metrics(enum.Enum):
    """List of metrics."""

    def __str__(self) -> str:
        return self.value

    CC = "CC"
    SLOC = "SLOC"
    LOC = "LOC"
    LLOC = "LLOC"
    CLOC = "CLOC"
    HALSTEAD = "HALSTEAD"


class CompareMetrics:
    """Compare metrics."""

    def __init__(
        self,
        first_json_filename: str,
        second_json_filename: str,
        first_json_data: T.Dict[str, T.Any],
        second_json_data: T.Dict[str, T.Any],
    ) -> None:

        self.first_json_filename = os.path.basename(first_json_filename)
        self.second_json_filename = os.path.basename(second_json_filename)
        self.first_json_data = first_json_data
        self.second_json_data = second_json_data

        self.metrics_json = {
            Metrics.CC: "CC",
            Metrics.SLOC: "SLOC",
            Metrics.LOC: "LOC",
            Metrics.LLOC: "LLOC",
            Metrics.CLOC: "CLOC",
            Metrics.HALSTEAD: "Halstead",
        }

    def compare_global_metrics(self, metrics: T.List[Metrics]) -> None:
        print("\nComparing global metrics...\n")
        for m in metrics:
            self._compare_metrics(
                self.first_json_data, self.second_json_data, m
            )

    def compare_file_metrics(self, metrics: T.List[Metrics]) -> None:
        print("\nComparing file metrics...\n")
        for m in metrics:
            check_missing_field(
                self.first_json_data["files"],
                "files",
                self.first_json_filename,
            )

            check_missing_field(
                self.second_json_data["files"],
                "files",
                self.second_json_filename,
            )

            for file_one, file_two in zip(
                self.first_json_data["files"], self.second_json_data["files"]
            ):
                self._compare_metrics(file_one, file_two, m)

    def compare_function_metrics(self, metrics: T.List[Metrics]) -> None:
        print("\nComparing function metrics...\n")
        for m in metrics:

            for file_one, file_two in zip(
                self.first_json_data["files"], self.second_json_data["files"]
            ):
                check_missing_field(
                    file_one["functions"],
                    "functions",
                    self.first_json_filename,
                )

                check_missing_field(
                    file_two["functions"],
                    "functions",
                    self.second_json_filename,
                )

                for function_one, function_two in zip(
                    file_one["functions"], file_two["functions"]
                ):
                    self._compare_metrics(function_one, function_two, m)

    def _compare_metrics(
        self,
        dict_one: T.Dict[str, T.Any],
        dict_two: T.Dict[str, T.Any],
        metric: Metrics,
    ) -> None:

        # Get metric
        json_metric = self.metrics_json.get(metric)

        metric_first_file = dict_one.get(json_metric, None)
        metric_second_file = dict_two.get(json_metric, None)

        # Compare metrics
        self._compare_two_metric(
            metric_first_file, metric_second_file, str(metric)
        )

    def _compare_two_metric(
        self,
        metric_first_file: T.Optional[int],
        metric_second_file: T.Optional[int],
        metric_as_string: str,
    ) -> None:

        if metric_first_file is None:
            log_err(
                "\n\n{} metric not found in {}",
                ExitCode.METRIC_NOT_FOUND,
                metric_as_string,
                self.first_json_filename,
            )

        if metric_second_file is None:
            log_err(
                "\n\n{} metric not found in {}",
                ExitCode.METRIC_NOT_FOUND,
                metric_as_string,
                self.second_json_filename,
            )

        if self._check_metrics_types(metric_first_file, metric_second_file):
            log_err(
                "\n\n{} metric is different\n\n" "{}: {}\n" "{}: {}",
                ExitCode.DIFFERENT_METRIC_VALUE,
                metric_as_string,
                self.first_json_filename,
                metric_first_file,
                self.second_json_filename,
                metric_second_file,
            )

    def _check_metrics_types(
        self, metric_one: T.Any, metric_two: T.Any
    ) -> bool:
        if type(metric_one) is int:
            return metric_one != metric_two
        elif type(metric_one) is float:
            return not math.isclose(metric_one, metric_two, rel_tol=1e-6)
        else:
            for halstead_one, halstead_two in zip(
                metric_one.values(), metric_two.values()
            ):
                if type(halstead_one) is int:
                    return halstead_one != halstead_two
                else:
                    return not math.isclose(
                        halstead_one, halstead_two, rel_tol=1e-6
                    )

        return True


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
    first_json_file: str,
    second_json_file: str,
    metrics: T.List[Metrics],
    enable_global: bool,
    enable_files: bool,
    enable_functions: bool,
) -> None:
    """Run metrics comparison."""

    with open(first_json_file, "r") as first_json:
        first_json_data = json.load(first_json)

    with open(second_json_file, "r") as second_json:
        second_json_data = json.load(second_json)

    diff = CompareMetrics(
        first_json_file, second_json_file, first_json_data, second_json_data
    )

    print("Check", *metrics, "metric" if len(metrics) == 1 else "metrics")

    if enable_global:
        diff.compare_global_metrics(metrics)

    if enable_files:
        diff.compare_file_metrics(metrics)

    if enable_functions:
        diff.compare_function_metrics(metrics)

    if not (enable_global or enable_files or enable_functions):
        diff.compare_global_metrics(metrics)

    print("Done. No differences between analyzed metrics.")


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

    parser.add_argument(
        "-g",
        "--globals",
        action="store_true",
        help="Compare json files global metrics",
    )

    parser.add_argument(
        "-f",
        "--files",
        action="store_true",
        help="Compare json files file metrics",
    )

    parser.add_argument(
        "-fu",
        "--functions",
        action="store_true",
        help="Compare json files function metrics",
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
        "-i",
        "--inputs",
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

    check_json_name(args.inputs[0])
    check_json_name(args.inputs[1])

    # Check metrics inserted by the user
    metrics = check_metrics(args.metrics)

    # Run comparison
    run_comparison(
        args.inputs[0],
        args.inputs[1],
        metrics,
        args.globals,
        args.files,
        args.functions,
    )


if __name__ == "__main__":
    main()
