import pytest_postgresql.factories
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_pg
from iker.common.utils.dbutils import ConnectionMaker, Dialects, Drivers
from iker.common.utils.dbutils import make_scheme
from iker.common.utils.jsonutils import JsonType
from iker.common.utils.randutils import randomizer
from sqlmodel import Field

from plexus.common.utils.ormutils import make_base_model, make_snapshot_model_mixin, make_snapshot_model_trigger
from plexus.common.utils.ormutils import snapshot_model_mixin

fixture_postgresql_test_proc = pytest_postgresql.factories.postgresql_proc(host="localhost", user="postgres")
fixture_postgresql_test = pytest_postgresql.factories.postgresql("fixture_postgresql_test_proc", dbname="test")


class DummyModel(make_base_model(), make_snapshot_model_mixin(), table=True):
    __tablename__ = "dummy_model"

    dummy_str: str = Field(sa_column=sa.Column(sa_pg.VARCHAR(256)), default="")
    dummy_int: int = Field(sa_column=sa.Column(sa_pg.BIGINT), default=0)
    dummy_float: float = Field(sa_column=sa.Column(sa_pg.DOUBLE_PRECISION), default=0.0)
    dummy_bool: bool = Field(sa_column=sa.Column(sa_pg.BOOLEAN), default=False)
    dummy_array: list[str] = Field(sa_column=sa.Column(sa_pg.ARRAY(sa_pg.VARCHAR(64))))
    dummy_json: JsonType = Field(sa_column=sa.Column(sa_pg.JSONB))

    __table_args__ = (
        snapshot_model_mixin.make_index_created_at_expired_at("ix_dummy_model_created_at_expired_at"),
        snapshot_model_mixin.make_active_unique_index_record_sid("aux_dummy_model_record_sid"),
    )


def test_make_snapshot_model_trigger(fixture_postgresql_test_proc, fixture_postgresql_test):
    scheme = make_scheme(Dialects.postgresql, Drivers.psycopg)
    host = fixture_postgresql_test.info.host
    port = fixture_postgresql_test.info.port
    user = fixture_postgresql_test.info.user
    database = fixture_postgresql_test.info.dbname

    maker = ConnectionMaker.create(scheme,
                                   host,
                                   port,
                                   user,
                                   None,
                                   database,
                                   session_opts=dict(expire_on_commit=False))

    DummyModel.metadata.create_all(maker.engine)
    make_snapshot_model_trigger(maker.engine, DummyModel)

    rng = randomizer()

    def random_record(record_sid: int | None = None):
        if record_sid is None:
            return DummyModel(
                dummy_int=rng.next_int(0, 1000),
                dummy_str=rng.random_alphanumeric(rng.next_int(10, 20)),
                dummy_float=rng.next_float(0.0, 100.0),
                dummy_bool=rng.next_bool(),
                dummy_array=list(rng.random_ascii(rng.next_int(10, 20)) for _ in range(rng.next_int(10, 20))),
                dummy_json=rng.random_json_object(5),
            )
        else:
            return DummyModel(
                record_sid=record_sid,
                dummy_int=rng.next_int(0, 1000),
                dummy_str=rng.random_alphanumeric(rng.next_int(10, 20)),
                dummy_float=rng.next_float(0.0, 100.0),
                dummy_bool=rng.next_bool(),
                dummy_array=list(rng.random_ascii(rng.next_int(10, 20)) for _ in range(rng.next_int(10, 20))),
                dummy_json=rng.random_json_object(5),
            )

    with maker.make_session() as session:
        initial_records = [random_record() for _ in range(0, 1000)]
        session.add_all(initial_records)
        session.commit()

        for record in initial_records:
            session.refresh(record)

        count = session.query(sa.func.count()).select_from(DummyModel).scalar()

        assert count == 1000

        for i, initial_record in enumerate(initial_records):
            assert initial_record.sid == i + 1
            assert initial_record.record_sid == i + 1
            assert initial_record.created_at is not None
            assert initial_record.expired_at is None

        updated_records = [random_record(record_sid=i + 1) for i in range(0, 1000)]
        session.add_all(updated_records)
        session.commit()

        for record in updated_records:
            session.refresh(record)
        for record in initial_records:
            session.refresh(record)

        count = session.query(sa.func.count()).select_from(DummyModel).scalar()

        assert count == 2000

        for i, (initial_record, updated_record) in enumerate(zip(initial_records, updated_records)):
            assert initial_record.sid == i + 1
            assert initial_record.record_sid == i + 1
            assert updated_record.sid == initial_record.sid + 1000
            assert updated_record.record_sid == initial_record.record_sid
            assert initial_record.created_at is not None
            assert initial_record.expired_at == updated_record.created_at
            assert updated_record.expired_at is None
