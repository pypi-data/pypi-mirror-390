
from typing import Union, List, Optional, Sequence, Any
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType


class AbstractBaseTableClient:

    @staticmethod
    def _normalize_params(
            param: Optional[Union[str, Sequence[str]]],
            default_type: type = list
    ) -> list:
        """统一处理参数标准化"""
        if param is None:
            return default_type()
        return list(param) if isinstance(param, Sequence) else [param]

    @staticmethod
    def _validate_schema(df: DataFrame, schema: StructType):
        """校验DataFrame和schema的有效性和一致性"""
        # 检查是否同时为空
        if df is None and schema is None:
            raise ValueError("Either DataFrame or schema must be provided")

        # 检查schema匹配
        if df is not None and schema is not None:
            df_schema = df.schema
            if df_schema != schema:
                diff_fields = set(df_schema.fieldNames()).symmetric_difference(set(schema.fieldNames()))
                raise ValueError(
                    f"DataFrame schema does not match. Differences: "
                    f"{diff_fields if diff_fields else 'field type mismatch'}"
                )

    @staticmethod
    def _validate_key_conflicts(primary_keys: List[str], timestamp_keys: str):
        """校验主键与时间戳键是否冲突"""
        if timestamp_keys in primary_keys:
            raise ValueError(f"Timestamp keys conflict with primary keys: {timestamp_keys}")

    @staticmethod
    def _validate_key_exists(primary_keys: List[str], timestamp_keys: str):
        """校验主键与时间戳键是否存在"""
        if not primary_keys:
            raise ValueError("Primary keys cannot be empty")
        if not timestamp_keys:
            raise ValueError("Timestamp keys cannot be empty")

    @staticmethod
    def _escape_sql_value(value: str) -> str:
        """转义SQL值中的特殊字符"""
        return value.replace("'", "''")

    @staticmethod
    def _check_sequence_element_type(sequence: Sequence[Any], element_type: type) -> bool:
        """检查序列中的元素是否为指定类型"""
        return all(isinstance(element, element_type) for element in sequence)
