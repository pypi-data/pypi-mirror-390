import sys
import gzip
from log import CustomLogger

logger = CustomLogger.get_logger(__name__)


def map_header_cols_to_indx(header_line: str) -> dict[str, int]:
    """We want to map column in the header to an index so that later we can access the right column"""
    return {
        col_name: indx for indx, col_name in enumerate(header_line.strip().split("\t"))
    }


def run_pull_samples(args) -> None:
    # We need to make sure the correct arguments were passed
    if not args.cases_only and args.case_col is not None:
        logger.fatal(
            "Expected the case-col flag to be empty since the case-only flag was not used. If you intend to only pull cases please pass the cases-only flag"
        )
        sys.exit(1)
    if args.cases_only and args.case_col is None:
        logger.fatal(
            "Expect arguments to be passed to the case-col flag since the cases-only flag was used. If you intend to pull only cases please provide both the cases-only flag and the column name to pull using the case-col flag."
        )

    # we are going to alias the open function to another variable. This aliasing is used
    # so that we can appropriately select the gzip reader if the file is compressed.
    writer = open
    # Alias the gzip writer instead if the file is compressed
    if args.input.suffix == ".gz":
        logger.debug(
            f"detected that the input file, {args.input}, was compressed. Using the gzip reader instead of standard open function"
        )
        writer = gzip.open

    with writer(args.input, "rt") as drive_results:
        samples = []
        # map the header line to an index
        header_map = map_header_cols_to_indx(next(drive_results))

        # If the user only wants to pull the column then we have to find
        # the index for that column header. Otherwise we can just pull
        # the IDs column for the whole network
        if args.cases_only:
            try:
                col_indx = header_map[args.case_col]
            except KeyError:
                logger.fatal(
                    f"Could not find the column, {args.case_col}, in the header. Please make sure you spelled the column you wish to grab exactly as it appears in the header"
                )
                sys.exit(1)
        else:
            col_indx = 6

        for line in drive_results:
            split_line = line.strip().split("\t")
            if split_line[0] == args.network_id:
                samples = split_line[col_indx].strip().split(",")
                break
        if len(samples) != 0:
            with open(args.output, "w", encoding="utf-8") as output_file:
                for grid in samples:
                    output_file.write(f"{grid.strip()}\n")
        else:
            logger.critical(
                f"The network id, {args.network_id}, was not found within the networks file at {args.input}. Please ensure that all of the network ids are properly formatted and that the network is present within your input file."
            )
