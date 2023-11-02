#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.


import logging
import time

from ingen.metadata.metadata_parser import MetaDataParser


logger = logging.getLogger()


def main(
    config_path, query_params, run_date, interfaces, infile=None, dynamic_data=None
):
    """Main function to parse metadata and generate interfaces"""
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


def process_json(config_path, dynamic_data):
    return main(config_path, None, None, None, dynamic_data=dynamic_data)
