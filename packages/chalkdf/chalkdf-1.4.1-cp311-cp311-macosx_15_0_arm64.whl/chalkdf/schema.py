from dataclasses import dataclass

import pyarrow as pa


@dataclass
class Schema:
    _schema_dict: dict[str, pa.DataType]

    def dtypes(self) -> list[pa.DataType]:
        return list(self._schema_dict.values())

    def len(self) -> int:
        return len(self._schema_dict)

    def names(self) -> list[str]:
        return list(self._schema_dict)
