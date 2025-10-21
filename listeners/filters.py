from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class FilterType(Enum):
    MULTI_SELECT = "multi_select"
    TOGGLE = "toggle"


@dataclass
class FilterOptions:
    name: str
    value: str


@dataclass
class Filter:
    name: str
    display_name: str
    type: FilterType
    display_name_plural: Optional[str] = None
    options: Optional[List[FilterOptions]] = None


LANGUAGES_FILTER = Filter(
    name="languages",
    display_name="Language",
    display_name_plural="Languages",
    type=FilterType.MULTI_SELECT.value,
    options=[
        FilterOptions(name="Python", value="python"),
        FilterOptions(name="Java", value="java"),
        FilterOptions(name="JavaScript", value="javascript"),
        FilterOptions(name="TypeScript", value="typescript"),
    ],
)

TEMPLATES_FILTER = Filter(name="template", display_name="Templates", type=FilterType.TOGGLE.value)


SAMPLES_FILTER = Filter(name="sample", display_name="Samples", type=FilterType.TOGGLE.value)
