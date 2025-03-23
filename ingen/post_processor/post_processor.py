import logging
import time
import pandas as pd

from ingen.post_processor.common_post_processor import pivot_to_dynamic_columns

log = logging.getLogger()

class PostProcessor:

    POST_PROCESSORS={
        'pivot': pivot_to_dynamic_columns
    }

    def __init__(self, post_processes, formatted_data):
        self._post_processes = post_processes
        self._formatted_data = formatted_data

    def apply_post_processing(self):
        if self._post_processes is not None:
            if not isinstance(self._formatted_data, pd.DataFrame):
                raise TypeError('Source data must be a dataframe')
            if len(self._formatted_data) < 1:
                raise ValueError('Source data cannot be empty')
            # if post-processing is needed, do that and return the processed data
            for post_process in self._post_processes:
                processor_func = self.get_processor_func(post_process)
                log.info(f"Starting post-processing step: {post_process}")
                start = time.time()
                self._formatted_data = processor_func(self._formatted_data, post_process.get("processing_values"))
                end = time.time()
                log.info(f"{post_process} post-processing step completed in {end-start:.2f} seconds")
        return self._formatted_data

    def get_processor_func(self, post_process):
        post_processor = self.POST_PROCESSORS.get(post_process.get("type"))
        if post_processor is None:
            raise NameError(f'post-processing {post_process["type"]} is not recognized')
        return post_processor
