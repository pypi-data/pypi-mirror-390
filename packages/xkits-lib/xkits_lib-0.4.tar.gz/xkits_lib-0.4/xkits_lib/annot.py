# coding:utf-8

import sys
from typing import Any
from typing import List
from typing import Tuple
from typing import Union
from typing import get_args
from typing import get_origin


def is_generic(annotation: Any) -> bool:
    return get_origin(annotation) is not None


def is_annot(annotation: Any) -> bool:
    return isinstance(annotation, type) or is_generic(annotation)


def _each_annot(annotation: Any) -> Tuple[Any, ...]:
    union_types: List[Any] = [Union]
    if sys.version_info >= (3, 10):
        from types import UnionType  # pragma: no cover, pylint: disable=C0415
        union_types.append(UnionType)  # pragma: no cover

    if get_origin(annotation) not in union_types:
        return (annotation,)

    return get_args(annotation)


def each_annot(annotation: Any) -> Tuple[Any, ...]:
    annotations = _each_annot(annotation)
    if (error := [annot for annot in annotations if not is_annot(annot)]):
        error_str: str = ", ".join(f'{i}' for i in error)
        raise TypeError(f"'{error_str}' is not a valid type annotation")
    return annotations
