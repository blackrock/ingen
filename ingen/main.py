#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import argparse
import logging
import time
from datetime import date
from datetime import datetime

from ingen.metadata.metadata_parser import MetaDataParser
from ingen.utils.utils import KeyValue
from ingen.logger import init_logging

log = logging.getLogger()


def main(config_path, query_params, run_date, interfaces, infile=None, dynamic_data=None):
    parser = MetaDataParser(config_path, query_params, run_date, interfaces, infile, dynamic_data)
    metadata_list = parser.parse_metadata()
    run_config = parser.run_config
    failed_interfaces = []  # Array to store the names of failed interfaces
    log.info("Metadata parsing complete. Starting interface generation")
    main_start = time.time()
    for metadata in metadata_list:
        try:
            generator = run_config.generator(run_config.writer, run_config.formatter)
            log.info(f"Generating interface '{metadata.name}'")
            start = time.time()
            interface = generator.generate(metadata.name, metadata.sources, metadata.pre_processes, metadata.columns,
                                           metadata.output, metadata.params, metadata.validation_action)
            end = time.time()
            log.info(f"Successfully generated interface '{metadata.name}' in {end - start:.2f} seconds.")
        except Exception as e:
            failed_interfaces.append(metadata.name)  # append the name of failed interfaces in a list
            log.error(f"Failed to generate interface file for {metadata.name} \n {e}")
    main_end = time.time()
    log.info(f"Interface Generation finished. Time taken: {main_end - main_start:.2f} seconds")

    if failed_interfaces:
        exit(f"Error while generating interface file for {failed_interfaces}")
    # dynamic_data: a JSON string input that was provided alongside a config file
    if dynamic_data:
        return interface


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path')
    parser.add_argument('run_date', nargs='?', default=date.today())
    parser.add_argument('--query_params', nargs='*', action=KeyValue)
    parser.add_argument('--interfaces')
    parser.add_argument('--infile', type=str, help="filepath")
    return parser


def init(arguments):
    init_logging()
    log.info("I'm here")
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args(arguments)
    if args.interfaces is not None:
        args.interfaces = args.interfaces.split(',')
    if type(args.run_date) == str:
        args.run_date = datetime.strptime(args.run_date, '%m%d%Y')
    if args.infile:
        log.info(f"Use poller $infile when source use_infile is turned on, overwrite source file_path: {args.infile}")
    main(args.config_path, args.query_params, args.run_date, args.interfaces, args.infile)


def process_json(config_path, dynamic_data):
    return main(config_path, None, None, None, dynamic_data=dynamic_data)
