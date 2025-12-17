import json
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


# cleaning
def clean_completion(text: str):
    clean = text

    # for nuextract tiny
    if text.startswith("### Template:"):
        clean = text.replace("### Template:", "")

    # for llama 1B
    for t in text.split("```"):
        if t.startswith("json"):
            clean = t[4:]
            break

    return clean


def tsv_to_data(text: str):
    lines = text.strip().split("\n")

    if not lines:
        return None

    headers = lines[0].strip().split("\t")

    if not headers:
        return None

    data = []
    if len(lines) < 2:
        return data

    for line in lines[1:]:
        values = line.strip().split("\t")
        row_dict = dict(zip(headers[: len(values)], values))
        data.append(row_dict)

    return data


def json_to_data(text: str):
    try:
        data = json.loads(text)
        if len(data):
            return data
    except Exception as error:
        logger.error(f"Error parsing json: {error}")
        return None
    return None


formatters_func = {"json": json_to_data, "tsv": tsv_to_data}
