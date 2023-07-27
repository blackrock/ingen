import unittest
from unittest.mock import patch

import pandas as pd

from ingen.reader.api_reader import APIReader
from ingen.utils.app_http.HTTPRequest import HTTPRequest


class TestAPIReader(unittest.TestCase):

    def setUp(self):
        self.auth = {
            'type': 'BasicAuth',
            'username': 'TEST_USER',
            'pwd': 'TEST_PWD'
        }

    @patch('ingen.reader.api_reader.execute_requests')
    def test_array_response(self, mock_execute_requests):
        mock_response = [
            {
                "name": "abc",
                "rolno": 1
            },
            {
                "name": "def",
                "rolno": 2
            }
        ]
        mock_execute_requests.return_value = [mock_response]

        expected_data = pd.DataFrame(
            {
                "name": ["abc", "def"],
                "rolno": [1, 2]
            })
        requests = [HTTPRequest(url="www.abc.com", auth=self.auth, method="GET")]
        reader = APIReader(requests)
        data = reader.execute()
        pd.testing.assert_frame_equal(expected_data, data)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_nested_response_when_data_key_empty(self, mock_execute_requests):
        mock_json = [
            {
                "type": "ModelPortfolioDto",
                "productType": "MODEL_PORTFOLIO_DATA",
                "classifications": [{
                    "classificationCode": "MPU_MES",
                    "classificationId": 0000,
                    "description": "MPS - MPU_MES (Model Portfolio)",
                    "descriptionValue": "MPS - MPU_MES (Model Portfolio)",
                    "domainCode": "UMB",
                    "domainId": 8,
                    "levelNumber": 1,
                    "treeCode": "MPU_MES",
                    "treeId": "0101"
                }]
            }
        ]
        expected_data = pd.DataFrame({
            "classificationCode": ["MPU_MES"],
            "classificationId": [0000],
            "description": ["MPS - MPU_MES (Model Portfolio)"],
            "descriptionValue": ["MPS - MPU_MES (Model Portfolio)"],
            "domainCode": ["UMB"],
            "domainId": [8],
            "levelNumber": [1],
            "treeCode": ["MPU_MES"],
            "treeId": ["0101"]
        })
        requests = [HTTPRequest(url="http://www.test-url.com", method="GET", auth=self.auth)]
        mock_execute_requests.return_value = [mock_json]
        source = {
            'data_node': ["classifications"],
        }

        reader = APIReader(requests)
        data = reader.execute(data_node=source['data_node'])
        pd.testing.assert_frame_equal(expected_data, data)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_nested_response_when_data_node_empty(self, mock_execute_requests):
        mock_json = [
            {
                "type": "ModelPortfolioDto",
                "productType": "MODEL_PORTFOLIO_DATA",
                "attributesByCodeMap": {
                    "FOA_flg": {
                        "attributeTranslation": "N",
                        "attributeTypeCode": "FOA_flg",
                        "attributeValue": "N"
                    },
                    "invest_obj": {
                        "attributeTranslation": "TOTRET",
                        "attributeTypeCode": "invest_obj",
                        "attributeValue": "TOTRET"
                    }
                }
            }
        ]
        expected_data = pd.DataFrame({
            "type": ["ModelPortfolioDto"],
            "productType": ["MODEL_PORTFOLIO_DATA"],
            "attributesByCodeMap.FOA_flg.attributeTranslation": ["N"]
        })
        requests = [HTTPRequest(url="http://www.test-url.com", method="GET", auth=self.auth)]
        source = {
            'data_key': ["type", "productType", "attributesByCodeMap.FOA_flg.attributeTranslation"],
        }
        mock_execute_requests.return_value = [mock_json]
        reader = APIReader(requests)
        data = reader.execute(data_key=source['data_key'])
        pd.testing.assert_frame_equal(expected_data, data)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_nested_response(self, mock_execute_requests):
        mock_json = [
            {
                "type": "ModelPortfolioDto",
                "productType": "MODEL_PORTFOLIO_DATA",
                "classifications": [
                    {
                        "classificationCode": "MPU_MES",
                        "anotherDataPoint": "sample"
                    },
                    {
                        "classificationCode": "XYX"
                    },
                    {
                        "classificationCode": "PQR"
                    }
                ]
            }
        ]
        expected_data = pd.DataFrame({
            "classificationCode": ["MPU_MES", "XYX", "PQR"]
        })
        requests = [HTTPRequest(url="http://www.test-url.com", method="GET", auth=self.auth)]
        source = {
            'data_node': ["classifications"],
            'data_key': ["classificationCode"]
        }
        mock_execute_requests.return_value = [mock_json]
        reader = APIReader(requests)
        data = reader.execute(source['data_node'], source['data_key'])
        pd.testing.assert_frame_equal(expected_data, data)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_combine_list_responses(self, mock_execute_requests):
        requests = [HTTPRequest(url="url1", method="GET", auth=self.auth),
                    HTTPRequest(url="url2", method="GET", auth=self.auth)]
        responses = [
            [{"name": "Abhijeet", "age": 24}, {"name": "Ananya", "age": 26}],
            [{"name": "Sukanya", "age": 32}]
        ]
        expected_dataframe = pd.DataFrame({
            "name": ["Abhijeet", "Ananya", "Sukanya"],
            "age": [24, 26, 32]
        })
        mock_execute_requests.return_value = responses
        reader = APIReader(requests)
        actual_dataframe = reader.execute()
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_combine_simple_json_objects(self, mock_execute_requests):
        requests = [HTTPRequest(url="url1", method="GET", auth=self.auth),
                    HTTPRequest(url="url2", method="GET", auth=self.auth)]
        responses = [
            {"name": "Abhijeet", "age": 24}, {"name": "Ananya", "age": 26},
            {"name": "Sukanya", "age": 32}
        ]
        expected_dataframe = pd.DataFrame({
            "name": ["Abhijeet", "Ananya", "Sukanya"],
            "age": [24, 26, 32]
        })
        mock_execute_requests.return_value = responses
        reader = APIReader(requests)
        actual_dataframe = reader.execute()
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_response_with_meta_field(self, mock_execute_requests):
        requests = [HTTPRequest(url="url1", method="GET", auth=self.auth),
                    HTTPRequest(url="url2", method="GET", auth=self.auth)]
        responses = [
            {"student_name": "Abhijeet", "age": 24,
             "subjects": [{"name": "maths", "marks": 90}, {"name": "science", "marks": 78}]},
            {"student_name": "Ananya", "age": 26,
             "subjects": [{"name": "maths", "marks": 69}, {"name": "geography", "marks": 68}]},
            {"student_name": "Sukanya", "age": 32,
             "subjects": [{"name": "maths", "marks": 70}, {"name": "botany", "marks": 78}]}
        ]
        expected_dataframe = pd.DataFrame({
            "name": ["maths", "science", "maths", "geography", "maths", "botany"],
            "marks": [90, 78, 69, 68, 70, 78],
            "student_name": ["Abhijeet", "Abhijeet", "Ananya", "Ananya", "Sukanya", "Sukanya"]
        })
        mock_execute_requests.return_value = responses
        reader = APIReader(requests)
        source = {
            'data_node': ['subjects'],
            'data_key': ['name', 'marks'],
            'meta': ['student_name']
        }
        actual_dataframe = reader.execute(data_node=['subjects'], data_key=source['data_key'], meta=source['meta'])
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_response_with_meta_field_and_data_key(self, mock_execute_requests):
        requests = [HTTPRequest(url="url1", method="GET", auth=self.auth),
                    HTTPRequest(url="url2", method="GET", auth=self.auth)]
        responses = [
            {"student_name": "Abhijeet", "age": 24,
             "subjects": [{"name": "maths", "marks": 90}, {"name": "science", "marks": 78}]},
            {"student_name": "Ananya", "age": 26,
             "subjects": [{"name": "maths", "marks": 69}, {"name": "geography", "marks": 68}]},
            {"student_name": "Sukanya", "age": 32,
             "subjects": [{"name": "maths", "marks": 70}, {"name": "botany", "marks": 78}]}
        ]
        expected_dataframe = pd.DataFrame({
            "name": ["maths", "science", "maths", "geography", "maths", "botany"],
            "student_name": ["Abhijeet", "Abhijeet", "Ananya", "Ananya", "Sukanya", "Sukanya"]
        })
        mock_execute_requests.return_value = responses
        reader = APIReader(requests)
        source = {
            'data_node': ['subjects'],
            'data_key': ['name'],
            'meta': ['student_name']
        }
        actual_dataframe = reader.execute(data_node=['subjects'], data_key=source['data_key'], meta=source['meta'])
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_response_with_nested_meta_field(self, mock_execute_requests):
        requests = [HTTPRequest(url="url1", method="GET", auth=self.auth),
                    HTTPRequest(url="url2", method="GET", auth=self.auth)]
        responses = [
            {"student_details": {"student_name": "Abhijeet", "age": 24},
             "subjects": [{"name": "maths", "marks": 90}, {"name": "science", "marks": 78}]},
            {"student_details": {"student_name": "Ananya", "age": 26},
             "subjects": [{"name": "maths", "marks": 69}, {"name": "geography", "marks": 68}]},
            {"student_details": {"student_name": "Sukanya", "age": 32},
             "subjects": [{"name": "maths", "marks": 70}, {"name": "botany", "marks": 78}]}
        ]
        expected_dataframe = pd.DataFrame({
            "name": ["maths", "science", "maths", "geography", "maths", "botany"],
            "marks": [90, 78, 69, 68, 70, 78],
            "student_details.student_name": ["Abhijeet", "Abhijeet", "Ananya", "Ananya", "Sukanya", "Sukanya"]
        })
        mock_execute_requests.return_value = responses
        reader = APIReader(requests)
        source = {
            'data_node': ['subjects'],
            'data_key': ['name', 'marks'],
            'meta': [['student_details', 'student_name']]
        }
        actual_dataframe = reader.execute(data_node=['subjects'], data_key=source['data_key'], meta=source['meta'])
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_combine_string_responses(self, mock_execute_requests):
        requests = [HTTPRequest(url="url1", method="GET", auth=self.auth),
                    HTTPRequest(url="url2", method="GET", auth=self.auth)]
        responses = ["result1", "result2"]
        expected_dataframe = pd.DataFrame(responses)
        mock_execute_requests.return_value = responses
        reader = APIReader(requests)
        actual_dataframe = reader.execute(self.auth)
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_combine_list_of_string_responses(self, mock_execute_requests):
        requests = [HTTPRequest(url="url1", method="GET", auth=self.auth),
                    HTTPRequest(url="url2", method="GET", auth=self.auth)]
        responses = [["result1", "result1.2"], ["result2", "result2.2"]]
        expected_dataframe = pd.DataFrame(["result1", "result1.2", "result2", "result2.2"])
        mock_execute_requests.return_value = responses
        reader = APIReader(requests)
        actual_dataframe = reader.execute()
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_combine_responses_with_response_to_list(self, mock_execute_requests):
        requests = [HTTPRequest(url="http://www.test-url.com", method="GET", auth=self.auth)]
        responses = [{
            "bee12159-9fb9-4440-ae51-2c8f00312813": {
                "firmName": "David",
                "accInfoAccNumber": "238792374"
            },
            "bee12159-9fb9-4440-ae51-2348sd723": {
                "firmName": "Jones",
                "accInfoAccNumber": "234798237"
            }
        }]
        expected_dataframe = pd.DataFrame({
            "firmName": ["David", "Jones"],
            "accInfoAccNumber": ["238792374", "234798237"]
        })
        mock_execute_requests.return_value = responses
        reader_params = {
            'response_to_list': True
        }
        reader = APIReader(requests, reader_params)
        actual_dataframe = reader.execute()
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_combine_responses_with_response_to_list_multiple(self, mock_execute_requests):
        requests = [HTTPRequest(url="http://www.test-url.com/1", method="GET", auth=self.auth),
                    HTTPRequest(url="http://www.test-url.com/2", method="GET", auth=self.auth)]
        responses = [{
            "bee12159-9fb9-4440-ae51-2c8f00312813": {
                "firmName": "David",
                "accInfoAccNumber": "238792374"
            },
            "bee12159-9fb9-4440-ae51-2348sd723": {
                "firmName": "Jones",
                "accInfoAccNumber": "234798237"
            }
        }, {
            "ant12159-9fb9-4440-ae51-2c8f00312813": {
                "firmName": "Michael",
                "accInfoAccNumber": "238792374"
            },
            "pig12159-9fb9-4440-ae51-2348sd723": {
                "firmName": "Kelly",
                "accInfoAccNumber": "234798237"
            }
        }]

        expected_dataframe = pd.DataFrame({
            "firmName": ["David", "Jones", "Michael", "Kelly"],
            "accInfoAccNumber": ["238792374", "234798237", "238792374", "234798237"]
        })
        mock_execute_requests.return_value = responses
        reader_params = {
            'response_to_list': True
        }
        reader = APIReader(requests, reader_params)
        actual_dataframe = reader.execute()
        pd.testing.assert_frame_equal(expected_dataframe, actual_dataframe)

    @patch('ingen.reader.api_reader.execute_requests')
    def test_empty_result(self, mock_execute_requests):
        requests = [HTTPRequest(url="http://www.test-url.com", method="GET", auth=self.auth)]
        empty_response = []
        empty_dataframe = pd.DataFrame()
        mock_execute_requests.return_value = empty_response
        reader = APIReader(requests)
        actual_dataframe = reader.execute()
        pd.testing.assert_frame_equal(empty_dataframe, actual_dataframe)


if __name__ == '__main__':
    unittest.main()
