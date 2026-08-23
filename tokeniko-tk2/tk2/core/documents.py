"""The document bases — where a collection model declares what it IS.

A tk2 collection model inherits from one of the three bases below, and that choice is its
write-class declaration. It is made unforgettable on purpose: there is no default, and inheriting
`TkDocument` directly without declaring fails at import time rather than at the first write.

Shape comes from the mixins in `mixins.py`; the collection name and indexes come from bunnet's
`Settings`, exactly as tk1 does it:

    class HeartLevelDoc(KbDocument, Timestamped):
        sphere: str
        value: float

        class Settings:
            name = "heart_levels"
"""

from typing import ClassVar, NoReturn

from bunnet import Document

from tk2.core.write_class import WriteClass, WriteClassViolation


class TkDocument(Document):
    """The root of every tk2 collection model. Declares nothing itself — that is the point."""

    # Bases that exist to be inherited from, not to become collections. Deliberately read off
    # `cls.__dict__` below and never inherited, so forgetting to unset it cannot make a real
    # collection model invisible to the check.
    __tk_abstract__: ClassVar[bool] = True

    # Annotated without a value: a subclass that declares nothing has no attribute at all, which is
    # what the check below catches. ClassVar keeps pydantic from reading it as a field — the
    # write-class is a property of the COLLECTION, not a column repeated on every row.
    write_class: ClassVar[WriteClass]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.__dict__.get("__tk_abstract__", False):
            return
        if not hasattr(cls, "write_class"):
            raise TypeError(
                f"{cls.__name__} declares no write-class. Every tk2 collection model inherits from "
                f"KbDocument (rw), ParamDocument (r) or LogicDocument (r) — the declaration is the "
                f"seam the datatier enforces on, so there is no default to fall back to."
            )


class KbDocument(TkDocument):
    """The knowledge base: what he learns, and what happens to him. The body's only writable tier."""

    __tk_abstract__: ClassVar[bool] = True
    write_class: ClassVar[WriteClass] = WriteClass.KB


class _ReadOnlyDocument(TkDocument):
    """The r-classes' shared floor: every ODM write path is closed at the MODEL.

    The datatier's `assert_writable` already refuses these, and this is the second lock — the
    Captain's ruling of 2026-08-23. The datatier is a door, and a door only guards what walks
    through it; a caller holding a model can call `.save()` on it directly and never pass the
    datatier at all. Closing the methods themselves makes «an r-class collection has no public
    write path» structurally TRUE rather than procedurally observed.

    Every public writer is closed, not the four obvious ones: a single method left open is the whole
    lock. Migrations reach these collections through `tk2.datatier.migration_writer`, which does not
    use the ODM at all — a different door, not this one with the lock taken off.
    """

    __tk_abstract__: ClassVar[bool] = True

    @classmethod
    def _refuse(cls, method: str) -> NoReturn:
        raise WriteClassViolation(
            f"{cls.__name__}.{method}() refused: write-class "
            f"'{cls.write_class.value}' is read-only to the body. Change these rows with a "
            f"migration in `db/` — the running body picks the change up on the slow tick."
        )

    # --- instance writers ---
    def insert(self, *args, **kwargs) -> NoReturn:
        type(self)._refuse("insert")

    def save(self, *args, **kwargs) -> NoReturn:
        type(self)._refuse("save")

    def save_changes(self, *args, **kwargs) -> NoReturn:
        type(self)._refuse("save_changes")

    def replace(self, *args, **kwargs) -> NoReturn:
        type(self)._refuse("replace")

    def update(self, *args, **kwargs) -> NoReturn:
        type(self)._refuse("update")

    def set(self, *args, **kwargs) -> NoReturn:
        type(self)._refuse("set")

    def inc(self, *args, **kwargs) -> NoReturn:
        type(self)._refuse("inc")

    def delete(self, *args, **kwargs) -> NoReturn:
        type(self)._refuse("delete")

    # --- class writers ---
    @classmethod
    def insert_one(cls, *args, **kwargs) -> NoReturn:
        cls._refuse("insert_one")

    @classmethod
    def insert_many(cls, *args, **kwargs) -> NoReturn:
        cls._refuse("insert_many")

    @classmethod
    def replace_many(cls, *args, **kwargs) -> NoReturn:
        cls._refuse("replace_many")

    @classmethod
    def update_all(cls, *args, **kwargs) -> NoReturn:
        cls._refuse("update_all")

    @classmethod
    def delete_all(cls, *args, **kwargs) -> NoReturn:
        cls._refuse("delete_all")


class ParamDocument(_ReadOnlyDocument):
    """The tunables. Read at boot, refreshed on the slow tick, written only by a migration."""

    __tk_abstract__: ClassVar[bool] = True
    write_class: ClassVar[WriteClass] = WriteClass.PARAM


class LogicDocument(_ReadOnlyDocument):
    """The hardwired-logic tables: the math as rows. He does not edit the floor he stands on."""

    __tk_abstract__: ClassVar[bool] = True
    write_class: ClassVar[WriteClass] = WriteClass.LOGIC


def assert_writable(model: type[TkDocument]) -> None:
    """The predicate the datatier's public write path calls before it writes [T3].

    Migrations do not call this and are not meant to: they reach the r-classes through the
    migration writer, which is a different door with a different name — not this one with a flag
    turned off. A permission that can be switched off from the calling side is not a permission.
    """
    if not model.write_class.writable:
        raise WriteClassViolation(
            f"{model.__name__} is write-class '{model.write_class.value}' (read-only to the body). "
            f"An r-class collection has no public write path: change it with a migration in `db/`, "
            f"and the running body will pick it up on the slow tick."
        )
