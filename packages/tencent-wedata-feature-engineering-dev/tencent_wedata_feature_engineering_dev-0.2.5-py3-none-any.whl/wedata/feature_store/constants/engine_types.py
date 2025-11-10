import warnings
from wedata.common.constants.engine_types import (EngineTypes as _EngineTypes,
                                                  CalculateEngineTypes as _CalculateEngineTypes,
                                                  judge_engine_type as _judge_engine_type)

warnings.warn("engine_types.py is deprecated, please use wedata.common.constants.engine_types.py")

EngineTypes = _EngineTypes

CalculateEngineTypes = _CalculateEngineTypes

judge_engine_type = _judge_engine_type
