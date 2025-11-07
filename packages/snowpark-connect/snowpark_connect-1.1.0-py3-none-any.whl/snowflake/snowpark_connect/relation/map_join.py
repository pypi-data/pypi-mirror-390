#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
import dataclasses
from collections.abc import Callable
from enum import Enum
from functools import reduce
from typing import Optional

import pyspark.sql.connect.proto.relations_pb2 as relation_proto
from pyspark.errors import AnalysisException

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark import DataFrame
from snowflake.snowpark.types import StructField, StructType
from snowflake.snowpark_connect.column_name_handler import (
    ColumnNames,
    ColumnQualifier,
    JoinColumnNameMap,
    make_unique_snowpark_name,
)
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.constants import COLUMN_METADATA_COLLISION_KEY
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.error.error_codes import ErrorCodes
from snowflake.snowpark_connect.error.error_utils import (
    SparkException,
    attach_custom_error_code,
)
from snowflake.snowpark_connect.expression.map_expression import (
    map_single_column_expression,
)
from snowflake.snowpark_connect.expression.typer import JoinExpressionTyper
from snowflake.snowpark_connect.relation.map_relation import (
    NATURAL_JOIN_TYPE_BASE,
    map_relation,
)
from snowflake.snowpark_connect.relation.read.metadata_utils import (
    without_internal_columns,
)
from snowflake.snowpark_connect.utils.context import (
    push_evaluating_join_condition,
    push_sql_scope,
    set_plan_id_map,
    set_sql_plan_name,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)

USING_COLUMN_NOT_FOUND_ERROR = "[UNRESOLVED_USING_COLUMN_FOR_JOIN] USING column `{0}` not found on the {1} side of the join. The {1}-side columns: {2}"


class ConditionType(Enum):
    USING_COLUMNS = 1
    JOIN_CONDITION = 2
    NO_CONDITION = 3


@dataclasses.dataclass
class JoinInfo:
    join_type: str
    condition_type: ConditionType
    join_columns: Optional[list[str]]
    just_left_columns: bool

    def is_using_columns(self):
        return self.condition_type == ConditionType.USING_COLUMNS


def map_join(rel: relation_proto.Relation) -> DataFrameContainer:
    left_container: DataFrameContainer = map_relation(rel.join.left)
    right_container: DataFrameContainer = map_relation(rel.join.right)

    # Remove any metadata columns(like metada$filename) present in the dataframes.
    # We cannot support inputfilename for multisources as each dataframe has it's own source.
    left_container = without_internal_columns(left_container)
    right_container = without_internal_columns(right_container)

    # if there are any conflicting snowpark columns, this is the time to rename them
    left_container, right_container = _disambiguate_snowpark_columns(
        left_container, right_container, rel
    )

    join_info = _get_join_info(rel, left_container, right_container)

    match join_info.condition_type:
        case ConditionType.JOIN_CONDITION:
            result_container = _join_using_condition(
                left_container, right_container, join_info, rel
            )
        case ConditionType.USING_COLUMNS:
            result_container = _join_using_columns(
                left_container, right_container, join_info
            )
        case _:
            result_container = _join_unconditionally(
                left_container, right_container, join_info
            )

    # Fix for USING join column references with different plan IDs
    # After a USING join, references to the right dataframe's columns should resolve
    # to the result dataframe that contains the merged columns
    if (
        join_info.is_using_columns()
        and rel.join.right.HasField("common")
        and rel.join.right.common.HasField("plan_id")
    ):
        right_plan_id = rel.join.right.common.plan_id
        set_plan_id_map(right_plan_id, result_container)

    # For FULL OUTER joins, we also need to map the left dataframe's plan_id
    # since both columns are replaced with a coalesced column
    if (
        join_info.is_using_columns()
        and join_info.join_type == "full_outer"
        and rel.join.left.HasField("common")
        and rel.join.left.common.HasField("plan_id")
    ):
        left_plan_id = rel.join.left.common.plan_id
        set_plan_id_map(left_plan_id, result_container)

    return result_container


def _join_unconditionally(
    left_container: DataFrameContainer,
    right_container: DataFrameContainer,
    info: JoinInfo,
) -> DataFrameContainer:
    if info.join_type != "cross" and not global_config.spark_sql_crossJoin_enabled:
        exception = SparkException.implicit_cartesian_product("inner")
        attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
        raise exception

    left_input = left_container.dataframe
    right_input = right_container.dataframe
    join_type = info.join_type

    # For outer joins without a condition, we need to use a TRUE condition
    # to match Spark's behavior.
    result: snowpark.DataFrame = left_input.join(
        right=right_input,
        on=snowpark_fn.lit(True)
        if join_type in ["left", "right", "full_outer"]
        else None,
        how=join_type,
    )

    columns = left_container.column_map.columns + right_container.column_map.columns
    column_metadata = _combine_metadata(left_container, right_container)

    if info.just_left_columns:
        columns = left_container.column_map.columns
        column_metadata = left_container.column_map.column_metadata
        result = result.select(*left_container.column_map.get_snowpark_columns())

    snowpark_columns = [c.snowpark_name for c in columns]

    return DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=[c.spark_name for c in columns],
        snowpark_column_names=snowpark_columns,
        column_metadata=column_metadata,
        column_qualifiers=[c.qualifiers for c in columns],
        cached_schema_getter=_build_joined_schema(
            snowpark_columns, left_input, right_input
        ),
    )


def _join_using_columns(
    left_container: DataFrameContainer,
    right_container: DataFrameContainer,
    info: JoinInfo,
) -> DataFrameContainer:
    join_columns = info.join_columns

    def _validate_using_column(
        column: str, container: DataFrameContainer, side: str
    ) -> None:
        if (
            container.column_map.get_snowpark_column_name_from_spark_column_name(
                column, allow_non_exists=True, return_first=True
            )
            is None
        ):
            exception = AnalysisException(
                USING_COLUMN_NOT_FOUND_ERROR.format(
                    column, side, container.column_map.get_spark_columns()
                )
            )
            attach_custom_error_code(exception, ErrorCodes.COLUMN_NOT_FOUND)
            raise exception

    for col in join_columns:
        _validate_using_column(col, left_container, "left")
        _validate_using_column(col, right_container, "right")

    left_input = left_container.dataframe
    right_input = right_container.dataframe

    # The inputs will have different snowpark names for the same spark name,
    # so we convert ["a", "b"] into (left["a"] == right["a"] & left["b"] == right["b"]),
    # then drop right["a"] and right["b"].
    snowpark_using_columns = [
        (
            snowpark_fn.col(
                left_container.column_map.get_snowpark_column_name_from_spark_column_name(
                    spark_name, return_first=True
                )
            ),
            snowpark_fn.col(
                right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                    spark_name, return_first=True
                )
            ),
        )
        for spark_name in join_columns
    ]

    # this is a condition join, so it will contain left + right columns
    # we need to postprocess this later to have a correct projection
    joined_df = left_input.join(
        right=right_input,
        on=reduce(
            snowpark.Column.__and__,
            (left == right for left, right in snowpark_using_columns),
        ),
        how=info.join_type,
    )

    # figure out default column ordering after the join
    columns = left_container.column_map.get_columns_after_join(
        right_container.column_map, join_columns, info.join_type
    )

    if info.join_type in ["full_outer", "left", "right"]:
        all_columns_for_select = []
        all_column_names = []

        for column_info in columns[: len(join_columns)]:
            spark_name = column_info.spark_name
            left_sp_name = left_container.column_map.get_snowpark_column_name_from_spark_column_name(
                spark_name, return_first=True
            )
            right_sp_name = right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                spark_name, return_first=True
            )

            if info.join_type == "full_outer":
                new_sp_name = make_unique_snowpark_name(spark_name)
                all_columns_for_select.append(
                    snowpark_fn.coalesce(
                        snowpark_fn.col(left_sp_name), snowpark_fn.col(right_sp_name)
                    ).alias(new_sp_name)
                )
                all_column_names.append(
                    ColumnNames(spark_name, new_sp_name, set(), is_hidden=False)
                )

                for sp_name, container in [
                    (left_sp_name, left_container),
                    (right_sp_name, right_container),
                ]:
                    all_columns_for_select.append(snowpark_fn.col(sp_name))
                    all_column_names.append(
                        ColumnNames(
                            spark_name,
                            sp_name,
                            container.column_map.get_qualifiers_for_spark_column(
                                spark_name
                            ),
                            is_hidden=True,
                        )
                    )
            else:
                for sp_name, container, side in [
                    (left_sp_name, left_container, "left"),
                    (right_sp_name, right_container, "right"),
                ]:
                    all_columns_for_select.append(snowpark_fn.col(sp_name))
                    qualifiers = container.column_map.get_qualifiers_for_spark_column(
                        spark_name
                    )
                    is_visible = info.join_type == side
                    if is_visible:
                        qualifiers = qualifiers | {ColumnQualifier(())}
                    all_column_names.append(
                        ColumnNames(
                            spark_name, sp_name, qualifiers, is_hidden=not is_visible
                        )
                    )

        for c in columns[len(join_columns) :]:
            all_columns_for_select.append(snowpark_fn.col(c.snowpark_name))
            all_column_names.append(c)

        result = joined_df.select(all_columns_for_select)
        snowpark_names_for_schema = [c.snowpark_name for c in columns]

        return DataFrameContainer.create_with_column_mapping(
            dataframe=result,
            spark_column_names=[c.spark_name for c in all_column_names],
            snowpark_column_names=[c.snowpark_name for c in all_column_names],
            column_metadata=_combine_metadata(left_container, right_container),
            column_qualifiers=[c.qualifiers for c in all_column_names],
            column_is_hidden=[c.is_hidden for c in all_column_names],
            cached_schema_getter=_build_joined_schema(
                snowpark_names_for_schema,
                left_input,
                right_input,
                all_column_names,
            ),
        )

    if info.just_left_columns:
        # we just need the left columns
        columns = columns[: len(left_container.column_map.columns)]
        snowpark_columns = [c.snowpark_name for c in columns]
        result = joined_df.select(*snowpark_columns)

        return DataFrameContainer.create_with_column_mapping(
            dataframe=result,
            spark_column_names=[c.spark_name for c in columns],
            snowpark_column_names=snowpark_columns,
            column_metadata=left_container.column_map.column_metadata,
            column_qualifiers=[c.qualifiers for c in columns],
            cached_schema_getter=_build_joined_schema(
                snowpark_columns, left_input, right_input
            ),
        )

    snowpark_columns = [c.snowpark_name for c in columns]
    result = joined_df.select(*snowpark_columns)
    return DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=[c.spark_name for c in columns],
        snowpark_column_names=snowpark_columns,
        column_metadata=_combine_metadata(left_container, right_container),
        column_qualifiers=[c.qualifiers for c in columns],
        cached_schema_getter=_build_joined_schema(
            snowpark_columns, left_input, right_input
        ),
    )


def _join_using_condition(
    left_container: DataFrameContainer,
    right_container: DataFrameContainer,
    info: JoinInfo,
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    left_columns = left_container.column_map.get_spark_columns()
    right_columns = right_container.column_map.get_spark_columns()

    left_input = left_container.dataframe
    right_input = right_container.dataframe

    # All PySpark join types are in the format of JOIN_TYPE_XXX.
    # We remove the first 10 characters (JOIN_TYPE_) and replace all underscores with spaces to match the exception.
    pyspark_join_type = relation_proto.Join.JoinType.Name(rel.join.join_type)[
        10:
    ].replace("_", " ")
    with push_sql_scope(), push_evaluating_join_condition(
        pyspark_join_type, left_columns, right_columns
    ):
        if left_container.alias is not None:
            set_sql_plan_name(left_container.alias, rel.join.left.common.plan_id)
        if right_container.alias is not None:
            set_sql_plan_name(right_container.alias, rel.join.right.common.plan_id)
        # resolve join condition expression
        _, join_expression = map_single_column_expression(
            rel.join.join_condition,
            column_mapping=JoinColumnNameMap(
                left_container.column_map,
                right_container.column_map,
            ),
            typer=JoinExpressionTyper(left_input, right_input),
        )

    result: snowpark.DataFrame = left_input.join(
        right=right_input,
        on=join_expression.col,
        how=info.join_type,
    )

    # column order is already correct, so we just take the left + right side list
    columns = left_container.column_map.columns + right_container.column_map.columns
    column_metadata = _combine_metadata(left_container, right_container)

    if info.just_left_columns:
        # we just need left-side columns
        columns = left_container.column_map.columns
        result = result.select(*[c.snowpark_name for c in columns])
        column_metadata = left_container.column_map.column_metadata

    snowpark_columns = [c.snowpark_name for c in columns]

    return DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=[c.spark_name for c in columns],
        snowpark_column_names=snowpark_columns,
        column_metadata=column_metadata,
        column_qualifiers=[c.qualifiers for c in columns],
        cached_schema_getter=_build_joined_schema(
            snowpark_columns, left_input, right_input
        ),
    )


def _get_join_info(
    rel: relation_proto.Relation, left: DataFrameContainer, right: DataFrameContainer
) -> JoinInfo:
    """
    Gathers basic information about the join, and performs basic assertions
    """

    is_natural_join = rel.join.join_type >= NATURAL_JOIN_TYPE_BASE
    join_columns = rel.join.using_columns
    if is_natural_join:
        rel.join.join_type -= NATURAL_JOIN_TYPE_BASE
        left_spark_columns = left.column_map.get_spark_columns()
        right_spark_columns = right.column_map.get_spark_columns()
        common_spark_columns = [
            x for x in left_spark_columns if x in right_spark_columns
        ]
        join_columns = common_spark_columns

    match rel.join.join_type:
        case relation_proto.Join.JOIN_TYPE_UNSPECIFIED:
            # TODO: Understand what UNSPECIFIED Join type is
            exception = SnowparkConnectNotImplementedError("Unspecified Join Type")
            attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
            raise exception
        case relation_proto.Join.JOIN_TYPE_INNER:
            join_type = "inner"
        case relation_proto.Join.JOIN_TYPE_FULL_OUTER:
            join_type = "full_outer"
        case relation_proto.Join.JOIN_TYPE_LEFT_OUTER:
            join_type = "left"
        case relation_proto.Join.JOIN_TYPE_RIGHT_OUTER:
            join_type = "right"
        case relation_proto.Join.JOIN_TYPE_LEFT_ANTI:
            join_type = "leftanti"
        case relation_proto.Join.JOIN_TYPE_LEFT_SEMI:
            join_type = "leftsemi"
        case relation_proto.Join.JOIN_TYPE_CROSS:
            join_type = "cross"
        case other:
            exception = SnowparkConnectNotImplementedError(f"Other Join Type: {other}")
            attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
            raise exception

    has_join_condition = rel.join.HasField("join_condition")
    is_using_columns = bool(join_columns)

    if join_type == "cross" and has_join_condition:
        # if the user provided any condition, it's no longer a cross join
        join_type = "inner"

    if has_join_condition:
        assert not is_using_columns

    condition_type = ConditionType.NO_CONDITION
    if has_join_condition:
        condition_type = ConditionType.JOIN_CONDITION
    elif is_using_columns:
        condition_type = ConditionType.USING_COLUMNS

    # Join types that only return columns from the left side:
    # - LEFT SEMI JOIN: Returns left rows that have matches in right table (no right columns)
    # - LEFT ANTI JOIN: Returns left rows that have NO matches in right table (no right columns)
    # Both preserve only the columns from the left DataFrame without adding any columns from the right.
    just_left_columns = join_type in ["leftanti", "leftsemi"]

    return JoinInfo(join_type, condition_type, join_columns, just_left_columns)


def _disambiguate_snowpark_columns(
    left: DataFrameContainer, right: DataFrameContainer, rel: relation_proto.Relation
) -> tuple[DataFrameContainer, DataFrameContainer]:
    conflicting_snowpark_columns = left.column_map.get_conflicting_snowpark_columns(
        right.column_map
    )

    if not conflicting_snowpark_columns:
        return left, right

    left_plan = rel.join.left.common.plan_id
    right_plan = rel.join.right.common.plan_id

    if left_plan == right_plan:
        # don't overwrite plan_id map for self joins
        right_plan = None

    # rename and create new right container
    # TODO: rename both sides after SNOW-2382499
    return left, _disambiguate_container(
        right, conflicting_snowpark_columns, right_plan
    )


def _disambiguate_container(
    container: DataFrameContainer,
    conflicting_snowpark_columns: set[str],
    plan_id: Optional[int],
) -> DataFrameContainer:
    column_map = container.column_map
    disambiguated_columns = []
    disambiguated_snowpark_names = []
    for c in column_map.columns:
        if c.snowpark_name in conflicting_snowpark_columns:
            # alias snowpark column with a new unique name
            new_name = make_unique_snowpark_name(c.spark_name)
            disambiguated_snowpark_names.append(new_name)
            disambiguated_columns.append(
                snowpark_fn.col(c.snowpark_name).alias(new_name)
            )
        else:
            disambiguated_snowpark_names.append(c.snowpark_name)
            disambiguated_columns.append(snowpark_fn.col(c.snowpark_name))

    disambiguated_df = container.dataframe.select(*disambiguated_columns)

    def _schema_getter() -> StructType:
        fields = container.dataframe.schema.fields
        return StructType(
            [
                StructField(name, fields[i].datatype, fields[i].nullable)
                for i, name in enumerate(disambiguated_snowpark_names)
            ]
        )

    disambiguated_container = DataFrameContainer.create_with_column_mapping(
        dataframe=disambiguated_df,
        spark_column_names=column_map.get_spark_columns(),
        snowpark_column_names=disambiguated_snowpark_names,
        column_metadata=column_map.column_metadata,
        column_qualifiers=column_map.get_qualifiers(),
        table_name=container.table_name,
        cached_schema_getter=_schema_getter,
    )

    # since we just renamed some snowpark columns, we need to update the dataframe container for the given plan_id
    # TODO: is there a better way to do this?
    if plan_id is not None:
        set_plan_id_map(plan_id, disambiguated_container)

    return disambiguated_container


def _combine_metadata(
    left_container: DataFrameContainer, right_container: DataFrameContainer
) -> dict:
    column_metadata = dict(left_container.column_map.column_metadata or {})
    if right_container.column_map.column_metadata:
        for key, value in right_container.column_map.column_metadata.items():
            if key not in column_metadata:
                column_metadata[key] = value
            else:
                # In case of collision, use snowpark's column's expr_id as prefix.
                # this is a temporary solution until SNOW-1926440 is resolved.
                try:
                    snowpark_name = right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                        key
                    )
                    expr_id = right_container.dataframe[
                        snowpark_name
                    ]._expression.expr_id
                    updated_key = COLUMN_METADATA_COLLISION_KEY.format(
                        expr_id=expr_id, key=snowpark_name
                    )
                    column_metadata[updated_key] = value
                except Exception:
                    # ignore any errors that happens while fetching the metadata
                    pass
    return column_metadata


def _build_joined_schema(
    snowpark_columns: list[str],
    left_input: DataFrame,
    right_input: DataFrame,
    outer_join_columns: Optional[list[ColumnNames]] = None,
) -> Callable[[], StructType]:
    """
    Builds a lazy schema for the joined dataframe, based on the given snowpark_columns and input dataframes.
    In case of full outer joins, we need a separate target_snowpark_columns, since join columns will have different
    names in the output than in any input.
    """

    def _schema_getter() -> StructType:
        all_fields = left_input.schema.fields + right_input.schema.fields
        fields: dict[str, StructField] = {f.name: f for f in all_fields}

        if outer_join_columns:
            visible_columns = [c for c in outer_join_columns if not c.is_hidden]
            assert len(snowpark_columns) == len(visible_columns)

            result_fields = []
            visible_idx = 0
            for col in outer_join_columns:
                if col.is_hidden:
                    source_field = fields[col.snowpark_name]
                    result_fields.append(
                        StructField(
                            col.snowpark_name,
                            source_field.datatype,
                            source_field.nullable,
                        )
                    )
                else:
                    source_field = fields[snowpark_columns[visible_idx]]
                    result_fields.append(
                        StructField(
                            col.snowpark_name,
                            source_field.datatype,
                            source_field.nullable,
                        )
                    )
                    visible_idx += 1

            return StructType(result_fields)

        return StructType(
            [
                StructField(name, fields[name].datatype, fields[name].nullable)
                for name in snowpark_columns
            ]
        )

    return _schema_getter
