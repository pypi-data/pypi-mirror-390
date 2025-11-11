from typing import Literal, TypeAlias

PandasFreqency: TypeAlias = Literal[
    "B", "C", "D", "W", "W-MON", "W-TUE", "W-WED", "W-THU", "W-FRI", "W-SAT", "W-SUN",
    "M", "MS", "Q", "QS", "A", "AS",
    "H", "T", "min", "S", "L", "ms", "U", "us", "N",
    "BH", "CBH", "BQS", "BA", "BAS", "BYS", "BY"
]
