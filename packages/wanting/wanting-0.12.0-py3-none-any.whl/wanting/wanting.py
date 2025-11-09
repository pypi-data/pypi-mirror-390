"""The Wanting module."""

import functools
from collections.abc import Iterator, Mapping, MutableMapping
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    NamedTuple,
    TypeGuard,
    Union,
    cast,
    get_origin,
)

import pydantic
import pydantic_core


class Json(pydantic.BaseModel):
    """Wrapper for a JSON value."""

    serialized: bytes


def _to_json(value: Any) -> Json:  # noqa: ANN401
    if isinstance(value, Json):
        return value
    try:
        return Json.model_validate(value)
    except pydantic.ValidationError:
        return Json(serialized=pydantic_core.to_json(value))


class Wanting(pydantic.BaseModel):
    """Abstract class that represents an incomplete field value.

    When serializing a model that contains wanting fields with
    ``exclude_unset``, optional fields in the wanting models that have not been
    explicitly set would normally be omitted. However, any model that
    subclasses :class:`Wanting` will not have their ``kind``, and ``value``
    fields omitted due to ``exclude_unset``. This behavior can be overridden
    when serializing by passing a context dict with a ``wanting`` key whose
    value is a dict that contains an ``enable_exclude_unset`` key whose value
    is True.

    Examples:
        Serialization ignores ``exclude_unset``.

        .. code-block:: python

            class M(pydantic.BaseModel):
                a: str = "unset"
                b: str | Unavailable


            m = M(b=Unavailable(source="docs"))

            assert m.model_dump(exclude_unset=True) == {
                # a is excluded by exclude_unset
                "b": {  # kind and value are not excluded by exclude_unset
                    "kind": "unavailable",
                    "source": "docs",
                    "value": {"serialized": b"null"},
                }
            }

        However this behavior can be overridden by passing a context.

        .. code-block:: python

            assert m.model_dump(
                exclude_unset=True, context={"wanting": {"enable_exclude_unset": True}}
            ) == {
                # a is excluded by exclude_unset
                "b": {  # kind and value are also excluded by exclude_unset
                    "source": "docs"
                }
            }
    """

    kind: str
    source: str
    if TYPE_CHECKING:
        value: Any
    else:
        value: Annotated[Json, pydantic.BeforeValidator(_to_json)]

    @pydantic.model_serializer(mode="wrap")
    def serializer(
        self, handler: pydantic.SerializerFunctionWrapHandler, info: pydantic.SerializationInfo
    ) -> dict[str, Any]:
        """Ignore ``exclude_unset`` for certain fields."""
        if not info.exclude_unset:
            return cast("dict[str, Any]", handler(self))

        if isinstance(info.context, Mapping) and info.context.get("wanting", {}).get(
            "enable_exclude_unset"
        ):
            return cast("dict[str, Any]", handler(self))

        add = {"kind", "value"} - self.model_fields_set
        if not add:
            return cast("dict[str, Any]", handler(self))

        self.model_fields_set.update(add)
        try:
            return cast("dict[str, Any]", handler(self))
        finally:
            self.model_fields_set.difference_update(add)


class Unavailable(Wanting):
    """Represents an unavailable field value."""

    kind: Literal["unavailable"] = "unavailable"
    value: Json = pydantic.Field(default_factory=lambda: Json(serialized=b"null"))


class Unmapped(Wanting):
    """Represents an unmapped field value."""

    kind: Literal["unmapped"] = "unmapped"


class FieldInfoEx(NamedTuple):
    """Extended information about a field."""

    cls: type[pydantic.BaseModel]
    name: str
    info: pydantic.fields.FieldInfo


_UNION_TYPES = {UnionType, Union}


def _is_union_type(typ: object) -> TypeGuard[UnionType]:
    return get_origin(typ) in _UNION_TYPES


def _field_wanting_types(fi: pydantic.fields.FieldInfo) -> Iterator[type[Wanting]]:
    typ = fi.annotation
    if _is_union_type(typ):
        for utyp in typ.__args__:
            if issubclass(utyp, Wanting):
                yield utyp
    elif isinstance(typ, type) and issubclass(typ, Wanting):
        yield typ


def _field_has_wanting_type(fi: pydantic.fields.FieldInfo) -> bool:
    return bool(next(_field_wanting_types(fi), False))


def _field_model_types(fi: pydantic.fields.FieldInfo) -> Iterator[type[pydantic.BaseModel]]:
    typ = fi.annotation
    if isinstance(typ, type) and issubclass(typ, pydantic.BaseModel):
        yield typ
    elif _is_union_type(typ):
        for utyp in typ.__args__:
            if issubclass(utyp, pydantic.BaseModel):
                yield utyp


def wanting_fields(
    cls: type[pydantic.BaseModel], *, depth: int = -1
) -> Iterator[list[FieldInfoEx]]:
    """Get the fields in a model class that could be :class:`Wanting`.

    Args:
        cls: The model class to inspect for wanting fields.
        depth: How deeply to check nested models for wanting fields. The depth
            is zero-based, so ``0`` for only top-level fields. ``-1`` for no
            limit.

    Returns:
        An iterator of :class:`FieldInfoEx` lists, where each list describes
        the path to a top-level, or nested wanting field.
    """
    top_level_wanting_field_paths = (
        [FieldInfoEx(cls, name, fi)]
        for name, fi in cls.model_fields.items()
        if _field_has_wanting_type(fi)
    )
    yield from top_level_wanting_field_paths

    if depth == 0:
        return

    top_level_model_fields = [
        (name, fi, list(_field_model_types(fi))) for name, fi in cls.model_fields.items()
    ]
    nested_wanting_field_paths = (
        [FieldInfoEx(cls, name, fi), *path]
        for name, fi, typs in top_level_model_fields
        for typ in typs
        for path in wanting_fields(typ, depth=depth - 1)
    )
    yield from nested_wanting_field_paths


type WantingValues = Mapping[str, Wanting | WantingValues]
type _MutableWantingValues = MutableMapping[str, Wanting | _MutableWantingValues]


def wanting_values[T](
    model: pydantic.BaseModel | pydantic.RootModel[T],
    *targets: type[Wanting],
    collapse_root: bool = True,
) -> WantingValues:
    """Get the values in a model instance that are target :class:`Wanting` types.

    Args:
        model: The model instance to inspect for wanting values.
        targets: The :class:`Wanting` types of values to get. Defaults to all
            Wanting types.
        collapse_root: If True, the wanting values under the ``root`` field of
            RootModels will be moved up one level in the result, as if they
            were top-level fields in the model.

    Returns:
        A dict that mirrors the structure of the model, but only contains the
        fields that have wanting values.

    Examples:
        Get all the wanting values from a model instance.

        .. code-block:: python

            class Child(pydantic.BaseModel):
                a: str | Unmapped

            class Parent(pydantic.BaseModel):
                a: str | Unavailable
                b: str | Unmapped
                c: Child

            m = Parent(
                a=Unavailable(source="docs"),
                b="foo",
                c=Child(a=Unmapped(source="docs", value="bar")),
            )

            assert wanting_values(m) == {
                "a": Unavailable(source="docs"),
                # b is not included because it doesn't have a Wanting value
                "c": {"a": Unmapped(source="docs", value="bar")},
            }

        Get only the unmapped values.

        .. code-block:: python

            assert wanting_values(m, Unmapped) == {
                # a is not included because it doesn't have an Unmapped value
                # b is not included because it doesn't have a Wanting value
                "c": {"a": Unmapped(source="docs", value="bar")}
            }
    """
    if not targets:
        targets = (Wanting,)

    if collapse_root and isinstance(model, pydantic.RootModel):
        return (
            wanting_values(model.root, *targets, collapse_root=collapse_root)
            if isinstance(model.root, pydantic.BaseModel)
            else {}
        )

    def _wanting_values_reducer(
        acc: _MutableWantingValues, curr: tuple[str, object]
    ) -> _MutableWantingValues:
        name, value = curr
        if collapse_root and isinstance(value, pydantic.RootModel):
            value = value.root
        if isinstance(value, targets):
            acc[name] = value
            return acc
        if isinstance(value, pydantic.BaseModel):
            nested = cast(
                "_MutableWantingValues",
                wanting_values(value, *targets, collapse_root=collapse_root),
            )
            if nested:
                acc[name] = nested
                return acc
        return acc

    initial: _MutableWantingValues = {}
    return cast("WantingValues", functools.reduce(_wanting_values_reducer, model, initial))


type IncExMapping = Mapping[str, bool | IncExMapping]
"""A mapping that describes which fields to include, or exclude during serialization.

Values of this type may be used as the ``include`` or ``exclude`` parameter to
:func:`pydantic.BaseModel.model_dump`.
"""

type _IncExMutableMapping = MutableMapping[str, bool | _IncExMutableMapping]


def wanting_incex(model: pydantic.BaseModel, *targets: type[Wanting]) -> IncExMapping:
    """Get a mapping to include or exclude :class:`Wanting` fields in a model instance.

    Args:
        model: The model instance to inspect for wanting values.
        targets: The :class:`Wanting` types to include, or exclude. Defaults to
            all Wanting types.

    Returns:
        An :type:`IncExMapping` that can be used as the ``include`` or
        ``exclude`` argument to Pydantic serialization methods.

    Examples:
        Dump all Wanting values in a model instance.

        .. code-block:: python

            class Child(pydantic.BaseModel):
                a: str | Unmapped

            class Parent(pydantic.BaseModel):
                a: str | Unavailable
                b: str | Unmapped
                c: Child

            m = Parent(
                a=Unavailable(source="docs"),
                b="foo",
                c=Child(a=Unmapped(source="docs", value="bar")),
            )

            incex = wanting_incex(m)
            assert incex == {"a": True, "c": {"a": True}}
            assert m.model_dump(include=incex) == {
                "a": {
                    "kind": "unavailable",
                    "source": "docs",
                    "value": {"serialized": b"null"},
                },
                # b is not included because it doesn't have a Wanting value
                "c": {
                    "a": {
                        "kind": "unmapped",
                        "source": "docs",
                        "value": {"serialized": b'"bar"'},
                    }
                },
            }

        Dump only the Unmapped values in a model instance.

        .. code-block:: python

            incex = wanting_incex(m, targets=(Unmapped,))
            assert incex == {"c": {"a": True}}
            assert m.model_dump(include=incex) == {
                # a is not included because it doesn't have an Unmapped value
                # b is not included because it doesn't have a Wanting value
                "c": {
                    "a": {
                        "kind": "unmapped",
                        "source": "docs",
                        "value": {"serialized": b'"bar"'},
                    }
                }
            }

    """
    if not targets:
        targets = (Wanting,)

    def _exclude_wanting_values_reducer(
        acc: _IncExMutableMapping, curr: tuple[str, Wanting | WantingValues]
    ) -> _IncExMutableMapping:
        name, value = curr
        if isinstance(value, targets):
            acc[name] = True
            return acc
        if isinstance(value, Mapping):
            initial: _IncExMutableMapping = {}
            acc[name] = functools.reduce(_exclude_wanting_values_reducer, value.items(), initial)
            return acc
        return acc

    wv = wanting_values(model, *targets, collapse_root=True)
    initial: _IncExMutableMapping = {}
    return cast(
        "IncExMapping", functools.reduce(_exclude_wanting_values_reducer, wv.items(), initial)
    )
