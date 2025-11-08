import datetime
from typing import Protocol, Self, TypeVar

import pydantic as pdt
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_pg
from sqlmodel import Field, SQLModel

from plexus.common.utils.datautils import validate_dt_timezone
from plexus.common.utils.jsonutils import json_datetime_encoder

__all__ = [
    "compare_postgresql_types",
    "validate_model_extended",
    "collect_model_tables",
    "model_copy_from",
    "make_base_model",
    "make_serial_model_mixin",
    "make_record_model_mixin",
    "make_snapshot_model_mixin",
    "serial_model_mixin",
    "record_model_mixin",
    "snapshot_model_mixin",
    "SerialModel",
    "RecordModel",
    "SnapshotModel",
    "make_snapshot_model_trigger",
]

ModelT = TypeVar("ModelT", bound=SQLModel)
ModelU = TypeVar("ModelU", bound=SQLModel)


def compare_postgresql_types(type_a, type_b) -> bool:
    """
    Compares two Postgresql-specific column types to determine if they are equivalent.
    This includes types from sqlalchemy.dialects.postgresql like ARRAY, JSON, UUID, etc.
    """
    if not isinstance(type_a, type(type_b)):
        return False
    if isinstance(type_a, sa_pg.ARRAY):
        return compare_postgresql_types(type_a.item_type, type_b.item_type)
    if isinstance(type_a, (sa_pg.VARCHAR, sa_pg.CHAR, sa_pg.TEXT)):
        return type_a.length == type_b.length
    if isinstance(type_a, (sa_pg.TIMESTAMP, sa_pg.TIME)):
        return type_a.timezone == type_b.timezone
    if isinstance(type_a, sa_pg.NUMERIC):
        return type_a.precision == type_b.precision and type_a.scale == type_b.scale
    return type(type_a) in {
        sa_pg.BOOLEAN,
        sa_pg.INTEGER,
        sa_pg.BIGINT,
        sa_pg.SMALLINT,
        sa_pg.FLOAT,
        sa_pg.DOUBLE_PRECISION,
        sa_pg.REAL,
        sa_pg.DATE,
        sa_pg.UUID,
        sa_pg.JSON,
        sa_pg.JSONB,
        sa_pg.HSTORE,
    }


def validate_model_extended(model_base: type[SQLModel], model_extended: type[SQLModel]) -> bool:
    """
    Validates if `model_extended` is an extension of `model_base` by checking if all fields in `model_base`
    are present in `model_extended` with compatible types.

    :param model_base: The base model class to compare against.
    :param model_extended: The model class that is expected to extend the base model.
    :return: True if `model_extended` extends `model_base` correctly, False otherwise.
    """
    columns_a = {column.name: column.type for column in model_base.__table__.columns}
    columns_b = {column.name: column.type for column in model_extended.__table__.columns}

    for field_a, field_a_type in columns_a.items():
        field_b_type = columns_b.get(field_a)
        if field_b_type is None or not compare_postgresql_types(field_a_type, field_b_type):
            return False
    return True


def collect_model_tables(*models: ModelT) -> sa.MetaData:
    metadata = sa.MetaData()
    for base in models:
        for table in base.metadata.tables.values():
            table.to_metadata(metadata)
    return metadata


def model_copy_from(dst: ModelT, src: ModelU, **kwargs) -> ModelT:
    if not isinstance(dst, SQLModel) or not isinstance(src, SQLModel):
        raise TypeError("both 'dst' and 'src' must be instances of SQLModel or its subclasses")

    for field, value in src.model_dump(**kwargs).items():
        if field not in dst.model_fields:
            continue
        # Skip fields that are not present in the destination model
        if value is None and dst.model_fields[field].required:
            raise ValueError(f"field '{field}' is required but got None")

        # Only set the field if it exists in the destination model
        if hasattr(dst, field):
            # If the field is a SQLModel, recursively copy it
            if isinstance(value, SQLModel):
                value = model_copy_from(getattr(dst, field), value, **kwargs)
            elif isinstance(value, list) and all(isinstance(item, SQLModel) for item in value):
                value = [model_copy_from(dst_item, src_item, **kwargs)
                         for dst_item, src_item in zip(getattr(dst, field), value)]

        setattr(dst, field, value)

    return dst


def make_base_model() -> type[SQLModel]:
    """
    Creates a base SQLModel class with custom metadata and JSON encoding for datetime fields.
    Use this as a base for all models that require these configurations.
    """

    class BaseModel(SQLModel):
        metadata = sa.MetaData()
        model_config = pdt.ConfigDict(json_encoders={datetime.datetime: json_datetime_encoder})

    return BaseModel


class SerialModelMixinProto(Protocol):
    sid: int | None


def make_serial_model_mixin() -> type[SerialModelMixinProto]:
    """
    Creates a mixin class for SQLModel models that adds a unique identifier field `sid`.
    Use this mixin to add an auto-incremented primary key to your models.
    """

    class ModelMixin(SQLModel):
        sid: int | None = Field(
            sa_column=sa.Column(sa_pg.BIGINT, primary_key=True, autoincrement=True),
            default=None,
            description="Unique auto-incremented primary key for the record",
        )

    return ModelMixin


class RecordModelMixinProto(Protocol):
    sid: int | None
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None

    @classmethod
    def make_index_created_at(cls, index_name: str) -> sa.Index:
        """
        Helper to create an index on the `created_at` field with the given index name.
        :param index_name: Name of the index to create.
        :return: The created SQLAlchemy Index object.
        """
        ...


def make_record_model_mixin() -> type[RecordModelMixinProto]:
    """
    Creates a mixin class for SQLModel models that adds common fields and validation logic for updatable records.
    This mixin includes `sid`, `created_at`, and `updated_at` fields, along with validation for timestamps.
    """

    class ModelMixin(SQLModel):
        sid: int | None = Field(
            sa_column=sa.Column(sa_pg.BIGINT, primary_key=True, autoincrement=True),
            default=None,
            description="Unique auto-incremented primary key for the record",
        )
        created_at: datetime.datetime | None = Field(
            sa_column=sa.Column(sa_pg.TIMESTAMP(timezone=True)),
            default=None,
            description="Timestamp (with timezone) when the record was created",
        )
        updated_at: datetime.datetime | None = Field(
            sa_column=sa.Column(sa_pg.TIMESTAMP(timezone=True)),
            default=None,
            description="Timestamp (with timezone) when the record was last updated",
        )

        @pdt.field_validator("created_at", mode="after")
        @classmethod
        def validate_created_at(cls, v: datetime.datetime) -> datetime.datetime:
            if v is not None:
                validate_dt_timezone(v)
            return v

        @pdt.field_validator("updated_at", mode="after")
        @classmethod
        def validate_updated_at(cls, v: datetime.datetime) -> datetime.datetime:
            if v is not None:
                validate_dt_timezone(v)
            return v

        @pdt.model_validator(mode="after")
        @classmethod
        def validate_created_at_updated_at(cls, m: Self) -> Self:
            if m.created_at is not None and m.updated_at is not None and m.created_at > m.updated_at:
                raise ValueError(f"create time '{m.created_at}' is greater than update time '{m.updated_at}'")
            return m

        @classmethod
        def make_index_created_at(cls, index_name: str) -> sa.Index:
            return sa.Index(index_name, "created_at")

    return ModelMixin


class SnapshotModelMixinProto(Protocol):
    sid: int | None
    created_at: datetime.datetime | None
    expired_at: datetime.datetime | None
    record_sid: int | None

    @classmethod
    def make_index_created_at_expired_at(cls, index_name: str) -> sa.Index:
        """
        Helper to create an index on the `created_at` and `expired_at` fields with the given index name.
        :param index_name: Name of the index to create.
        :return: The created SQLAlchemy Index object.
        """
        ...

    @classmethod
    def make_active_unique_index_record_sid(cls, index_name: str) -> sa.Index:
        """
        Helper to create a unique index on the `record_sid` field for active records (where `expired_at` is NULL).
        This ensures that there is only one active snapshot per record at any given time.
        :param index_name: Name of the index to create.
        :return: The created SQLAlchemy Index object.
        """
        ...

    @classmethod
    def make_active_unique_index_for(cls, index_name: str, *fields: str) -> sa.Index:
        """
        Helper to create a unique index on the specified fields for active records (where `expired_at` is NULL).
        This ensures that there is only one active snapshot per combination of the specified fields at any given
        time.
        :param index_name: Name of the index to create.
        :param fields: Fields to include in the unique index.
        :return: The created SQLAlchemy Index object.
        """
        ...


def make_snapshot_model_mixin() -> type[SnapshotModelMixinProto]:
    """
    Provides a mixin class for SQLModel models that adds common fields and validation logic for record snapshots.
    A snapshot model tracks the full change history of an entity: when any field changes, the current record (with a
    NULL expiration time) is updated to set its expiration time, and a new record with the updated values is created.

    The mixin includes the following fields:
      - `sid`: Unique, auto-incremented primary key identifying each snapshot of the record in the change history.
      - `created_at`: Time (with timezone) when this snapshot of the record was created and became active.
      - `expired_at`: Time (with timezone) when this snapshot of the record was superseded or became inactive;
        `None` if still active.
      - `record_sid`: Foreign key to the record this snapshot belongs to; used to link snapshots together.
    """

    class ModelMixin(SQLModel):
        sid: int | None = Field(
            sa_column=sa.Column(sa_pg.BIGINT, primary_key=True, autoincrement=True),
            default=None,
            description="Unique auto-incremented primary key for each record snapshot",
        )
        created_at: datetime.datetime | None = Field(
            sa_column=sa.Column(sa_pg.TIMESTAMP(timezone=True)),
            default=None,
            description="Timestamp (with timezone) when this record snapshot became active",
        )
        expired_at: datetime.datetime | None = Field(
            sa_column=sa.Column(sa_pg.TIMESTAMP(timezone=True)),
            default=None,
            description="Timestamp (with timezone) when this record snapshot became inactive; None if still active",
        )
        record_sid: int | None = Field(
            sa_column=sa.Column(sa_pg.BIGINT, nullable=True),
            default=None,
            description="Foreign key to the record this snapshot belongs to",
        )

        @pdt.field_validator("created_at", mode="after")
        @classmethod
        def validate_created_at(cls, v: datetime.datetime) -> datetime.datetime:
            if v is not None:
                validate_dt_timezone(v)
            return v

        @pdt.field_validator("expired_at", mode="after")
        @classmethod
        def validate_expired_at(cls, v: datetime.datetime) -> datetime.datetime:
            if v is not None:
                validate_dt_timezone(v)
            return v

        @pdt.model_validator(mode="after")
        @classmethod
        def validate_created_at_expired_at(cls, m: Self) -> Self:
            if m.created_at is not None and m.expired_at is not None and m.created_at > m.expired_at:
                raise ValueError(f"create time '{m.created_at}' is greater than expire time '{m.expired_at}'")
            return m

        @classmethod
        def make_index_created_at_expired_at(cls, index_name: str) -> sa.Index:
            return sa.Index(index_name, "created_at", "expired_at")

        @classmethod
        def make_active_unique_index_record_sid(cls, index_name: str) -> sa.Index:
            return sa.Index(
                index_name,
                "record_sid",
                unique=True,
                postgresql_where=sa.text('"expired_at" IS NULL'),
            )

        @classmethod
        def make_active_unique_index_for(cls, index_name: str, *fields: str) -> sa.Index:
            return sa.Index(
                index_name,
                *fields,
                unique=True,
                postgresql_where=sa.text('"expired_at" IS NULL'),
            )

    return ModelMixin


serial_model_mixin = make_serial_model_mixin()
record_model_mixin = make_record_model_mixin()
snapshot_model_mixin = make_snapshot_model_mixin()


class SerialModel(make_base_model(), make_serial_model_mixin(), table=True):
    pass


class RecordModel(make_base_model(), make_record_model_mixin(), table=True):
    pass


class SnapshotModel(make_base_model(), make_snapshot_model_mixin(), table=True):
    pass


def make_snapshot_model_trigger(engine: sa.Engine, model: type[SQLModel]):
    table_name = model.__tablename__
    if not table_name:
        raise ValueError("missing '__tablename__' attribute")

    if not validate_model_extended(SnapshotModel, model):
        raise ValueError("not an extended model of 'SnapshotModel'")

    record_sid_seq_name = f"{table_name}_record_sid_seq"
    snapshot_auto_update_function_name = f"{table_name}_snapshot_auto_update_function"
    snapshot_auto_update_trigger_name = f"{table_name}_snapshot_auto_update_trigger"

    # language=postgresql
    create_record_sid_seq_sql = f"""
        CREATE SEQUENCE "{record_sid_seq_name}"
        START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
    """

    # language=postgresql
    create_snapshot_auto_update_function_sql = f"""
        CREATE FUNCTION "{snapshot_auto_update_function_name}"()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW."record_sid" IS NULL THEN
                NEW."record_sid" := nextval('{record_sid_seq_name}');
            END IF;

            IF NEW."created_at" IS NULL THEN
                NEW."created_at" := CURRENT_TIMESTAMP;
            END IF;

            IF NEW."record_sid" IS NOT NULL THEN
                UPDATE "{table_name}"
                SET "expired_at" = NEW."created_at"
                WHERE "record_sid" = NEW."record_sid" AND "expired_at" IS NULL;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """

    # language=postgresql
    create_snapshot_auto_update_trigger_sql = f"""
        CREATE TRIGGER "{snapshot_auto_update_trigger_name}"
        BEFORE INSERT ON "{table_name}"
        FOR EACH ROW
        EXECUTE FUNCTION "{snapshot_auto_update_function_name}"();
    """

    with engine.connect() as conn:
        conn.execute(sa.text(create_record_sid_seq_sql))
        conn.execute(sa.text(create_snapshot_auto_update_function_sql))
        conn.execute(sa.text(create_snapshot_auto_update_trigger_sql))
        conn.commit()
