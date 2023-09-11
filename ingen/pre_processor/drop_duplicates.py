#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.pre_processor.process import Process


class DropDuplicates(Process):
    def execute(self, config, sources_data, data):
        columns = config.get('columns', data.columns)
        keep = config.get('keep', 'first')
        return self._drop_duplicates(data, columns, keep)

    def _drop_duplicates(self, data, columns, keep):
        return data.drop_duplicates(subset=columns, keep=keep, ignore_index=True)
