import itertools
import pytest
import sys
import pandas as pd
import sysconfig
from pathlib import Path
import os

sys.path.append("./src")

from drive import drive


site_packages_path = Path(sysconfig.get_paths().get("platlib"))


@pytest.fixture()
def system_args_no_pheno(monkeypatch):
    input_file = (
        site_packages_path / "tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz"
    )

    output_file = (
        site_packages_path / "tests/test_output/integration_test_results_no_pheno"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "drive",
            "cluster",
            "-i",
            str(input_file.absolute()),
            "-f",
            "hapibd",
            "-t",
            "20:4666882-4682236",
            "-o",
            str(output_file.absolute()),
            "-m",
            "3",
            "--recluster",
            "--log-filename",
            "integration_test_results_no_pheno.log",
        ],
    )


@pytest.fixture()
def with_compression_flag(monkeypatch):
    input_file = (
        site_packages_path / "tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz"
    )

    output_file = (
        site_packages_path
        / "tests/test_output/integration_test_results_with_compression_flag"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "drive",
            "cluster",
            "-i",
            str(input_file.absolute()),
            "-f",
            "hapibd",
            "-t",
            "20:4666882-4682236",
            "-o",
            str(output_file.absolute()),
            "-m",
            "3",
            "--recluster",
            "--log-filename",
            "integration_test_results_no_pheno.log",
            "--compress-output",
        ],
    )


@pytest.fixture()
def system_args_with_pheno(monkeypatch):
    input_file = (
        site_packages_path / "tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz"
    )

    output_file = (
        site_packages_path / "tests/test_output/integration_test_results_with_pheno"
    )

    carrier_file = (
        site_packages_path / "tests/test_inputs/test_phenotype_file_withNAs.txt"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "drive",
            "cluster",
            "-i",
            str(input_file.absolute()),
            "-f",
            "hapibd",
            "-t",
            "20:4666882-4682236",
            "-o",
            str(output_file.absolute()),
            "-m",
            "3",
            "-c",
            str(carrier_file.absolute()),
            "--recluster",
            "--log-file",
            "integration_test_results_with_pheno.log",
        ],
    )


@pytest.fixture()
def system_args_for_dendrogram(monkeypatch):
    input_file = (
        site_packages_path
        / "tests/test_inputs/integration_dendrogram_test_results_no_pheno.drive_networks.txt"
    )

    output_path = site_packages_path / "tests/test_output/"

    ibd_file = (
        site_packages_path / "tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "drive",
            "dendrogram",
            "-i",
            str(input_file.absolute()),
            "-f",
            "hapibd",
            "-t",
            "20:4666882-4682236",
            "-o",
            str(output_path.absolute()),
            "-n",
            "0",
            "-m",
            "3",
            "--ibd",
            str(ibd_file.absolute()),
            "--log-file",
            "integration_dendrogram_test_results.log",
        ],
    )


def test_drive_full_run_no_phenotypes(system_args_no_pheno):
    # Make sure the output directory exists
    output_path = site_packages_path / "tests/test_output"
    output_path.mkdir(exist_ok=True)

    drive.main()

    # we need to make sure the output was properly formed
    output = pd.read_csv(
        site_packages_path
        / "tests/test_output/integration_test_results_no_pheno.drive_networks.txt",
        sep="\t",
    )
    # list of errors to keep
    errors = []

    # list of columns it should have
    expected_colnames = [
        "clstID",
        "n.total",
        "n.haplotype",
        "true.positive.n",
        "true.positive",
        "falst.postive",
        "IDs",
        "ID.haplotype",
    ]

    if not output.shape == (165, 8):
        errors.append(
            f"Expected the output to have 165 rows and 8 columns instead it had {output.shape[0]} rows and {output.shape[1]}"
        )
    if [col for col in output.columns if col not in expected_colnames]:
        errors.append(
            f"Expected the output to have the columns: {','.join(expected_colnames)}, instead these columns were found: {','.join(output.columns)}"
        )

    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_drive_with_compression_flag(with_compression_flag):
    # Make sure the output directory exists
    output_path = site_packages_path / "tests/test_output"
    output_path.mkdir(exist_ok=True)

    drive.main()

    errors = []

    output_file = (
        site_packages_path
        / "tests/test_output/integration_test_results_with_compression_flag.drive_networks.txt.gz"
    )

    uncompressed_output_file = (
        site_packages_path
        / "tests/test_output/integration_test_results_with_compression_flag.drive_networks.txt"
    )

    if not os.path.exists(output_file):
        errors.append(
            f"Expected to find the output file, {output_file}. This file was not found"
        )
    if os.path.exists(uncompressed_output_file):
        errors.append(
            f"Expected to find a compressed file, {output_file}. Instead we found the uncompressed output file, {uncompressed_output_file}"
        )
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_drive_full_run_with_phenotypes(system_args_with_pheno):
    # Make sure the output directory exists
    output_path = site_packages_path / "tests/test_output"
    output_path.mkdir(exist_ok=True)

    drive.main()

    # we need to make sure the output was properly formed
    output = pd.read_csv(
        site_packages_path
        / "tests/test_output/integration_test_results_with_pheno.drive_networks.txt",
        sep="\t",
    )

    # list of errors to keep
    errors = []

    # lets read in the header of the phenotype file so that we can form the additional columns
    with open(
        site_packages_path / "tests/test_inputs/test_phenotype_file_withNAs.txt", "r"
    ) as pheno_input:
        grid_col, pheno1, pheno2, pheno3 = pheno_input.readline().strip().split("\t")

        col_combinations = list(
            itertools.product(
                [pheno1, pheno2, pheno3],
                [
                    "_case_count_in_network",
                    "_cases_in_network",
                    "_excluded_count_in_network",
                    "_excluded_in_network",
                    "_pvalue",
                ],
            )
        )

        phenotype_cols = [
            "min_pvalue",
            "min_phenotype",
            "min_phenotype_description",
        ] + ["".join(val) for val in col_combinations]

    # list of columns it should have
    expected_colnames = [
        "clstID",
        "n.total",
        "n.haplotype",
        "true.positive.n",
        "true.positive",
        "falst.postive",
        "IDs",
        "ID.haplotype",
    ] + phenotype_cols

    if not output.shape == (165, 26):
        errors.append(
            f"Expected the output to have 165 rows and 8 columns instead it had {output.shape[0]} rows and {output.shape[1]}"
        )
    if [col for col in output.columns if col not in expected_colnames]:
        errors.append(
            f"Expected the output to have the columns: {','.join(expected_colnames)}, instead these columns were found: {','.join(output.columns)}"
        )

    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_drive_dendrogram_single_network(system_args_for_dendrogram):
    output_path = site_packages_path / "tests/test_output"
    output_path.mkdir(exist_ok=True)

    drive.main()

    output_path = output_path / "network_0_dendrogram.png"

    assert (
        output_path.exists()
    ), "An error occurred while running the integration test for the dendrogram functionality. This error prevented the appropriate output from being generated."


@pytest.fixture()
def system_args_for_pull_samples(monkeypatch):
    input_path = (
        site_packages_path
        / "tests/test_inputs/integration_dendrogram_test_results_no_pheno.drive_networks.txt"
    )
    output_path = site_packages_path / "tests/test_output/test_sample_list.txt"

    monkeypatch.setattr(
        "sys.argv",
        [
            "drive",
            "utilities",
            "pull-samples",
            "-i",
            str(input_path.absolute()),
            "-o",
            str(output_path.absolute()),
            "-n",
            "4",
        ],
    )


def test_pull_samples_success(system_args_for_pull_samples):
    output_path = site_packages_path / "tests/test_output"
    output_path.mkdir(exist_ok=True)

    # run the drive function
    drive.main()

    samples_filepath = output_path / "test_sample_list.txt"

    assert (
        samples_filepath.exists()
    ), f"An error occurred while running the integration test for the utilties 'pull-samples' subcommand. the output file, {samples_filepath}, was not found."


def test_for_correct_samples(system_args_for_pull_samples):
    output_path = site_packages_path / "tests/test_output"
    output_path.mkdir(exist_ok=True)

    # run the drive function
    drive.main()

    samples_filepath = output_path / "test_sample_list.txt"

    # we are going to make a set of samples to look for and use this to check if all of the samples are in the file
    samples_to_find = {"535", "574", "94", "210", "676"}

    samples_in_file = set()

    with open(samples_filepath, "r") as samples_file:
        # we are making the assumption that each line in the file is a single id
        for line in samples_file:
            samples_in_file.add(line.strip())

    sample_differences = samples_to_find.difference(samples_in_file)

    assert (
        not sample_differences
    ), f"The samples, {','.join(sample_differences)}, were expected to be found within the file but were not. Instead, only these values were found, {','.join(samples_in_file)}"
