from typing import NamedTupleMeta, _NamedTuple


class NestedNamedTupleMeta(type):

    def __new__(cls, name, bases, attrs):

        attrs["__annotations__"] = attrs.get("__annotations__", {})
        nm_attrs = dict(**attrs)

        reordered_annotations = {name: annotation for name, annotation in attrs["__annotations__"].items()
                                 if name not in attrs.keys()}
        for attr_name, attr_val in list(attrs.items()):

            if attr_name in attrs["__annotations__"].keys():
                reordered_annotations[attr_name] = nm_attrs["__annotations__"][attr_name]

            if isinstance(attr_val, type):
                _cls = nestedtuple(attr_val)

                reordered_annotations[attr_name] = _cls
                attrs[attr_name] = _cls
                try:
                    nm_attrs[attr_name] = _cls()
                except TypeError:
                    nm_attrs.pop(attr_name)

        nm_attrs["__annotations__"] = reordered_annotations

        nm = NamedTupleMeta(
            name,
            (_NamedTuple, *bases),
            {
                **nm_attrs
            }
        )

        _asdict = nm._asdict

        def __nested_new__(self, *args, **kwargs):
            default_args = {name: nm_attrs[name] for name in reordered_annotations.keys()
                            if name in nm_attrs.keys()}
            for attr_name, _ in zip(nm._fields, args):
                default_args.pop(attr_name, None)
            kwargs = default_args | kwargs
            return nm(*args, **kwargs)

        def _nested_asdict(self, *args, **kwargs):
            nested_dict = _asdict(self, *args, **kwargs)

            for name, value in dict(**nested_dict).items():
                if hasattr(value, "_asdict"):
                    nested_dict[name] = value._asdict(*args, **kwargs)

            return nested_dict

        nm._asdict = _nested_asdict

        for attr_name in ("_fields", "_field_defaults", "__repr__"):
            attrs[attr_name] = getattr(nm, attr_name)

        return type(name, bases, {
            "__new__": __nested_new__,
            **attrs
        })


def nestedtuple(cls):
    class_attrs = dict(cls.__dict__)
    class_attrs.pop("__dict__")
    class_attrs.pop("__weakref__")

    return NestedNamedTupleMeta(cls.__name__, cls.__bases__, class_attrs)
