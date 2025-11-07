from __future__ import annotations

from enum import Enum
from typing import Any, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel

T = TypeVar("T", bound="SerializableMixin")


class SerializableMixin(BaseModel):
    """
    Mixin for Pydantic models that provides compact serialization into dictionaries
    with numeric keys and the reverse deserialization.

    The main idea:
      * Field names are sorted alphabetically and replaced with integer indices.
      * The model is serialized into a dictionary where keys are field indices.
      * Works recursively for nested models, collections, and enums.
      * During deserialization, numeric keys are mapped back to field names.

    Supports:
      * Primitive types (`int`, `str`, `float`, `bool`, etc.)
      * `Enum` types (stored by their `.value`)
      * Nested Pydantic models
      * Collections (`list`, `tuple`, `set`, `dict`)
      * Optional/Union and complex nested structures

    Example:
        class Address(SerializableMixin):
            city: str
            zip_code: int

        class User(SerializableMixin):
            name: str
            age: int
            address: Address

        user = User(name="Alice", age=30, address=Address(city="NY", zip_code=10001))
        compact = user.to_compact_dict()
        restored = User.from_compact_dict(compact)
    """

    def to_compact_dict(self) -> dict[int, Any]:
        """
        Serialize the model into a compact dictionary with numeric keys.

        Field names are sorted alphabetically and replaced by sequential indices.
        Values are recursively serialized, including nested models and collections.

        :return: Compact serialized representation of the model
        :rtype: dict[int, Any]
        """
        data = self.model_dump()
        return self._serialize_value(data, self.__class__)  # type:ignore

    @classmethod
    def _serialize_value(cls, value: Any, field_type: Any = None) -> Any:  # noqa
        """
        Recursively serialize any value (model, collection, enum, etc.) into compact form.

        :param value: Value to serialize
        :type value: Any
        :param field_type: Type annotation used for recursive type-aware serialization
        :type field_type: Any
        :return: Serialized value
        :rtype: Any
        """
        if value is None:
            return None

        if isinstance(value, dict):
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                return cls._serialize_model_dict(value, field_type)
            else:
                return cls._serialize_arbitrary_dict(value)
        elif isinstance(value, list):
            item_type = (
                get_args(field_type)[0]
                if field_type and get_origin(field_type) is list
                else Any
            )
            return [cls._serialize_value(v, item_type) for v in value]
        elif isinstance(value, tuple):
            if field_type and get_origin(field_type) is tuple:
                tuple_args = get_args(field_type)
                if tuple_args and tuple_args[-1] is ...:
                    item_type = tuple_args[0]
                    return tuple(cls._serialize_value(v, item_type) for v in value)
                else:
                    result = []
                    for i, v in enumerate(value):
                        item_type = tuple_args[i] if i < len(tuple_args) else Any
                        result.append(cls._serialize_value(v, item_type))
                    return tuple(result)
            else:
                return tuple(cls._serialize_value(v, Any) for v in value)
        elif isinstance(value, set):
            item_type = (
                get_args(field_type)[0]
                if field_type and get_origin(field_type) is set
                else Any
            )
            return {cls._serialize_value(v, item_type) for v in value}
        elif isinstance(value, BaseModel) and hasattr(value, "to_compact_dict"):
            if isinstance(value, field_type) if field_type else True:
                return value.to_compact_dict()
            return value
        elif isinstance(value, Enum):
            return value.value
        else:
            return value

    @classmethod
    def _serialize_model_dict(
        cls, data: dict[str, Any], model_class: type[BaseModel]
    ) -> dict[int, Any]:
        """
        Serialize a dictionary representing a Pydantic model into numeric-key format.

        :param data: Dictionary obtained from ``model_dump()``
        :type data: dict[str, Any]
        :param model_class: Pydantic model class that owns this dictionary
        :type model_class: Type[BaseModel]
        :return: Serialized dictionary where keys are integer indices
        :rtype: dict[int, Any]
        """
        fields = sorted(model_class.model_fields.keys())
        key_map = {key: i for i, key in enumerate(fields)}
        result = {}

        for key, value in data.items():
            if key not in key_map:
                continue
            idx = key_map[key]
            field_info = model_class.model_fields[key]
            field_type = field_info.annotation

            result[idx] = cls._serialize_value(value, field_type)

        return result

    @classmethod
    def _serialize_arbitrary_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Serialize an arbitrary dictionary that is not a Pydantic model.

        String keys are kept as-is, values are serialized recursively.

        :param data: Arbitrary dictionary to serialize
        :type data: dict[str, Any]
        :return: Serialized dictionary with string keys
        :rtype: dict[str, Any]
        """
        return {k: cls._serialize_value(v) for k, v in data.items()}

    @classmethod
    def from_compact_dict(cls: type[T], compact_data: dict[int, Any]) -> T:
        """
        Deserialize a compact dictionary back into a model instance.

        :param compact_data: Dictionary obtained from :meth:`to_compact_dict`
        :type compact_data: dict[int, Any]
        :return: Restored model instance
        :rtype: SerializableMixin
        :raises ValidationError: If deserialized data does not satisfy model constraints
        """
        fields = sorted(cls.model_fields.keys())
        reverse_map = {i: key for i, key in enumerate(fields)}
        data = {}

        for idx, value in compact_data.items():
            if idx not in reverse_map:
                continue

            key = reverse_map[idx]
            field_info = cls.model_fields[key]
            field_type = field_info.annotation

            data[key] = cls._deserialize_value(value, field_type, field_info)

        return cls(**data)

    @classmethod
    def _deserialize_value(  # noqa
        cls, value: Any, field_type: Any, field_info: Any = None
    ) -> Any:
        """
        Recursively deserialize a value with respect to its annotated field type.

        Supports nested models, enums, lists, tuples, sets, and arbitrary dictionaries.

        :param value: Serialized value (int, list, dict, etc.)
        :type value: Any
        :param field_type: Type annotation of the field
        :type field_type: Any
        :param field_info: Optional Pydantic field metadata
        :type field_info: Any, optional
        :return: Deserialized value
        :rtype: Any
        """
        if value is None:
            return None

        if field_type is None:
            field_type = Any

        origin = get_origin(field_type) if field_type is not Any else None
        args = get_args(field_type) if field_type is not Any else []

        if origin is Union:
            if type(None) in args:
                non_none_types = [t for t in args if t is not type(None)]
                if non_none_types:
                    field_type = non_none_types[0]
                    origin = get_origin(field_type) if field_type is not Any else None
                    args = get_args(field_type) if field_type is not Any else []

        if isinstance(value, dict):
            if (
                isinstance(field_type, type)
                and issubclass(field_type, BaseModel)
                and hasattr(field_type, "from_compact_dict")
            ):
                return field_type.from_compact_dict(value)  # type:ignore

            elif origin is dict:
                key_type, value_type = args if len(args) == 2 else (Any, Any)

                if key_type is str:
                    result = {}
                    for k, v in value.items():
                        deserialized_key = str(k) if not isinstance(k, str) else k
                        deserialized_value = cls._deserialize_value(v, value_type)
                        result[deserialized_key] = deserialized_value
                    return result
                else:
                    result = {}
                    for k, v in value.items():
                        deserialized_key = cls._deserialize_value(k, key_type)
                        deserialized_value = cls._deserialize_value(v, value_type)
                        result[deserialized_key] = deserialized_value
                    return result

            else:
                return cls._deserialize_arbitrary_dict(value)

        elif isinstance(value, list):
            if origin is list and args:
                item_type = args[0]
                return [cls._deserialize_value(v, item_type) for v in value]
            else:
                return [cls._deserialize_value(v, Any) for v in value]

        elif isinstance(value, tuple):
            if origin is tuple:
                if args and args[-1] is ...:  # Tuple[Type, ...]
                    item_type = args[0]
                    return tuple(cls._deserialize_value(v, item_type) for v in value)
                else:  # Tuple[Type1, Type2, ...]
                    result_l = []  # type: list[dict[str, Any]]
                    for i, v in enumerate(value):
                        if i < len(args):
                            item_type = args[i]
                            result_l.append(cls._deserialize_value(v, item_type))
                        else:
                            result_l.append(v)
                    return tuple(result_l)
            else:
                return tuple(cls._deserialize_value(v, Any) for v in value)

        elif isinstance(value, set):
            if origin is set and args:
                item_type = args[0]
                return {cls._deserialize_value(v, item_type) for v in value}
            else:
                return {cls._deserialize_value(v, Any) for v in value}

        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            try:
                return field_type(value)
            except (ValueError, KeyError):
                return value

        else:
            return value

    @classmethod
    def _deserialize_arbitrary_dict(cls, data: dict[Any, Any]) -> dict[str, Any]:
        """
        Deserialize an arbitrary dictionary that may contain nested structures.

        All keys are converted to strings; nested collections are processed recursively.

        :param data: Dictionary with arbitrary key-value types
        :type data: dict[Any, Any]
        :return: Fully deserialized dictionary with string keys
        :rtype: dict[str, Any]
        """
        result = {}  # type: dict[str, Any]
        for k, v in data.items():
            key = str(k)
            if isinstance(v, dict):
                result[key] = cls._deserialize_arbitrary_dict(v)
            elif isinstance(v, list):
                result[key] = [
                    (
                        cls._deserialize_arbitrary_dict(item)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in v
                ]
            elif isinstance(v, tuple):
                result[key] = tuple(
                    (
                        cls._deserialize_arbitrary_dict(item)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in v
                )
            elif isinstance(v, set):
                result[key] = {
                    (
                        cls._deserialize_arbitrary_dict(item)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in v
                }
            else:
                result[key] = v
        return result
