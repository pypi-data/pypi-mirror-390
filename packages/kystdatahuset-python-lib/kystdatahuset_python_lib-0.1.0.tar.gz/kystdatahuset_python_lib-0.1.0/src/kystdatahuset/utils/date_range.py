from typing import List, Optional, Tuple

from datetime import datetime, timedelta
from kystdatahuset.types import PandasFreqency

def date_range2(start_date: datetime, end_date: datetime, freq: PandasFreqency) -> List[datetime]:
    """
    Generate a list of dates from start_date to end_date, inclusive.
    """
    if start_date > end_date:
        raise ValueError("start_date must be less than or equal to end_date")
    
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]