import json
from typing import Any
from core.utils.logger import get_logger

logger = get_logger(__name__)


def tsv_to_data(text: str) -> dict[str, Any]:
    lines = text.strip().split("\n")
    if not lines:
        raise ValueError("No lines found in TSV text")

    headers = lines[0].strip().split("\t")
    if not headers:
        raise ValueError("No headers found in TSV text")

    data = {}
    if len(lines) < 2:
        raise ValueError("No data rows found in TSV text")

    for line in lines[1:]:
        values = line.strip().split("\t")
        row_dict = dict(zip(headers[: len(values)], values))
        for key, value in row_dict.items():
            if key not in data:
                data[key] = []
            data[key].append(value)

    return data


def json_to_data(text: str) -> dict[str, Any]:
    data = json.loads(text)
    return data


formatters_func = {"json": json_to_data, "tsv": tsv_to_data}
