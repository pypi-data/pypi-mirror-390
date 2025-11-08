"""This module implements custom YAML representer functions"""

from typing import Any, Callable, Union

from .yaml import (
    BaseRepresenter,
    Node,
    RepresenterFunc,
    add_representer,
    is_representer,
)

# -- Multi-purpose representers -----------------------------------------------


def represent_by_type(
    representer: BaseRepresenter,
    obj: Union[list, tuple, dict, Any],
    *,
    tag: str,
) -> Node:
    """A representer for simple types: sequence-like, mapping-like or scalar"""
    if isinstance(obj, (list, tuple)):
        return representer.represent_sequence(tag, list(obj))

    elif isinstance(obj, dict):
        return representer.represent_mapping(tag, obj)

    return representer.represent_scalar(tag, str(obj))


# -- Representer factories ----------------------------------------------------


def build_representer(
    simplify_type: Callable[[Any], Union[list, tuple, dict, Any]]
) -> RepresenterFunc:
    """Builds a representer that"""

    def representer_func(representer: BaseRepresenter, obj: Any, *, tag: str):
        return represent_by_type(
            representer,
            simplify_type(obj),
            tag=tag,
        )

    return representer_func


# -- Registration of representers ---------------------------------------------

add_representer(
    slice,
    build_representer(lambda o: [o.start, o.stop, o.step]),
)

add_representer(
    range,
    build_representer(lambda o: [o.start, o.stop, o.step]),
)
