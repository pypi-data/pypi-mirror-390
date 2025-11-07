import argparse
from importlib.metadata import version
from pathlib import Path

from rich_argparse import RichHelpFormatter

from drive.dendrogram import generate_dendrograms
from drive.network import run_network_identification
from drive.utilities.pull_samples import run_pull_samples
from drive.utilities.callbacks import CheckInputExist
from drive.utilities.testing import run_integration_test


def generate_cmd_parser() -> argparse.ArgumentParser:
    """Function that will generate the correct cmd parser for DRIVE"""
    parser = argparse.ArgumentParser(
        description=" Distant Relatedness for Identification and Variant Evaluation (DRIVE) is a novel approach to IBD-based genotype inference used to identify shared chromosomal segments in dense genetic arrays",
        formatter_class=RichHelpFormatter,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s: {version('drive-ibd')}"
    )

    # We are also going to create a parser for common options
    common_parser = argparse.ArgumentParser(
        formatter_class=RichHelpFormatter, add_help=False
    )

    logging_group = common_parser.add_argument_group(
        "logging",
        description="parameters that affect what runtime information is printed to a file or the console",
    )

    logging_group.add_argument(
        "--verbose",
        "-v",
        default=0,
        help="verbose flag indicating if the user wants more information",
        action="count",
    )

    logging_group.add_argument(
        "--log-to-console",
        default=False,
        help="Optional flag to log to only the console or also a file",
        action="store_true",
    )

    logging_group.add_argument(
        "--log-filename",
        default="drive.log",
        type=str,
        help="Name for the log output file. (default: %(default)s)",
    )

    # This first section will handle all of the arguments for the
    # clustering subcommand
    subparser = parser.add_subparsers(
        title="subcommands",
        description="options to run either the DRIVE clustering algorithm or the dendrogram algorithm. To run DRIVE, type either: 'drive cluster --help' or 'drive dendrogram --help'",
    )

    cluster_parser = subparser.add_parser(
        name="cluster",
        help="run the DRIVE clustering algorithm",
        formatter_class=RichHelpFormatter,
        parents=[common_parser],
        description="cluster",
    )

    cluster_parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="IBD input file from ibd detection software",
        required=True,
        action=CheckInputExist,
    )

    cluster_parser.add_argument(
        "--format",
        "-f",
        default="hapibd",
        type=str,
        help="IBD program used to detect segments. Allowed values are hapibd, ilash, germline, rapid. Program expects for value to be lowercase. (default: %(default)s)",
        choices=["hapibd", "ilash", "germline", "rapid"],
    )

    cluster_parser.add_argument(
        "--target",
        "-t",
        type=str,
        help="Target region or position, chr:start-end or chr:pos",
        required=True,
    )

    cluster_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="output file prefix. The program will append .drive_networks.txt to the filename provided",
        required=True,
    )

    cluster_parser.add_argument(
        "--min-cm",
        "-m",
        default=3,
        type=int,
        help="minimum centimorgan threshold. The program expects this to be an integer value. (default: %(default)s)",
    )

    cluster_parser.add_argument(
        "--step",
        "-k",
        default=3,
        type=int,
        help="Minimum required number of steps for the community walktrap algorithm.(default: %(default)s)",
    )

    cluster_parser.add_argument(
        "--max-recheck",
        default=5,
        type=int,
        help="Maximum number of times to re-perform the clustering. This value will not be used if the flag --no-recluster is used.(default: %(default)s)",  # noqa: E501
    )

    cluster_parser.add_argument(
        "--cases",
        "-c",
        type=Path,
        help="A file containing individuals who are cases. This file expects for there to be two columns. The first column will have individual ids and the second has status where cases are indicated by a 1, control are indicated by a 0, and exclusions are indicated by NA.",  # noqa: E501
        action=CheckInputExist,
    )

    cluster_parser.add_argument(
        "--segment-overlap",
        default="contains",
        choices=["contains", "overlaps"],
        type=str,
        help="Indicates if the user wants the gene to contain the whole target region or if it just needs to overlap the segment. (default: %(default)s)",  # noqa: E501
    )

    cluster_parser.add_argument(
        "--max-network-size",
        default=30,
        type=int,
        help="maximum network size allowed if the user has allowed the recluster option. (default: %(default)s)",
    )

    cluster_parser.add_argument(
        "--min-connected-threshold",
        default=0.5,
        type=float,
        help="minimum connectedness ratio required for the network. (default: %(default)s)",
    )

    cluster_parser.add_argument(
        "--min-network-size",
        default=3,
        type=int,
        help="This argument sets the minimun network size that we allow. All networks smaller than this size will be filtered out. If the user wishes to keep all networks they can set this to 0. (default: %(default)s)",  # noqa: E501
    )

    cluster_parser.add_argument(
        "--segment-distribution-threshold",
        default=0.2,
        type=float,
        help="Threshold to filter the network length to remove hub individuals. (default: %(default)s)",
    )

    cluster_parser.add_argument(
        "--phenotype-name",
        default=None,
        type=str,
        help="If the user wishes to only run 1 phenotype from a file with multiple phenotypes they can prioritize a column that has the phenotype name. The name must match with the column.",
    )

    cluster_parser.add_argument(
        "--hub-threshold",
        default=0.01,
        type=float,
        help="Threshold to determine what percentage of hubs to keep. (default: %(default)s)",
    )

    cluster_parser.add_argument(
        "--json-config",
        "-j",
        default=None,
        type=Path,
        help="path to the json config file",
    )

    cluster_parser.add_argument(
        "--recluster",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="whether or not the user wishes the program to automically recluster based on things like hub threshold, max network size and how connected the graph is. ",  # noqa: E501
    )

    cluster_parser.add_argument(
        "--chunksize",
        type=int,
        default=100_000,
        help="change the chunksize used to read in the shared segment data. Larger chunksizes will speed up the analysis but will use more memory. There is a asymptotic limit on the speed up still. Due to how pandas reads in data, trying to read in the whole file at once will still be slower than chunking if the file is really big. (default: %(default)s)",
    )

    cluster_parser.add_argument(
        "--compress-output",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="whether or not to compress the output file from the DRIVE clustering output file. When the program is run PhenomeWide, the output file can be quite large. This option helps make file storage more managable",
    )

    cluster_parser.add_argument(
        "--phecode-categories-to-keep",
        required=False,
        nargs="+",
        type=str,
        help="List of phecode categories to write to the output file. This flag is only useful if you are running DRIVE phenomewide and if you are running DRIVE with phecodeX. DRIVE will calculate pvalues for all phecodes by default. This flag will check to see if the PheCode Category prefix (such as the CV prefix for cardiovascular phecodes) and only return those phecodes that match. Even with this flag, DRIVE will still return the phenomewide minimum phecode across all the different phecodes. If there is a '/' in the category name please replace this with a underscore",
    )

    cluster_parser.add_argument(
        "--split-phecode-categories",
        required=False,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="if this flag is provided by the user then the output will be broken up into a file for each phecode category. Each file will still contain the columns that give the network information and the minimum phecode for each network. Output files will all be written to the same output directory. This flag should only be used if the user is running the analysis phenomewide. It shouldn't be used with the phecode-categories-to-keep flag.",
    )

    cluster_parser.set_defaults(func=run_network_identification)

    # This is where we will define all of the necessary arguments to make
    # the dendrogram script work
    dendrogram_parser = subparser.add_parser(
        name="dendrogram",
        help="run the DRIVE dendrogram program",
        formatter_class=RichHelpFormatter,
        parents=[common_parser],
        description="dendrogram",
    )

    dendrogram_parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input file to generate the dendrogram from. This file should be the output from running DRIVE",
        required=True,
        action=CheckInputExist,
    )

    dendrogram_parser.add_argument(
        "--ibd",
        type=Path,
        help="path to the input ibd file that was used to create the networks from",
        required=True,
        action=CheckInputExist,
    )

    dendrogram_parser.add_argument(
        "--output",
        "-o",
        help="directory to write output to. Default value: %(default)s",
        default=Path("./"),
        type=Path,
    )

    dendrogram_parser.add_argument(
        "--keep-temp",
        default=False,
        help="Optional flag to retain the intermediate distance matrices. (default: %(default)s)",
        action="store_true",
    )

    dendrogram_parser.add_argument(
        "--format",
        "-f",
        default="hapibd",
        type=str,
        help="IBD program used to detect segments. Allowed values are hapibd, ilash, germline, rapid. Program expects for value to be lowercase. (default: %(default)s)",
        choices=["hapibd", "ilash", "germline", "rapid"],
    )

    dendrogram_parser.add_argument(
        "--target",
        "-t",
        type=str,
        help="Target region or position, chr:start-end or chr:pos",
        required=True,
    )

    dendrogram_parser.add_argument(
        "--segment-overlap",
        default="contains",
        choices=["contains", "overlaps"],
        type=str,
        help="Indicates if the user wants the gene to contain the whole target region or if it just needs to overlap the segment. (default: %(default)s)",  # noqa: E501
    )

    dendrogram_parser.add_argument(
        "--min-cm",
        "-m",
        default=3,
        type=int,
        help="minimum centimorgan threshold. The program expects this to be an integer value. (default: %(default)s)",
    )

    dendrogram_parser.add_argument(
        "--map-ids",
        default=False,
        help="Map the ids in the network to an anonymous ID of the form patient_X. This labelling is mainly used for publication to change internal identifiers. The mapping will be saved in the output directory as the dendrogram as a file called 'network_{clstID}_id_mappings.txt' (default: %(default)s)",
        action="store_true",
    )

    # Add a mutually exclusive group that requires you to either provide the
    # argument for the network id or the generate-all flag
    exclusive_group = dendrogram_parser.add_mutually_exclusive_group(required=True)

    exclusive_group.add_argument(
        "--network-id",
        "-n",
        type=str,
        help="Network ID to make dendrograms only for a specific cluster. This value needs to match what is in the clstID column from the output from DRIVE.",
    )

    exclusive_group.add_argument(
        "--generate-all",
        default=False,
        help="Optional flag to choose to generate dendrograms for all networks. This option will require longer runtime. (default: %(default)s)",
        action="store_true",
    )

    dendrogram_parser.add_argument(
        "--max-network-size",
        type=int,
        default=30,
        help="maximum network size to make a dendrogram for. When networks are really large they are hard to visualize. We suggest using your own script for these networks. This value will only be used if the user chooses to generate all the dendrograms in the DRIVE output. (default: %(default)s)",
    )

    dendrogram_parser.add_argument(
        "--min-network-size",
        type=int,
        default=3,
        help="minimum network size to make a dendrogram for. By default, DRIVE can return 2 person networks. Dendrogram should not be made for these because they are uninformative. Users can also select different values if they are interested in returning networks of only size 'x' or larger. This value will only be used if the user chooses to generate all the dendrograms in the DRIVE output. (default: %(default)s)",
    )

    dendrogram_parser.add_argument(
        "--font-size",
        default=15,
        type=int,
        help="set the label size for the output dendrograms. (default: %(default)s)",
    )

    dendrogram_parser.add_argument(
        "--title",
        type=str,
        default="test dendrogram",
        help="title of the dendrogram to be written on the plot. This is not the output file name. This argument should not be used if you are creating dendrograms for every network provided by DRIVE",
    )

    dendrogram_parser.set_defaults(func=generate_dendrograms)

    # The utilities parser is going to be used to create help commands
    # that can process the file. This can be used as follows: drive utilities <subcommand> ...
    utilities_parser = subparser.add_parser(
        name="utilities",
        help="Run subcommands that help process the drive file",
        formatter_class=RichHelpFormatter,
        parents=[common_parser],
        description="utilities",
    )

    utility_cmd_subparser = utilities_parser.add_subparsers(
        title="utility commands",
        description="helper functions that help process the DRIVE file",
    )

    # This command will be used to pull samples from a network of interest and provide that to
    pull_samples_parser = utility_cmd_subparser.add_parser(
        name="pull-samples",
        help="pull sample ids from a network of interest",
        formatter_class=RichHelpFormatter,
        parents=[common_parser],
        description="pull-samples",
    )

    pull_samples_parser.add_argument(
        "-n",
        "--network-id",
        type=str,
        required=True,
        help="ID of the network to pull from the DRIVE results file",
    )

    pull_samples_parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="filepath to a tab separated file that described each of the network from the drive analysis. This command is designed to work with the output from the drive cluster command. You can use the output file from DRIVE as input or a file with the same columns and structure.",
    )

    pull_samples_parser.add_argument(
        "--cases-only",
        default=False,
        help="Optional flag that indicates if the user wants to pull the ids for all samples in a network or just the cases. If this flag is provided then the user also needs to provide the '--case-col' flag. (default: %(default)s)",
        action="store_true",
    )

    pull_samples_parser.add_argument(
        "--case-col",
        type=str,
        help="This is the column that list the cases in the network of interest. This flag should only be used if the '--cases-",
    )

    pull_samples_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("samples.txt"),
        help="Output tab separated text file with one column where each row is a sample id. This file is designed to work with bcftools. (default: %(default)s)",
    )

    pull_samples_parser.set_defaults(func=run_pull_samples)

    testing_parser = utility_cmd_subparser.add_parser(
        name="test",
        help="run the integration test to ensure that DRIVE was installed correctly",
        formatter_class=RichHelpFormatter,
        parents=[common_parser],
        description="run-integration-test",
    )

    testing_parser.add_argument(
        "--run-integration-test",
        default=True,
        help="Flag that indicates the user wishes to run the integration test. (default: %(default)s)",
        action="store_true",
    )

    testing_parser.set_defaults(func=run_integration_test)

    return parser
