#  Copyright 2023 Exactpro (Exactpro Systems Limited)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from collections import defaultdict
from re import sub, search
from typing import Union, List, Any, DefaultDict, Dict, Optional
from pandas import DataFrame, concat
from pandas.core.groupby import DataFrameGroupBy


def search_fields(
        data: Union[List[dict], dict], *fields: str
) -> DefaultDict[str, List[Any]]:
    """Search for fields.

    Args:
        data: Data.
        fields: Fields for search

    Returns:
        Dictionary with a list of found tags.
    """
    if not data:
        raise ValueError("Input data is empty.")
    if not fields:
        raise ValueError("Fields is empty.")

    found_fields = defaultdict(list)

    def __find_fields(piece_data: dict):
        for label, payload in piece_data.items():
            if label in fields:
                found_fields[label].append(payload)
            else:
                if isinstance(payload, dict):
                    __find_fields(payload)
                elif isinstance(payload, list):
                    for piece_payload in payload:
                        __find_fields(piece_payload)

    if isinstance(data, dict):
        data = [data]
    for piece in data:
        __find_fields(piece)

    return found_fields


def append_total_rows(
        data: DataFrameGroupBy, fields_options: Dict[str, str]
) -> Union[DataFrame, DataFrameGroupBy]:
    """Append total rows in data.

    Args:
        data: Data.
        fields_options: Aggregate function for total rows.

    Returns:
        DataFrame with total rows.
    """
    if fields_options:
        computes = []
        for field, option in fields_options.items():
            computes.append(
                data[field]
                    .unstack()
                    .assign(total=data[field].unstack().agg(option, axis=1))
                    .stack()
                    .to_frame(field)
            )
        return concat(computes, axis=1)
    else:
        return data


def delete_string_by_pattern(string: str, pattern: str) -> str:
    """Deletes string by pattern.

    Args:
        string: String for delete.
        pattern: Pattern.

    Returns:
        String with deleted pieces.
    """
    return sub(pattern, "", string)


def find_tag_in_string(data: str, search_tag: str) -> str:
    """Find tag value in record as string.

    Args:
        data: Record as string.
        search_tag: Tag for search.

    Returns:
        Tag value.
    """
    pattern = r"[\"']\S*[\"']"
    position = data.find(search_tag)
    if position != -1:
        position += len(search_tag)
        return search(pattern, data[position:]).group(0)[1:-1]
