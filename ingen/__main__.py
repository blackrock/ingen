#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import argparse
import logging
import time
from datetime import date

from ingen.metadata.metadata_parser import MetaDataParser
from ingen.utils.utils import KeyValue
from ingen.logger import init_logging

logger = logging.getLogger()


def main(
    config_path, query_params, run_date, interfaces, infile=None, dynamic_data=None
):
    parser = MetaDataParser(
        config_path, query_params, run_date, interfaces, infile, dynamic_data
    )
    metadata_list = parser.parse_metadata()
    run_config = parser.run_config
    logger.info("Metadata parsing complete. Starting interface generation")
    main_start = time.time()
    for metadata in metadata_list:
        try:
            generator = run_config.generator(run_config.writer, run_config.formatter)
            logger.info(f"Generating interface '{metadata.name}'")
            start = time.time()
            interface = generator.generate(
                metadata.name,
                metadata.sources,
                metadata.pre_processes,
                metadata.columns,
                metadata.output,
                metadata.params,
                metadata.validation_action,
            )
            end = time.time()
            logger.info(
                f"Successfully generated interface '{metadata.name}' in {end - start:.2f} seconds."
            )
        except Exception as e:
            logger.error(
                f"Failed to generate interface file for {metadata.name} \n {e}"
            )
    main_end = time.time()
    logger.info(
        f"Interface Generation finished. Time taken: {main_end - main_start:.2f} seconds"
    )

    # dynamic_data: a JSON string input that was provided alongside a config file
    if dynamic_data:
        return interface


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="Path to config file")
    parser.add_argument(
        "run_date",
        nargs="?",
        default=date.today(),
        help="Run date in YYYY-MM-DD format, if provided "
        "this will override today's date in "
        "formatters",
    )
    parser.add_argument(
        "--query_params",
        nargs="*",
        action=KeyValue,
        help="Query parameters in key value pairs to be " "used in the SQL query",
    )
    parser.add_argument(
        "--interfaces",
        help="Comma separated list of interface names to generate, if not provided "
        "all interfaces listed in the config file will be generated",
    )
    parser.add_argument(
        "--infile", help="filepath to the JSON file to be used in JSON source"
    )
    return parser


def process_json(config_path, dynamic_data):
    return main(config_path, None, None, None, dynamic_data=dynamic_data)


if __name__ == "__main__":
    """Initializes logger and command line arguments"""
    init_logging()
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()
    if args.interfaces is not None:
        args.interfaces = args.interfaces.split(",")
    if args.infile:
        logger.info(
            f"Use poller $infile when source use_infile is turned on, overwrite source file_path: {args.infile}"
        )
    main(
        args.config_path, args.query_params, args.run_date, args.interfaces, args.infile
    )
