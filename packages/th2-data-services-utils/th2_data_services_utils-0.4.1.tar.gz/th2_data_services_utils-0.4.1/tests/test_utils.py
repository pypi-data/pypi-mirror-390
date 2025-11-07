from typing import List

# from th2_data_services.utils.pandas.aggregate import aggregate_by_fields
from th2_data_services.utils.pandas.utils import search_fields, append_total_rows, delete_string_by_pattern, find_tag_in_string


def test_search_fields_with_general_body(general_body: dict):
    fields = search_fields(general_body, "OrdType", "OrderCapacity", "PartyID")

    assert fields == {
        "OrdType": [{"columns": {"fieldValue": "2"}, "type": "row"}],
        "OrderCapacity": [{"columns": {"fieldValue": "A"}, "type": "row"}],
        "PartyID": [
            {"columns": {"fieldValue": "DEMO-CONN1"}, "type": "row"},
            {"columns": {"fieldValue": "0"}, "type": "row"},
            {"columns": {"fieldValue": "0"}, "type": "row"},
            {"columns": {"fieldValue": "3"}, "type": "row"},
        ],
    }


def test_search_fields_with_complex_body(complex_body: List[dict]):
    fields = search_fields(complex_body, "CumQty", "OrdType")

    assert fields == {
        "CumQty": [
            {
                "actual": "0",
                "expected": "0",
                "key": False,
                "operation": "EQUAL",
                "status": "PASSED",
                "type": "field",
            }
        ],
        "OrdType": [
            {
                "actual": "2",
                "expected": "2",
                "key": False,
                "operation": "EQUAL",
                "status": "PASSED",
                "type": "field",
            }
        ],
    }


# def test_append_total_rows_not_change(data_for_analyzing: List[dict]):
#     statistics = aggregate_by_fields(
#         data_for_analyzing, "eventName", "type", "successful"
#     )
#
#     statistics_with_total = append_total_rows(statistics, {"count": "sum"})
#     statistics_without_total = append_total_rows(statistics, {})
#
#     assert not statistics_with_total.equals(statistics_without_total)
#
#
# def test_append_total_rows(data_for_analyzing: List[dict]):
#     statistics = aggregate_by_fields(
#         data_for_analyzing, "eventName", "type", "successful"
#     )
#     statistics = append_total_rows(statistics, {"count": "sum"})
#
#     assert statistics.to_dict() == {
#         "count": {
#             ("heartbeat", "Heartbeat", False): 2.0,
#             ("heartbeat", "Heartbeat", True): 1.0,
#             ("heartbeat", "Heartbeat", "total"): 3.0,
#             ("message", "Send message", False): 1.0,
#             ("message", "Send message", "total"): 1.0,
#             ("message 333", "Receive message", False): 1.0,
#             ("message 333", "Receive message", "total"): 1.0,
#             ("message 333", "Send message", True): 1.0,
#             ("message 333", "Send message", "total"): 1.0,
#             ("message 444", "Receive message", False): 1.0,
#             ("message 444", "Receive message", True): 1.0,
#             ("message 444", "Receive message", "total"): 2.0,
#             ("message 444", "Send message", True): 1.0,
#             ("message 444", "Send message", "total"): 1.0,
#             ("message122", "Receive message", True): 1.0,
#             ("message122", "Receive message", "total"): 1.0,
#             ("message122", "Send message", True): 1.0,
#             ("message122", "Send message", "total"): 1.0,
#             ("message123", "Receive message", True): 1.0,
#             ("message123", "Receive message", "total"): 1.0,
#             ("message123", "Send message", True): 1.0,
#             ("message123", "Send message", "total"): 1.0,
#             ("test case 1", "Test Case", True): 1.0,
#             ("test case 1", "Test Case", "total"): 1.0,
#             ("test case 2", "Test Case", True): 1.0,
#             ("test case 2", "Test Case", "total"): 1.0,
#             ("test case 3", "Test Case", False): 1.0,
#             ("test case 3", "Test Case", "total"): 1.0,
#             ("test case 4", "Test Case", True): 1.0,
#             ("test case 4", "Test Case", "total"): 1.0,
#             ("test run 1", "Test Run", True): 1.0,
#             ("test run 1", "Test Run", "total"): 1.0,
#             ("test run 2", "Test Run", False): 1.0,
#             ("test run 2", "Test Run", "total"): 1.0,
#             ("test run 3", "Test Case", True): 1.0,
#             ("test run 3", "Test Case", "total"): 1.0,
#             ("test run 4", "Test Run", False): 1.0,
#             ("test run 4", "Test Run", "total"): 1.0,
#             ("verification", "Verification", True): 1.0,
#             ("verification", "Verification", "total"): 1.0,
#             ("verification32", "Verification", True): 1.0,
#             ("verification32", "Verification", "total"): 1.0,
#             ("verification33", "Verification", False): 1.0,
#             ("verification33", "Verification", "total"): 1.0,
#         }
#     }


def test_delete_string_by_pattern():
    string = "The test string with test tag."
    pattern = "string"

    assert delete_string_by_pattern(string, pattern) == "The test  with test tag."


def test_find_tag_in_string():
    string = "'Tag1': 'value1'\n 'Tag2': 'value2'\n 'Tag3: 'value3'"
    tag = "'Tag2'"

    assert find_tag_in_string(string, tag) == "value2"


