#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pandas as pd

from ingen.pre_processor.filter import Filter


class TestDFFilter:
    def test_filter_by_columnwise_and(self):
        config = {
            'operator': 'and',
            'cols': [{'col': 'name', 'val': ['Ashish', 'Aman']},
                     {'col': 'score', 'val': [82]}
                     ]
        }

        data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'score': [50, 75, 82, 93, 77],
            'subject': ['Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })

        expected_data = pd.DataFrame({
            'name': ['Ashish'],
            'score': [82],
            'subject': ['Hindi']
        })

        pre_processor = Filter()
        actual_data = pre_processor.execute(config, sources_data=[data], data=data)
        pd.testing.assert_frame_equal(expected_data.reset_index(drop=True), actual_data.reset_index(drop=True))

    def test_filter_by_columnwise_or(self):
        config = {
            'operator': 'or',
            'cols': [{'col': 'name', 'val': ['Ashish']},
                     {'col': 'score', 'val': [75, 82]}
                     ]
        }

        data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'score': [50, 75, 82, 93, 77],
            'subject': ['Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })

        expected_data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Ashish'],
            'score': [50, 75, 82],
            'subject': ['Science', 'Hindi', 'Hindi']
        })

        pre_processor = Filter()
        actual_data = pre_processor.execute(config, sources_data=[data], data=data)
        pd.testing.assert_frame_equal(expected_data.reset_index(drop=True), actual_data.reset_index(drop=True))
