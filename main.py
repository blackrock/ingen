#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.
import argparse
import logging

from ingen.main import main
from datetime import datetime
from datetime import date
from ingen.utils.utils import KeyValue
from ingen.logger import init_logging

logger = logging.getLogger()


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="path to config file")
    parser.add_argument(
        "run_date",
        nargs="?",
        default=date.today(),
        help="run date in format MMDDYYYY",
        type=lambda d: datetime.strptime(d, "%m%d%Y"),
    )
    parser.add_argument(
        "--query_params",
        nargs="*",
        action=KeyValue,
        help="key value pairs to replace in sql queries",
    )
    parser.add_argument(
        "--interfaces", help="comma separated list of interfaces to generate"
    )
    parser.add_argument(
        "--infile",
        type=str,
        help="overwrite path of a file when `use_infile` is turned on in a file source",
    )
    return parser


if __name__ == "__main__":
    """Initializes logger and arguments"""
    init_logging()
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()
    if args.interfaces is not None:
        args.interfaces = args.interfaces.split(",")
    if args.infile:
        logger.info(
            f"Use $infile when source use_infile is turned on, overwrite source file_path: {args.infile}"
        )
    main(
        args.config_path, args.query_params, args.run_date, args.interfaces, args.infile
    )
