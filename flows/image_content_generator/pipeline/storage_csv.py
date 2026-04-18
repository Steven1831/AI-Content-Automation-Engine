from enum import Enum
from pathlib import Path
from typing import Any, cast

import pandas as pd

from flows.image_content_generator.pipeline.schemas import IdeaRaw, State
from tools.common.csv_processor import CsvProcessor


class Column(str, Enum):
    ID = "id"
    TITLE = "title"
    STATE = "state"
    CATEGORY = "category"

# TODO: Solve casts


class CsvStore(CsvProcessor):
    """
    Adapter for the CSV storage for Image Content Generator.
    """

    def __init__(self, csv_path: Path):
        super().__init__(
            path=csv_path,
            required_columns=[col.value for col in Column]
        )

    def get_by_index(self, index: int) -> IdeaRaw:
        row = self.get_row(index)
        return self._map_row(row)

    def get_first_by_state(self, state: State) -> IdeaRaw | None:
        df = self.read_all()

        # Simplified casting: single Any cast on the index to handle dynamic lookup
        idx = cast(Any, df.index)[df[Column.STATE.value] == state.value]
        if len(idx) == 0:
            return None

        return self.get_by_index(int(idx[0]))

    def get_next_id(self) -> int:
        df = self.read_all()
        if df.empty:
            return 1

        # Simplified casting: single Any cast on the series for max() lookup
        max_id = cast(Any, df[Column.ID.value]).max()
        return int(max_id) + 1

    def add_new_idea(self, title: str, category: str) -> IdeaRaw:
        new_id = self.get_next_id()

        row_data: dict[str, Any] = {
            Column.ID.value: new_id,
            Column.TITLE.value: title,
            Column.STATE.value: State.NEW.value,
            Column.CATEGORY.value: category,
        }
        self.add_row(row_data)
        return self._map_row(pd.Series(row_data))

    def save(self, idea_obj: IdeaRaw) -> None:
        df = self.read_all()

        # Simplified casting: single Any cast on the index for ID lookup
        idx = cast(Any, df.index)[df[Column.ID.value] == idea_obj.id]
        if len(idx) == 0:
            raise ValueError(f"No idea found in storage with ID: {idea_obj.id}")

        row_index = int(idx[0])

        row_data: dict[str, Any] = {
            Column.ID.value: idea_obj.id,
            Column.TITLE.value: idea_obj.title,
            Column.STATE.value: idea_obj.state.value,
            Column.CATEGORY.value: idea_obj.category
        }
        self.update_row(row_index, row_data)

    def _map_row(self, row: Any) -> IdeaRaw:
        idea_id = int(row[Column.ID.value])

        # Create the object
        idea_obj = IdeaRaw(
            id=idea_id,
            title=row[Column.TITLE.value],
            state=row[Column.STATE.value],
            category=row[Column.CATEGORY.value],
        )
        return idea_obj
