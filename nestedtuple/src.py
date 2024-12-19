from typing import Callable, List, NamedTupleMeta, _NamedTuple, Tuple, Union
import types


class NestedNamedTupleMeta(type):
    """Metaclass for creating nested named tuples."""

    def __new__(cls, name, bases, attrs):

        attrs["__annotations__"] = attrs.get("__annotations__", {})
        nm_attrs = dict(**attrs)
        reordered_annotations = {name: annotation for name, annotation in attrs["__annotations__"].items()
                                 if name not in attrs.keys()}

        for attr_name, attr_val in list(attrs.items()):

            if attr_name in attrs["__annotations__"].keys():
                reordered_annotations[attr_name] = nm_attrs["__annotations__"][attr_name]

            if isinstance(attr_val, types.FunctionType):
                reordered_annotations[attr_name] = Callable

            if isinstance(attr_val, type):

                _cls = nestedtuple(attr_val)

                reordered_annotations[attr_name] = _cls.__base__._type_of(_cls)
                attrs[attr_name] = _cls
                default_generator = _cls.__base__._default_generator(_cls)
                nm_attrs.pop(attr_name)
                if default_generator:
                    nm_attrs[attr_name] = default_generator(_cls)

        nm_attrs["__annotations__"] = reordered_annotations

        # print(name, nm_attrs)
        nm = NamedTupleMeta(
            name,
            (_NamedTuple,),
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
                elif isinstance(value, (tuple, list)):
                    nested_dict[name] = type(value)(
                        item._asdict(*args, **kwargs) if hasattr(item, "_asdict") else item
                        for item in value)
                elif isinstance(value, (dict,)):
                    nested_dict[name] = {key: item._asdict(*args, **kwargs) if hasattr(item, "_asdict") else item
                                         for key, item in value.items()}

            return nested_dict

        nm._asdict = _nested_asdict

        for attr_name in ("_fields", "_field_defaults", "__repr__"):
            attrs[attr_name] = getattr(nm, attr_name)

        return type(name, bases, {
            "__new__": __nested_new__,
            "__namedtuple_class__": nm,
            **attrs
        })


def nestedtuple(cls):
    """Decorator to create nested named tuples."""

    class AssignAsAttribute:

        @staticmethod
        def _type_of(cls): return cls

        @staticmethod
        def _default_generator(cls):
            issubset = set(cls.__annotations__.keys()).issubset(cls.__dict__.keys())
            return (lambda _cls: _cls()) if issubset else None

    class_attrs = dict(cls.__dict__)

    if cls.__base__ is object:
        __bases__ = (AssignAsAttribute, *cls.__bases__[1:])
    else:
        __bases__ = cls.__bases__

    # If one of the parent is ```object```, e.g., class Name: or class Name():
    class_attrs.pop("__dict__", None)
    class_attrs.pop("__weakref__", None)

    return NestedNamedTupleMeta(cls.__name__, __bases__, class_attrs)


def listof(cls):
    """Assign the subclass attribute as List[cls] instead of cls."""

    class AssignListOfAttribute:

        @staticmethod
        def _type_of(cls): return List[cls]
        @staticmethod
        def _default_generator(cls): return None

    class_attrs = dict(cls.__dict__)
    __bases__ = (AssignListOfAttribute, *cls.__bases__[1:])
    return type(cls.__name__, __bases__, class_attrs)


def tupleof(cls):
    """Assign the subclass attribute as Tuple[cls] instead of cls."""

    class AssignListOfAttribute:

        @staticmethod
        def _type_of(cls): return Tuple[cls]
        @staticmethod
        def _default_generator(cls): return None

    class_attrs = dict(cls.__dict__)
    __bases__ = (AssignListOfAttribute, *cls.__bases__[1:])
    return type(cls.__name__, __bases__, class_attrs)


def unionof(cls):
    """Assign the subclass attribute as Union[*cls._fields] instead of cls."""

    class AssignListOfAttribute:

        @staticmethod
        def _type_of(cls):
            class_typed_attributes = [key for key in cls._fields
                                      if isinstance(getattr(cls, key), type)]
            if len(class_typed_attributes) == 0:
                raise ValueError(f"Class {cls.__name__} does not have class typed attributes!")
            if len(class_typed_attributes) != len(cls._fields):
                non_class_attributes = set(cls._fields).difference(
                    set(class_typed_attributes))
                msg = ", ".join(non_class_attributes)
                raise ValueError(f"Class {cls.__name__} has non-class typed attributes: {msg}")
            return Union.__getitem__(tuple(getattr(cls, name) for name in class_typed_attributes))

        @staticmethod
        def _default_generator(cls): return None

    class_attrs = dict(cls.__dict__)
    __bases__ = (AssignListOfAttribute, *cls.__bases__[1:])
    return type(cls.__name__, __bases__, class_attrs)
