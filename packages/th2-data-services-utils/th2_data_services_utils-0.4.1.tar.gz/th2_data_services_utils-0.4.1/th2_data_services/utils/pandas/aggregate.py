#  Copyright 2023-2024 Exactpro (Exactpro Systems Limited)
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

# from functools import reduce
# from itertools import chain, cycle
from typing import Union, Iterable
# from typing import Optional

# import vaex
# from IPython.core.display import display_html
from pandas import DataFrame, Series, Grouper
# from pandas import concat
# from pandas.core.groupby import DataFrameGroupBy


# def aggregate_by_fields(
#         data: Union[Iterable[dict], DataFrame],
#         *fields: str,
#         total_row: bool = False,
#         pivot: Union[Iterable[str], str] = None,
# ) -> Union[DataFrame, DataFrameGroupBy]:
#     """Aggregates by fields using the lazy method.
#     The method need you if require to count fields or fields group.
#
#     Args:
#         data: Data.
#         fields: Fields for aggregate.
#         total_row: Adding a total row.
#         pivot: Which columns must is pivoted.
#
#     Returns:
#         Statistics.
#
#     Raises:
#         ValueError.
#     """
#     df = DataFrame(data)
#     if df.empty:
#         raise ValueError("Input data is empty.")
#     if not fields:
#         raise ValueError("Fields is empty.")
#
#     df: DataFrame = (
#         vaex.from_pandas(df)
#             .groupby(by=fields, agg="count", sort=True)
#             .to_pandas_df()
#             .set_index([*fields])
#     )
#
#     if pivot:
#         if isinstance(pivot, str):
#             pivot = (pivot,)
#         index = (field for field in fields if field not in pivot)
#         df = df.reset_index().pivot(index=index, columns=pivot, values="count")
#     if total_row:
#         index_length = len(df.index.names)
#         name = ("Total",) * index_length if index_length > 1 else "Total"
#         df.loc[name, :] = [
#             column.sum() if str(column.dtype) != "object" else "Total"
#             for _, column in df.items()
#         ]
#     return df


# def aggregate_several_group(
#         data: Iterable[dict], display_html_df: bool = True, receive_df: bool = False
# ) -> Optional[DataFrame]:
#     """Aggregates several groups in dataframe.
#     The method divided each field on separated groups.
#
#     Note:
#         The method can use DataFrame type for output and Html type for output.
#         If you use 'Jupyter Notebook' then use display_html_df = True else False.
#
#     Args:
#         data: Data.
#         display_html_df: Whether display to html.
#         receive_df: Whether to create dataframe.
#
#     Returns:
#         DataFrame with data divided into groups.
#
#     Raises:
#         ValueError.
#     """
#
#     if not data:
#         raise ValueError("Input data is empty.")
#
#     df = DataFrame(data)
#
#     results = []
#     for column in df.columns:
#         results.append(aggregate_by_fields(df, column, total_row=True).reset_index())
#
#     if display_html_df:
#         html_str = ""
#         for output, title in zip(results, chain(cycle([""]), cycle(["</br>"]))):
#             html_str += '<th style="text-align: center"><td style="vertical-align:top">'
#             html_str += f"<h2>{title}<h2>"
#             html_str += output.to_html().replace(
#                 "table", 'table style="display:inline"'
#             )
#             html_str += "</td><th>"
#         display_html(html_str, raw=True)
#
#     if receive_df:
#         result = reduce(
#             lambda main_df, another_df: concat([main_df, another_df], axis=1)
#             if len(main_df.index) > len(another_df.index)
#             else concat([another_df, main_df], axis=1),
#             results,
#         )
#         return result


# def aggregate_by_intervals_lazy(
#         data: Iterable[dict],
#         time_field: str,
#         agg: str = "count",
#         resolution: str = "D",
#         every: int = 1,
# ) -> DataFrame:
#     """Aggregates by time using lazy method.
#     The method only to count quantity records in intervals.
#
#     Args:
#         data: Data.
#         time_field: Time field.
#         agg: Aggregate function name.
#         resolution: Datetime suffix for intervals.
#         every: Frequently of intervals.
#
#     Returns:
#         Show all groups in dataframe.
#
#     Raises:
#         ValueError.
#     """
#     if not data:
#         raise ValueError("Input data is empty.")
#
#     dfv = vaex.from_pandas(DataFrame(data))
#     compute = dfv.groupby(
#         by=vaex.BinnerTime(
#             expression=time_field, df=dfv, resolution=resolution, every=every
#         ),
#         agg=agg,
#     ).to_pandas_df()
#
#     return compute


def aggregate_by_intervals(
        data: Iterable[dict],
        time_field: str,
        *fields: str,
        intervals: str = "Q",
        total_row: bool = False,
        pivot: Union[Iterable[str], str] = None,
) -> DataFrame:
    """Aggregates by fields with time intervals.
    The method count records and records groups in intervals.

    Args:
        data: Data.
        time_field: Time field.
        fields: Fields for aggregate.
        intervals: Intervals.
        total_row: Adding a total row.
        pivot: Which columns must is pivoted.

    Returns:
        Statistics.

    Raises:
        ValueError.
    """
    if not data:
        raise ValueError("Input data is empty.")
    if not fields:
        raise ValueError("Fields is empty")

    df = DataFrame(data=data)

    time: Series = df.get(time_field)
    if time.empty:
        raise ValueError(f"{time_field} is empty.")
    elif time.dtype != "datetime64[ns]":
        raise ValueError(f"{time_field} isn't of type datetime64[ns]")

    df = (
        df.filter(items=[time_field, *fields])
            .set_index(time_field)
            .groupby([Grouper(freq=intervals), *fields], sort=True)
            .size()
            .reset_index(name="count")
            .set_index([time_field, *fields])
    )

    if pivot:
        if isinstance(pivot, str):
            pivot = (pivot,)
        index = [time_field] + [field for field in fields if field not in pivot]
        df = df.reset_index().pivot(index=index, columns=pivot, values="count")
    if total_row:
        index_length = len(df.index.names)
        name = ("Total",) * index_length if index_length > 1 else "Total"
        df.loc[name, :] = [
            column.sum() if str(column.dtype) != "object" else "Total"
            for _, column in df.items()
        ]
    return df
