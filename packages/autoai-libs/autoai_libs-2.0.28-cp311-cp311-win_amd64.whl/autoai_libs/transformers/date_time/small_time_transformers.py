################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R, 5737-L65
# (c) Copyright IBM Corp. 2021-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
import numpy as np
import pandas as pd

from autoai_libs.transformers.small_data_column_transformer import SmallDataColumnTransformer

from datetime import datetime


class DayExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).day, *args, **kwargs)


class HourExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).hour, *args, **kwargs)


class DayOfWeekExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).dayofweek, *args, **kwargs)


class DayOfYearExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).dayofyear, *args, **kwargs)


class WeekExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).isocalendar().week, *args, **kwargs)


class MonthExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).month, *args, **kwargs)


class YearExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).year, *args, **kwargs)


class SecondExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).second, *args, **kwargs)


class MinuteExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: pd.to_datetime(x).minute, *args, **kwargs)


class DateToFloatTimestampTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: (pd.to_datetime(x).values.astype(float)), *args, **kwargs)


class DateToTimestampTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: (pd.to_datetime(x).values.astype(np.int64)), *args, **kwargs)


class TimestampExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: (pd.to_datetime(x).asi8), *args, **kwargs)


class FloatTimestampExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: (pd.to_datetime(x).asi8.astype(float)), *args, **kwargs)


class DatetimeExtractTransformer(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda x: (pd.to_datetime(x)), *args, **kwargs)


class FloatTimestampExtractTransformer32(SmallDataColumnTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(
            lambda x: (
                (pd.to_datetime(x).tz_localize(None) - datetime.utcfromtimestamp(0)).total_seconds().astype(np.float32)
            ),
            *args,
            **kwargs,
        )
