import pandas as pd  # type: ignore
from pydantic import BaseModel, ConfigDict


class SecData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    color: str
    data: pd.DataFrame
    coefficient: int = 1

    def valid(self) -> bool:
        return not self.data.empty
