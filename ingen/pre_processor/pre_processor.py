#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
import time

from ingen.pre_processor.aggregator import Aggregator
from ingen.pre_processor.drop_duplicates import DropDuplicates
from ingen.pre_processor.filter import Filter
from ingen.pre_processor.mask import Mask
from ingen.pre_processor.melt import Melt
from ingen.pre_processor.merger import Merger
from ingen.pre_processor.union import Union

log = logging.getLogger()


class PreProcessor:
    PRE_PROCESSORS = {
        "merge": Merger,
        "union": Union,
        "aggregate": Aggregator,
        "mask": Mask,
        "melt": Melt,
        "drop_duplicates": DropDuplicates,
        "filter": Filter
    }

    def __init__(self, pre_processes, source_data):
        self._pre_processes = pre_processes
        self._sources_data = source_data
        if len(source_data) < 1:
            raise ValueError('Source data cannot be empty')
        self._data = list(self._sources_data.values())[0]

    def pre_process(self):
        if self._pre_processes is not None:
            # if pre processing is needed, do that and return the processed data
            for pre_process in self._pre_processes:
                processor = self.get_processor(pre_process)
                log.info(f"Starting pre-processing step: {pre_process}")
                start = time.time()
                self._data = processor.execute(pre_process, self._sources_data, self._data)
                end = time.time()
                log.info(f"{pre_process} pre-processing step completed in {end - start:.2f} seconds")
        return self._data

    def get_processor(self, pre_process):
        pre_processor = self.PRE_PROCESSORS.get(pre_process.get("type"))
        if pre_processor is not None:
            return pre_processor()
        else:
            raise NameError(f'pre-processing {pre_process["type"]} is not recognized')
