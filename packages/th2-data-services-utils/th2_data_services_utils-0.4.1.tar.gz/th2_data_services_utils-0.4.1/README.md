[![](https://img.shields.io/badge/python-3.8+-g.svg)](https://www.python.org/downloads/)

# Since v0.4 this repo use DS-core v2 structure and can be used only with DS-core v2

Table of Contents
=================

<!--ts-->
* [Table of Contents](#table-of-contents)
* [1. Introduction](#1-introduction)
* [2. Getting started](#2-getting-started)
   * [2.1. Installation](#21-installation)
   * [2.2. Example](#22-example)
      * [2.2.1. Aggregating](#221-aggregating)
         * [aggregate_by_fields](#aggregate_by_fields)
         * [aggregate_several_group:](#aggregate_several_group)
         * [aggregate_by_intervals_lazy:](#aggregate_by_intervals_lazy)
         * [aggregate_by_intervals:](#aggregate_by_intervals)
   * [2.3. Links](#23-links)
* [3. API](#3-api)
<!--te-->

# 1. Introduction

This repository is a set of auxiliary functions for th2-data-services library helping to solve the most common task.

Common tasks:

* Aggregating data
* Creating graphs
* Searching
* And other.

# 2. Getting started

## 2.1. Installation

- From PyPI (pip)

This package can be found on [PyPI](https://pypi.org/project/th2-data-services-utils/ "th2-data-services-utils").

```
pip install th2-data-services-utils
```

- From Source

```
git clone https://github.com/th2-net/th2-data-services-utils
pip install th2-data-services-utils
```

## 2.2. Example

### 2.2.1. Aggregating

For our example, we're using this data.
```
raw_data = [
    {'attachedMessageIds': False, 'eventName': 'test run 1', 'successful': True,
        'time': datetime.datetime(2021, 1, 1, 1, 1, 1), 'type': 'Test Run'},
    {'attachedMessageIds': True, 'eventName': 'heartbeat', 'successful': True,
        'time': datetime.datetime(2021, 1, 1, 1, 10, 2), 'type': 'Heartbeat'},
    {'attachedMessageIds': False, 'eventName': 'test run 2', 'successful': False,
      'time': datetime.datetime(2021, 1, 1, 1, 2, 12), 'type': 'Test Run'},
      . . . . . 
]
```

#### aggregate_by_fields

A method aggregate records by fields. It's using Vaex library so using lazy method.

Here we group the data for 'type', 'successful' fields and count them.
```    
>> data = aggregate_by_fields(raw_data, "type", "successful")
                                count
type            successful
Heartbeat       False           2
                True            1
Receive message False           2
                True            3
Send message    False           1
                True            4
Test Case       False           1
                True            4
Test Run        False           2
                True            1
Verification    False           1
                True            2
```

We can add a total row to the table.
```
>> data_total = aggregate_by_fields(raw_data, "type", "successful", total_row=True)
                                count
type            successful
Heartbeat       False           2.0
                True            1.0
Receive message False           2.0
                True            3.0
Send message    False           1.0
                True            4.0
Test Case       False           1.0
                True            4.0
Test Run        False           2.0
                True            1.0
Verification    False           1.0
                True            2.0
Total           Total           24.0
```

Or we can rotate the field for comfortable viewing.
```
>> data_pivot = aggregate_by_fields(raw_data, "type", "successful", pivot="successful")

successful       False  True
type
Heartbeat            2      1
Receive message      2      3
Send message         1      4
Test Case            1      4
Test Run             2      1
Verification         1      2
```

#### aggregate_several_group:
A method aggregate each field in the data separately. 
It's using Pandas library so for the big data can be problems with performance. 
The method can use DataFrame type for output and Html type for output.

Here we aggregate all fields in the data. This example we use DataFrame type.
```
>> output = aggregate_several_group(raw_data, display_html_df=False, receive_df=True).fillna("-")

                   time count             type  ... count attachedMessageIds count
0   2021-01-01 01:01:01   1.0        Heartbeat  ...     9              False    10
1   2021-01-01 01:01:59   1.0  Receive message  ...    15               True    14
2   2021-01-01 01:02:12   1.0     Send message  ...    24              Total    24
3   2021-01-01 01:03:54   1.0        Test Case  ...     -                  -     -
4   2021-01-01 01:04:30   1.0         Test Run  ...     -                  -     -
5   2021-01-01 01:10:02   1.0     Verification  ...     -                  -     -
6   2021-01-01 01:11:11   1.0            Total  ...     -                  -     -
7   2021-01-01 01:13:40   1.0                -  ...     -                  -     -
8   2021-01-01 01:23:23   1.0                -  ...     -                  -     -
9   2021-01-01 01:32:42   1.0                -  ...     -                  -     -
10  2021-01-01 01:33:12   1.0                -  ...     -                  -     -
11  2021-01-01 01:33:33   1.0                -  ...     -                  -     -
12  2021-01-01 01:40:10   1.0                -  ...     -                  -     -
13  2021-01-01 01:41:19   1.0                -  ...     -                  -     -
14  2021-01-01 01:43:43   1.0                -  ...     -                  -     -
15  2021-01-01 01:44:44   1.0                -  ...     -                  -     -
16  2021-01-01 01:45:22   1.0                -  ...     -                  -     -
17  2021-01-01 01:54:52   1.0                -  ...     -                  -     -
18  2021-01-01 01:55:55   1.0                -  ...     -                  -     -
19  2021-01-01 01:56:32   1.0                -  ...     -                  -     -
20  2021-01-01 02:10:01   1.0                -  ...     -                  -     -
21  2021-01-01 02:12:11   1.0                -  ...     -                  -     -
22  2021-01-01 02:12:32   1.0                -  ...     -                  -     -
23  2021-01-01 02:33:01   1.0                -  ...     -                  -     -
24                Total  24.0                -  ...     -                  -     -
```

#### aggregate_by_intervals_lazy:
A method aggregate all records in intervals. It's using Vaex library so using lazy method.

Here we aggregate records at 30-minute intervals.
```
# resolution is time series. every is frequency.
# m - Minute
# h - Hour
# D - Day
# W - Week
# M - Month
# Y - Year
>> output = aggregate_by_intervals_lazy(data_for_analyzing, "time", resolution="m", every=30)

time  count
0 2021-01-01 01:02:00      7
1 2021-01-01 01:32:00     11
2 2021-01-01 02:02:00      3
3 2021-01-01 02:32:00      1
```

#### aggregate_by_intervals:
A method aggregate records by specified fields in intervals. 
It's using Pandas library so for the big data can be problems with performance.

Here we aggregate records at a minute intervals.
All alias intervals can be viewed [here](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).
Note that intervals of function aggregate_by_intervals_lazy and aggregate_by_intervals is different.
```
>> data = aggregate_by_intervals(data_for_analyzing, "time", "eventName", "type", intervals="1min")
                                                        count
time                eventName      type
2021-01-01 01:01:00 test case 3    Test Case            1
                    test run 1     Test Run             1
2021-01-01 01:02:00 test run 2     Test Run             1
2021-01-01 01:03:00 message        Send message         1
2021-01-01 01:04:00 test case 1    Test Case            1
2021-01-01 01:10:00 heartbeat      Heartbeat            1
2021-01-01 01:11:00 message 444    Receive message      1
2021-01-01 01:13:00 message123     Receive message      1
2021-01-01 01:23:00 message 333    Receive message      1
2021-01-01 01:32:00 test run 3     Test Case            1
2021-01-01 01:33:00 heartbeat      Heartbeat            1
                    test run 4     Test Run             1
2021-01-01 01:40:00 test case 4    Test Case            1
2021-01-01 01:41:00 message122     Receive message      1
2021-01-01 01:43:00 message 444    Send message         1
2021-01-01 01:44:00 message122     Send message         1
2021-01-01 01:45:00 verification32 Verification         1
2021-01-01 01:54:00 verification33 Verification         1
2021-01-01 01:55:00 message 333    Send message         1
2021-01-01 01:56:00 message 444    Receive message      1
2021-01-01 02:10:00 test case 2    Test Case            1
2021-01-01 02:12:00 heartbeat      Heartbeat            1
                    message123     Send message         1
2021-01-01 02:33:00 verification   Verification         1
```

Here we can also add a total row.
```
>> data = aggregate_by_intervals(data_for_analyzing, "time", "eventName", "type", intervals="min", total_row=True)
                                                        count
time                eventName      type
2021-01-01 01:01:00 test case 3    Test Case            1
                    test run 1     Test Run             1
2021-01-01 01:02:00 test run 2     Test Run             1
2021-01-01 01:03:00 message        Send message         1
2021-01-01 01:04:00 test case 1    Test Case            1
2021-01-01 01:10:00 heartbeat      Heartbeat            1
2021-01-01 01:11:00 message 444    Receive message      1
2021-01-01 01:13:00 message123     Receive message      1
2021-01-01 01:23:00 message 333    Receive message      1
2021-01-01 01:32:00 test run 3     Test Case            1
2021-01-01 01:33:00 heartbeat      Heartbeat            1
                    test run 4     Test Run             1
2021-01-01 01:40:00 test case 4    Test Case            1
2021-01-01 01:41:00 message122     Receive message      1
2021-01-01 01:43:00 message 444    Send message         1
2021-01-01 01:44:00 message122     Send message         1
2021-01-01 01:45:00 verification32 Verification         1
2021-01-01 01:54:00 verification33 Verification         1
2021-01-01 01:55:00 message 333    Send message         1
2021-01-01 01:56:00 message 444    Receive message      1
2021-01-01 02:10:00 test case 2    Test Case            1
2021-01-01 02:12:00 heartbeat      Heartbeat            1
                    message123     Send message         1
2021-01-01 02:33:00 verification   Verification         1
Total               Total          Total             24.0
```

Or we can rotate the field for comfortable viewing.
```
>> data = aggregate_by_intervals(data_for_analyzing, "time", "eventName", "type", intervals="min", pivot="type")

type                                Heartbeat  ...  Verification
time                eventName                  ...
2021-01-01 01:01:00 test case 3           NaN  ...           NaN
                    test run 1            NaN  ...           NaN
2021-01-01 01:02:00 test run 2            NaN  ...           NaN
2021-01-01 01:03:00 message               NaN  ...           NaN
2021-01-01 01:04:00 test case 1           NaN  ...           NaN
2021-01-01 01:10:00 heartbeat             1.0  ...           NaN
2021-01-01 01:11:00 message 444           NaN  ...           NaN
2021-01-01 01:13:00 message123            NaN  ...           NaN
2021-01-01 01:23:00 message 333           NaN  ...           NaN
2021-01-01 01:32:00 test run 3            NaN  ...           NaN
2021-01-01 01:33:00 heartbeat             1.0  ...           NaN
                    test run 4            NaN  ...           NaN
2021-01-01 01:40:00 test case 4           NaN  ...           NaN
2021-01-01 01:41:00 message122            NaN  ...           NaN
2021-01-01 01:43:00 message 444           NaN  ...           NaN
2021-01-01 01:44:00 message122            NaN  ...           NaN
2021-01-01 01:45:00 verification32        NaN  ...           1.0
2021-01-01 01:54:00 verification33        NaN  ...           1.0
2021-01-01 01:55:00 message 333           NaN  ...           NaN
2021-01-01 01:56:00 message 444           NaN  ...           NaN
2021-01-01 02:10:00 test case 2           NaN  ...           NaN
2021-01-01 02:12:00 heartbeat             1.0  ...           NaN
                    message123            NaN  ...           NaN
2021-01-01 02:33:00 verification          NaN  ...           1.0
```

## 2.3. Links

- [Th2 Data Services](https://github.com/th2-net/th2-data-services)
- [Pandas](https://pandas.pydata.org/docs/)
- [Vaex](https://vaex.io/docs/index.html)

# 3. API

If you are looking for functions description see the [API Documentation](documentation/api/index.md).