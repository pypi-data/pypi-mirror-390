from __future__ import annotations

import functools
import sys
import typing
from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import _MISSING_TYPE
from dataclasses import Field
from dataclasses import dataclass
from dataclasses import field
from types import MappingProxyType
from typing import Annotated
from typing import Any
from typing import ClassVar
from typing import Literal
from typing import Protocol
from typing import TypedDict
from typing import TypeGuard
from typing import Unpack
from typing import cast
from typing import dataclass_transform
from typing import overload

from docnote import Note

if typing.TYPE_CHECKING:
    from _typeshed import DataclassInstance
else:
     DataclassInstance = object


class DataclassFieldKwargs(TypedDict, total=False):
    init: bool
    repr: bool
    hash: bool | None
    compare: bool
    metadata: Mapping[Any, Any] | None
    kw_only: bool | Literal[_MISSING_TYPE.MISSING]


class DataclassFieldKwargs14(DataclassFieldKwargs, TypedDict, total=False):
    doc: str | None


# The following is adapted directly from typeshed. We did some formatting
# updates, and inserted our *ext_configs param.
if sys.version_info >= (3, 14):
    @overload
    def ext_field[_T](
            *ext_configs: Any,
            default: _T,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            **field_kwargs: Unpack[DataclassFieldKwargs14]
            ) -> _T: ...
    @overload
    def ext_field[_T](
            *ext_configs: Any,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Callable[[], _T],
            **field_kwargs: Unpack[DataclassFieldKwargs14]
            ) -> _T: ...
    @overload
    def ext_field[_T](
            *ext_configs: Any,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            **field_kwargs: Unpack[DataclassFieldKwargs14]
            ) -> Any: ...

# This is technically only valid for >=3.10, but we require that anyways
else:
    @overload
    def ext_field[_T](
            *ext_configs: Any,
            default: _T,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            **field_kwargs: Unpack[DataclassFieldKwargs]
            ) -> _T: ...
    @overload
    def ext_field[_T](
            *ext_configs: Any,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Callable[[], _T],
            **field_kwargs: Unpack[DataclassFieldKwargs]
            ) -> _T: ...
    @overload
    def ext_field[_T](
            *ext_configs: Any,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            **field_kwargs: Unpack[DataclassFieldKwargs]
            ) -> Any: ...


def ext_field(
        *ext_configs: Any,
        metadata: Mapping[Any, Any] | None = None,
        **field_kwargs):
    """``ext_field`` is a light wrapper around stdlib dataclass fields.
    It allows end users to specify field configs as positional-only
    ``*args``, which are then collected together into a field config
    dict, with their types as keys (ie, ``{type(config}: config}``).
    This is then used as the field metadata (after combining it with any
    other metadata passed to ``ext_field``).
    """
    # The ordering here is so that the configs always take precedence over
    # the existing metadata
    additional_metadata = {
        type(ext_config): ext_config for ext_config in ext_configs}

    if len(additional_metadata) != len(ext_configs):
        raise TypeError(
            'Cannot have multiple field configs of the same type in a '
            + 'single ``ext_field(...)`` call!', ext_configs)

    if metadata is None:
        combined_metadata = additional_metadata
    else:
        combined_metadata = {
            **metadata,
            **additional_metadata}

    return field(**field_kwargs, metadata=combined_metadata)


class DataclassKwargs(TypedDict, total=False):
    init: bool
    repr: bool
    eq: bool
    order: bool
    unsafe_hash: bool
    frozen: bool
    match_args: bool
    kw_only: bool
    slots: bool
    weakref_slot: bool


type DceiClassConfigDict[T: DceiConfigProtocol] = Annotated[
    Mapping[type[T], T],
    Note('''The DCEI class config dict maps the config type to its instance
        (ie, ``{type(config): config}``). It is made available on the resulting
        dataclass-transformed class as per the ``ExtDataclassInstance``
        protocol.''')]


class ExtDataclassInstance(Protocol):
    __dcei_cls_configs__: ClassVar[DceiClassConfigDict]


class DceiConfigProtocol[T: type[Any]]:
    """The DceiConfigProtocol is used to define what interface is
    required for postprocessing dataclasses.

    It accepts a single type parameter that describes any postprocessing
    done on the dataclass:

    > Example postprocessing protocol
    __embed__: 'code/python'
        from typing import ClassVar
        from typing import Protocol

        from dcei import DceiConfigProtocol


        class MyExtensionProtocol(Protocol):
            '''The final post-processed dataclass is an intersection of
            the result of the original datclass transform and this
            protocol.
            '''
            my_postprocess_result: ClassVar[str]


        class MyExtensionConfig(DceiConfigProtocol[type[MyExtensionProtocol]]):
            def postprocess_dataclass(
                    self,
                    cls: type[DataclassInstance]
                    ) -> TypeGuard[type[MyExtensionProtocol]]]:
                cls.my_postprocess_result = 'success'
                return True

    Note that currently, the type parameter is **informational only.**
    Python lacks language support for it to have an actual impact on
    the result of type analysis, so (unless type checkers introduce
    their own special-cased code specifically for DCEI), you will need
    to either ``cast(...)`` or ``type: ignore`` when actually accessing
    protocol members (``my_postprocess_result`` in the example above).
    Specifically, what would be needed:
    ++  support for intersection types
    ++  the ability to intersect with the result of
        ``@dataclass_transform``, or an alternative generic
        ``DataclassTransform`` type that could be intersected with

    **Note that we still recommend you pass the type parameter when
    defining config protocols.** This will allow you and your users to
    seamlessly incorporate full type support if and when the above are
    added to python at a language level, and increase the likelihood
    that type checkers would add special-cased support in the interim.
    """

    def postprocess_dataclass(
            self,
            cls: type[DataclassInstance],
            cls_configs: DceiClassConfigDict,
            dataclass_kwargs: DataclassKwargs
            ) -> TypeGuard[T]:
        """Postproccessing is called on dataclasses after the dataclass
        transform has been applied. It can modify the dataclass
        in-place, but these modifications must be strictly addative --
        for example, by setting a new classvar on the dataclass. (Note
        that this isn't a technical requirement, but rather, a condition
        of the DCEI spec).

        Since postprocessing is responsible for guaranteeing that the
        dataclass adheres to the protocol passed by the underlying type
        parameter, it should always return True (but the return value
        will be ignored by dcei).
        """
        ...


class DceiConfigMixin(DceiConfigProtocol[type[DataclassInstance]]):
    """This class can be used as a no-op mixin for config classes that
    do not require any post-processing on the dataclass.
    """

    def postprocess_dataclass[T: type[DataclassInstance]](
            self,
            cls: T,
            cls_configs: DceiClassConfigDict,
            dataclass_kwargs: DataclassKwargs
            ) -> TypeGuard[T]:
        return True


@dataclass_transform(field_specifiers=(ext_field, field, Field))
def ext_dataclass[T: type](
        *dcei_configs: DceiConfigProtocol,
        **dataclass_kwargs: Unpack[DataclassKwargs]
        ) -> Callable[[T], T]:
    """Constructs a normal stdlib dataclass, and then performs the
    required DCEI processing on it.

    Note that extensions that don't require configuration can just use
    the normal stdlib ``@dataclass`` decorator.
    """
    @functools.wraps(dataclass)
    def wrap_make_dataclass(cls: T) -> T:
        """This is just our closure around normal dataclass creation.
        """
        # Immediately wrap in a mapping proxy to prevent accidental mutation
        cls_configs = MappingProxyType({
            type(dcei_config): dcei_config
            for dcei_config in dcei_configs})
        dataclass_kwargs_view = cast(
            DataclassKwargs,
            MappingProxyType(dataclass_kwargs))

        if len(cls_configs) != len(dcei_configs):
            raise TypeError(
                'Cannot have multiple DCEI configs of the same type in a '
                + 'single ``@ext_dataclass(...)`` call!', cls, dcei_configs)

        dataclassed = dataclass(**dataclass_kwargs)(cls)
        dataclassed.__dcei_cls_configs__ = cls_configs

        # Note that this can't be combined witht he dict comprehension, because
        # our API contract includes passing the full config dict to all of the
        # postprocessing calls
        for dcei_config in dcei_configs:
            dcei_config.postprocess_dataclass(
                dataclassed,
                cls_configs,
                dataclass_kwargs_view)

        return dataclassed

    return wrap_make_dataclass
