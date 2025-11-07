import gzip
import sys
from dataclasses import dataclass
from typing import Callable, Iterable, List

from log import CustomLogger

from drive.network.factory import factory_register
from drive.network.models import Network_Interface, RuntimeState
from drive.utilities.parser.phenotype_descriptions_parser import PhecodesMapper

logger = CustomLogger.get_logger(__name__)


@dataclass
class NetworkWriter:
    """Class that is responsible for creating the *_networks.
    txt file from the information provided"""

    name: str = "NetworkWriter plugin"

    @staticmethod
    def _form_header(phenotypes: List[str]) -> str:
        """Method that will form the header line for the output file

        Parameters
        ----------
        phenotypes : List[str]
            list of all the phenotypes from the Data.carriers attribute

        Returns
        -------
        str
            returns the header string for the file
        """

        # making a string for the initial first few columns
        header_str = "clstID\tn.total\tn.haplotype\ttrue.positive.n\ttrue.positive\tfalst.postive\tIDs\tID.haplotype"  # noqa: E501

        if not phenotypes:
            return header_str + "\n"
        else:
            # We need to add columns for the min pvalue descriptions
            header_str += "\tmin_pvalue\tmin_phenotype\tmin_phenotype_description"
            # for each phenotype we are going to create 4 columns for the number
            # of cases in the network, The case ids in the network the number of
            # excluded individuals in the network, and the pvalue for the phenotype
            for column in phenotypes:
                header_str += f"\t{column + '_case_count_in_network'}\t{column + '_cases_in_network'}\t{column + '_excluded_count_in_network'}\t{column + '_excluded_in_network'}\t{column + '_pvalue'}"  # noqa: E501

            return header_str + "\n"

    @staticmethod
    def _create_network_info_str(
        network: Network_Interface, phenotypes: List[str]
    ) -> str:
        """create a string that has all the information from the network
        such as cluster id, member count, pvalues, etc...

        Parameters
        ----------
        network : Network_Interface
            network object that hsas all the per network
            information from the clusters such as cluster
            ids, networks, pvalues, etc...

        phenotypes : List[str]
            list of the phenotypes provided the program.

        Returns
        -------
        str
            returns a string formatted for the output file
        """
        # fill in the initial few columns of the output string
        output_str = f"{network.clst_id}\t{len(network.members)}\t{len(network.haplotypes)}\t{network.true_positive_count}\t{network.true_positive_percent:.4f}\t{network.false_negative_count}\t{','.join(network.members)}\t{','.join(network.haplotypes)}"  # noqa: E501

        if not phenotypes:
            return output_str + "\n"
        else:
            output_str += f"\t{network.min_pvalue_str}"

            for phenotype in phenotypes:
                output_str += f"\t{network.pvalues[phenotype]}"

            return output_str + "\n"

    @staticmethod
    def check_keep_categories(
        categories_to_keep: list[str], phecodeDesc: PhecodesMapper
    ) -> None:
        """Check if the phecode categories that the user
        provided exist in our mappings file. This step will
        hopefully catch typos

        Parameters
        ----------
        categories_to_keep : list[str]
            list of phecode categories that the user wishes to
            keep

        phecodeDesc : PhecodesMapper
            object that maps the phecode ids to their
            descriptions and it maps which phecodes are in which
            categories

        Raises
        ------
        ValueError
            raises a value error if there are any categories
            that were not in the mapping file
        """

        category_not_found = []
        for category in categories_to_keep:
            if category not in phecodeDesc.category_groups.keys():
                category_not_found.append(category)
        if len(category_not_found) > 0:
            output_str = ", ".join(category_not_found)
            available_vals = ", ".join(phecodeDesc.category_groups.keys())
            logger.critical(
                f"categories, {output_str}, were not found in the list of categories. Allowed values are: {available_vals}"
            )
            raise ValueError(
                f"categories {output_str} not found. Please check spelling of the phecode category"
            )

    @staticmethod
    def collect_phenotypes(
        categories_to_keep: list[str],
        phecode_cols: Iterable[str],
        phecodeDesc: PhecodesMapper,
    ) -> list[str]:
        return_list = []
        for category in categories_to_keep:
            phecodes_in_category = phecodeDesc.category_groups.get(category, [])
            return_list.extend(
                [value for value in phecode_cols if value in phecodes_in_category]
            )

        if len(return_list) == 0:
            phecode_str = ", ".join(categories_to_keep)
            logger.fatal(
                f"There were no phecodes from the provided phenotype file that fell into the PheWAS defined categories: {phecode_str}. This error probably indicates you are using multiple custom phecode columns and DRIVE is unable to filter for custom phecode columns"
            )
            sys.exit(1)
        return return_list

    @staticmethod
    def multi_file_output(
        writer: Callable,
        data: RuntimeState,
        phenotypes: PhecodesMapper,
        compress_output: bool,
    ) -> None:
        """write the output to different files based on phecode category

        Parameters:
        -----------
        writer : Callable
            function that opens a filehandle. This will either be the python open
            function or the gzip.open function if the user chooses to compress the
            output

        data : RuntimeState
            container that holds information about the runtime of the program such
            as the networks identified and configuration optons that the user has
            choosen

        phecodes : PhecodesMapper
            object that contains information about the phecodes such as what phecodes are within each category

        compress_output : bool
            indicates whether the user wants to compress the output or not
        """

        logger.info(
            "Writing output for each phecode category to a separate output file within the output directory"
        )

        # We need to iterate over each group
        for category, phecodes in phenotypes.category_groups.items():

            phecodes_in_analysis = [
                phecode for phecode in phecodes if phecode in data.carriers.keys()
            ]
            # The phenotypes.category_groups contains phecodes for both 1.2 and X so we should expect if the user provides only PheCode X classifications then it will not find any phecodes from the 1.2 categories and vice versa. Because of this fact we can just use continue in the loop if there are no phecodes found for a group
            if len(phecodes_in_analysis) == 0:
                continue
            # We should warn the user though if the number of phecodes used in the analysis does
            if len(phecodes_in_analysis) != len(phecodes):
                logger.debug(
                    f"Using {len(phecodes_in_analysis)} from the original {len(phecodes)} in the category {category}. Any difference between the two counts is the results of the original file containing all the possible phecodes while the input matrix only contains a subset of the phecodes"
                )

            # we are going to replace the spaces if there are any in the category and replace
            # it with an underscore. This just helps with file naming
            category = category.replace(" ", "_")

            network_file_output = data.output_path.parent / (
                data.output_path.name + f".{category}" + ".drive_networks.txt"
            )

            if compress_output:
                network_file_output = (
                    network_file_output.parent / f"{network_file_output.name}.gz"
                )

            logger.verbose(
                f"The output in the network_writer plugin is being written to: {network_file_output}"  # noqa: E501
            )

            with writer(network_file_output, "wt") as networks_output:
                # The phecodes from the category_groups includes every single phecode that is
                # defined in the pheWAS catelogue. Sometimes our matrix might not have all of
                # those codes. We need to make sure that we only use the codes that match ours

                header_str = NetworkWriter._form_header(phecodes_in_analysis)
                # iterate over each network and pull out the appropriate
                # information into strings
                _ = networks_output.write(header_str)

                for network in data.networks:
                    network_info_str = NetworkWriter._create_network_info_str(
                        network, phecodes_in_analysis
                    )

                    networks_output.write(network_info_str)

    @staticmethod
    def single_file_output(
        writer: Callable,
        data: RuntimeState,
        phenotypes: list[str],
        compress_output: bool,
    ) -> None:
        """Write output to a single file

        Parameters:
        -----------
        writer : Callable
            function that opens a filehandle. This will either be the python open
            function or the gzip.open function if the user chooses to compress the
            output

        data : RuntimeState
            container that holds information about the runtime of the program such
            as the networks identified and configuration optons that the user has
            choosen

        phenotypes : list[str]
            list of the phenotypes to write output for. This can either be all of
            the phenotypes or a subset specified by the user

        compress_output : bool
            indicates whether the user wants to compress the output or not
        """

        # Create the output path for the file
        network_file_output = data.output_path.parent / (
            data.output_path.name + ".drive_networks.txt"
        )  # noqa: E501

        if compress_output:
            network_file_output = (
                network_file_output.parent / f"{network_file_output.name}.gz"
            )

        logger.debug(
            f"The output in the network_writer plugin is being written to: {network_file_output}"  # noqa: E501
        )

        with writer(network_file_output, "wt") as networks_output:
            header_str = NetworkWriter._form_header(phenotypes)
            # iterate over each network and pull out the appropriate
            # information into strings
            _ = networks_output.write(header_str)

            for network in data.networks:
                network_info_str = NetworkWriter._create_network_info_str(
                    network, phenotypes
                )

                networks_output.write(network_info_str)

    def analyze(self, **kwargs) -> None:
        """main function of the plugin that will create the
        output path and then use helper functions to write
        information to a file"""
        # We need to pull out the data to write to a file
        # and then the configuration options to use
        data: RuntimeState = kwargs["data"]
        config_options = data.config_options
        compress_data = config_options.get("compress", False)
        phecodes_to_keep = config_options.get("phecode_categories_to_keep", [])
        # If the user wants to output the different phecodes as different files
        split_phecodes = config_options.get("split_phecode_categories", False)

        # Create the output
        writer = open

        if compress_data:
            writer = gzip.open

        # we are going to pull out the phenotypes into a list so that we
        # are guarenteed to maintain order as we are creating the rows
        if phecodes_to_keep:
            # make sure the categories exist
            self.check_keep_categories(phecodes_to_keep, data.phenotype_descriptions)

            # We are going to find all of the phecodes that are in this additional string
            phecode_categories = ", ".join(phecodes_to_keep)
            logger.info(
                f"Gathering the results for the phecodes in the categories: {phecode_categories}"
            )

            phenotypes = self.collect_phenotypes(
                phecodes_to_keep, data.carriers.keys(), data.phenotype_descriptions
            )

            if len(phenotypes) == 0:
                logger.fatal(
                    f"There were no phenotypes found in the categories: {phecode_categories}. This probably indicates a typo in the flag provided. No output will be written and program will be terminated."
                )
                sys.exit(1)
        else:
            phenotypes = list(data.carriers.keys())

        # We need to decide how to write the output. Whether we want
        # to write it as multiple files or to output to a single file
        if split_phecodes:
            self.multi_file_output(
                writer, data, data.phenotype_descriptions, compress_data
            )
        else:
            self.single_file_output(writer, data, phenotypes, compress_data)


def initialize() -> None:
    factory_register("network_writer", NetworkWriter)
