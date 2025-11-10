import os
from collections.abc import Generator
from contextlib import AbstractContextManager
from typing import Literal

import sqlalchemy
from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session
from sqlalchemy.orm import mapped_column, relationship

__all__ = [
    "SerializationFormat",
    "BagTopic",
    "BagMessage",
    "BagSchema",
    "BagMessageDefinition",
    "BagMetadata",
    "BagReader",
    "BagWriter",
    "bag_reader",
    "bag_writer",
]

SerializationFormat = Literal["cdr", "cdr2", "json", "yaml"]

default_bag_db_file = "bag.db"


class BagBase(DeclarativeBase):
    pass


class BagSchema(BagBase):
    __tablename__ = "schema"

    schema_version: Mapped[int] = mapped_column(Integer, primary_key=True)
    ros_distro: Mapped[str] = mapped_column(String, nullable=False)


class BagMetadata(BagBase):
    __tablename__ = "metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metadata_version: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_text: Mapped[str] = mapped_column(String, nullable=False)


class BagTopic(BagBase):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    serialization_format: Mapped[str] = mapped_column(String, nullable=False)
    type_description_hash: Mapped[str] = mapped_column(String, nullable=False)

    messages: Mapped[list["BagMessage"]] = relationship("BagMessage", back_populates="topic")


class BagMessageDefinition(BagBase):
    __tablename__ = "message_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_type: Mapped[str] = mapped_column(String, nullable=False)
    encoding: Mapped[str] = mapped_column(String, nullable=False)
    encoded_message_definition: Mapped[str] = mapped_column(String, nullable=False)
    type_description_hash: Mapped[str] = mapped_column(String, nullable=False)


class BagMessage(BagBase):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    topic: Mapped["BagTopic"] = relationship("BagTopic", back_populates="messages")


class BagReader(AbstractContextManager):
    def __init__(self, db_dir: str, db_file: str = default_bag_db_file):
        self.db_path = os.path.join(db_dir, db_file)
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"could not find SQLite DB at '{db_dir}'")

        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_path}")
        self.session = Session(self.engine)
        self.topic_map = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def get_topics(self) -> dict[str, BagTopic]:
        if self.topic_map is None:
            stmt = select(BagTopic)
            self.topic_map = {db_topic.name: db_topic for db_topic in self.session.scalars(stmt).all()}
        return self.topic_map

    def iter_messages(
        self,
        topic_names: list[str] | None = None,
        begin_timestamp: int | None = None,
        end_timestamp: int | None = None,
    ) -> Generator[BagMessage, None, None]:
        stmt = select(BagMessage)
        if topic_names is not None:
            topic_ids = [db_topic.id for db_topic in self.get_topics().values() if db_topic.name in topic_names]
            stmt = stmt.where(BagMessage.topic_id.in_(topic_ids))
        if begin_timestamp is not None:
            stmt = stmt.where(BagMessage.timestamp >= begin_timestamp)
        if end_timestamp is not None:
            stmt = stmt.where(BagMessage.timestamp <= end_timestamp)
        for db_message in self.session.scalars(stmt.order_by(BagMessage.timestamp)):
            yield db_message


class BagWriter(AbstractContextManager):
    def __init__(self, db_dir: str, db_file: str = default_bag_db_file):
        self.db_path = os.path.join(db_dir, db_file)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_path}")
        self.session = sqlalchemy.orm.Session(self.engine)
        self.topic_map = {}

        BagBase.metadata.create_all(self.engine)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        self.session.commit()
        self.session.close()
        self.engine.dispose()

    def get_or_create_topic(
        self,
        topic_name: str,
        topic_type: str,
        *,
        serialization_format: SerializationFormat = "cdr",
    ) -> BagTopic:
        if topic_name in self.topic_map:
            return self.topic_map[topic_name]

        db_topic = self.session.query(BagTopic).filter(BagTopic.name == topic_name).first()
        if db_topic is None:
            db_topic = BagTopic(name=topic_name,
                                type=topic_type,
                                serialization_format=serialization_format,
                                type_description_hash="")
            self.session.add(db_topic)
            self.session.flush()

        self.topic_map[topic_name] = db_topic
        self.session.commit()

        return db_topic

    def write_message(
        self,
        topic_name: str,
        timestamp: int,
        data: bytes,
        topic_type: str = None,
        *,
        serialization_format: SerializationFormat = "cdr",
    ) -> BagMessage:
        if topic_name not in self.topic_map:
            if topic_type is None:
                raise ValueError(f"missing topic type to create topic '{topic_name}' dynamically")

            self.get_or_create_topic(topic_name, topic_type, serialization_format=serialization_format)

        db_topic = self.topic_map[topic_name]
        db_message = BagMessage(topic_id=db_topic.id, timestamp=timestamp, data=data)

        self.session.add(db_message)
        self.session.flush()

        return db_message


def bag_reader(db_dir: str, db_file: str = default_bag_db_file) -> BagReader:
    """
    Creates a BagReader instance to read messages from a ROS2 bag file.

    :param db_dir: directory containing the SQLite DB file.
    :param db_file: name of the SQLite DB file.
    :return: BagReader instance.
    """
    return BagReader(db_dir, db_file)


def bag_writer(db_dir: str, db_file: str = default_bag_db_file) -> BagWriter:
    """
    Creates a BagWriter instance to write messages to a ROS2 bag file.

    :param db_dir: directory to store the SQLite DB file.
    :param db_file: name of the SQLite DB file.
    :return: BagWriter instance.
    """
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return BagWriter(db_dir, db_file)
