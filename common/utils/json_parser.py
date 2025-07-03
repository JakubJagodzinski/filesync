from pydantic import ValidationError

from common.logger.log_types import LogType
from common.logger.logger import log


def safe_parse(model_class, data):
    try:
        model_instance = model_class.model_validate(data)
        return model_instance, None
    except ValidationError as e:
        log(
            LogType.ERROR,
            f"Validation error while parsing {model_class.__name__}: {e}"
        )
        return None, e
