import json
import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

from ipsl_ncdiff.diff import diff
from ipsl_ncdiff.loader.auto import open_dataset
from ipsl_ncdiff.output import format_nccmp
from ipsl_ncdiff.tolerance import ToleranceDict


def main():
    """
    Implementation of the main ipsl-ncdiff script.
    """
    parser = ArgumentParser()
    parser.add_argument("inputs", nargs=2)
    parser.add_argument(
        "--frontend",
        choices=["auto", "h5netcdf"],
        default="auto",
        help="Select fronted used to open and read NetCDF files (default: "
        "%(default)s; auto means automatic selection of the frontend)",
    )
    # parser.add_argument("--nan-not-equal", action="store_true")
    parser.add_argument(
        "--exclude",
        nargs="*",
        type=str,
        help="List of excluded variables from the comparison",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Don't display difference report. Instead, return 0 if files are equal and 1 if they are not",
    )
    parser.add_argument(
        "--tolerance-file",
        type=Path,
        help="Path to a file with difference tolerances considered as the same values.",
    )
    tests_group = parser.add_argument_group(
        "Testing options", "Control specific testing options"
    )
    tests_group.add_argument(
        "--skip-global-attributes",
        action="store_true",
        help="Skip comparison of global attributes",
    )
    tests_group.add_argument(
        "--align-dimensions",
        # TODO: for the moment, only single dimension alignment is supported
        nargs=1,
        type=str,
        help="Align with a single dimension to compare the variable intersecting parts",
    )

    output_group = parser.add_argument_group(
        "Output format", "Format of the output results"
    )
    format_group = output_group.add_mutually_exclusive_group(required=False)
    format_group.add_argument(
        "--json", action="store_true", help="Display difference report in JSON format"
    )
    format_group.add_argument(
        "--csv", action="store_true", help="Display difference report in CSV format"
    )
    format_group.add_argument(
        "--nccmp",
        action="store_true",
        help="Display value difference in a table as in the nccmp tool",
    )
    args = parser.parse_args()

    # TODO: finish fronted selection
    # if args.frontend == "auto":
    #     print("Trying to select the frontend automatically")

    # TODO:
    # 1. Check if any file is empty -> then STOP
    # 2. Check if all variables are the same -> in strict mode -> STOP, otherwise continue with common variables
    # TODO: pass frontend option to the open_dataset()
    with open_dataset(args.inputs[0]) as dataset_1:
        with open_dataset(args.inputs[1]) as dataset_2:
            tolerances = (
                ToleranceDict.from_file(args.tolerance_file)
                if args.tolerance_file
                else None
            )
            differences = diff(
                dataset_1,
                dataset_2,
                exclude_variables=args.exclude or [],
                tolerances=tolerances,
                skip_attributes=args.skip_global_attributes,
                align_dimensions=args.align_dimensions,
            )
            # Print output or not!
            if args.silent:
                pass
            else:
                if args.json:
                    print(json.dumps(differences, indent=2))
                elif args.nccmp:
                    print(format_nccmp(differences))
                else:
                    pprint(differences)
            sys.exit(0) if not differences else sys.exit(1)


if __name__ == "__main__":
    main()
