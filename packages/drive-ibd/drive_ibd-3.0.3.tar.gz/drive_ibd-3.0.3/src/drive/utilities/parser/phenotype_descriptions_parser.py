from pathlib import Path
from dataclasses import dataclass, field
import csv
import sys

from log import CustomLogger

from pandas import read_csv

logger = CustomLogger.get_logger(__name__)


@dataclass
class PhecodesMapper:
    phecode_names: dict[str, str] = field(default_factory=dict)
    category_groups: dict[str, list[str]] = field(default_factory=dict)


def load_phenotype_descriptions(
    phecode_container: PhecodesMapper,
) -> None:
    """Function that will loads information about the phecode id names and the categories into a dictionary

    Parameters
    ----------
    phecode_container : PhecodesMapper
        class that contains 2 maps. One map has key value
        pairs mapping the phecode id to the phecode name.
        The other map stores all the phecode categories as
        keys and a list of the phecode ids within that
        category as values

    """
    # We need to find the path to each phecode file

    phecode_filepaths = Path(__file__).parent.parent.parent / "phecode_mappings"

    phecode_map_files = list(phecode_filepaths.glob("*.txt"))

    if len(phecode_map_files) != 2:
        logger.critical(
            f"Unable to detect the files for the PheCode 1.2 & PheCode X mappings. This error probably means they were deleted. Attempted search in this directory: {phecode_filepaths}."
        )
        sys.exit(1)

    for file in phecode_map_files:
        with open(file, "r") as phecode_file:
            header = next(phecode_file)
            csvreader = csv.reader(phecode_file, delimiter="\t", quotechar='"')
            for line in csvreader:
                phecodeid, desc, category = line
                if "/" in category:
                    category = category.replace("/", "_")
                # There are phecodes in the 1000+ range that have no category.
                # We will use the phrase other here
                if category == "NULL":
                    category = "Other"
                phecode_container.phecode_names[phecodeid] = desc
                phecode_container.category_groups.setdefault(category, []).append(
                    phecodeid
                )
