#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.pre_processor.process import Process


class Mask(Process):
    def execute(self, config, sources_data, data):
        on_col = config['on_col']
        masking_col = config.get('masking_col')
        masking_data_name = config.get('masking_source')
        masking_data = sources_data.get(masking_data_name)

        return self.mask(data, on_col, masking_col, masking_data)

    def mask(self, data, on_col, masking_col, masking_data):
        mask_filter = data[on_col].isin(masking_data[masking_col])
        return data[mask_filter].reset_index(drop=True)
