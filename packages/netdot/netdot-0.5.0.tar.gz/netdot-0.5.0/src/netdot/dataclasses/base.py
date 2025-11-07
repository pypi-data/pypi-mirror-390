import dataclasses
import ipaddress
import logging
import textwrap
import threading
from typing import Callable, ClassVar, Dict, List, Set, Tuple

import typing_inspect

import netdot
import netdot.exceptions
from netdot import config, parse, utils
from netdot.csv_util import CSVDataclass
from netdot.mac_address import MACAddress

logger = logging.getLogger(__name__)


inconsistent_and_ignorable_fields = set(
    [
        'info',
        'ttl',
    ]
)

name_collision_marker = "__KEYWORD_ESC"

def handle_None_values(dto):
    # ! TODO Do we ever need to send an empty string when None is provided??
    return {k: v for k, v in dto.items() if bool(v) is True}


def handle_bool_values(dto):
    return {k: str(int(v)) if isinstance(v, bool) else v for k, v in dto.items()}


def handle_xlink_fields(dto):
    # Convert _xlink fields to remove the suffix, and send ID only
    for k, v in dto.items():
        if k.endswith('_xlink'):
            str_or_object = dto[k.replace('_xlink', '')]
            if isinstance(str_or_object, NetdotAPIDataclass):
                dto[k.replace('_xlink', '')] = str_or_object.id
            else:
                dto[k.replace('_xlink', '')] = v
    return {k: v for k, v in dto.items() if not k.endswith('_xlink')}

@dataclasses.dataclass
class NetdotAPIDataclass(CSVDataclass):
    #
    #
    # Class variables
    #
    #
    _initialized: ClassVar[bool] = False
    _logged_unused_fields: ClassVar[Set] = None
    _NETDOT_ASSOCIATIVE_TABLE: ClassVar[bool] = False
    _NETDOT_TABLE_NAME: ClassVar[str] = None  # Optional -- will use class name if not provided
    DEFAULT_DTO_FIELD_PARSERS: ClassVar = {
        '*_xlink': parse.ID_from_xlink,
    }
    DISPLAY_ATTRIBUTES: ClassVar[List[str]] = ['access', 'name', 'level', 'bgppeerid', 'number']  # TODO This would be more efficient if set per-dataclass. Ex. netdot.AccessRight._DISPLAY_ATTRIBUTES should be ['access'] only. Ex2. netdot.rrloc._DISPLAY_ATTRIBUTES should be ['longitude', 'latitude'] only

    #
    #
    # Default dataclass fields
    #
    #
    id: int = None
    _post_init: bool = dataclasses.field(
        # Set to true via __post_init__
        default=False,
        repr=False,
        compare=False,
    )
    _auto_update_lock: bool = dataclasses.field(default=threading.Lock(), repr=False, compare=False)
    _repository: 'netdot.Repository' = dataclasses.field(  # noqa
        default=None, repr=False, compare=False
    )

    #
    #
    # Properties
    #
    #
    @property
    def netdot_url(self):
        return self.repository.connection.netdot_url

    @property
    def repository(self) -> 'netdot.Repository':
        return self._repository

    @property
    def web_url(self) -> str:
        """A URL to view this object in Netdot's web interface.
        """
        return f'{self.netdot_url}/generic/view.html?table={self._table_name()}&id={self.id}'

    # @repository.setter  # TODO Test this property setter
    def with_repository(self, repository: 'netdot.Repository') -> 'NetdotAPIDataclass':
        """Add your Netdot repository to this object (to simplify `create_or_update`, `load_*`, etc)."""
        self._repository = repository
        return self

    #
    #
    # CRUD Operations
    #
    #
    def create(self):
        """Create this object in Netdot. (wrapper around :func:`create_or_update()`)

        Raises:
            ValueError: If trying to create an object that already has an `id`.
        """
        if self.id is not None:
            raise ValueError(
                f'Cannot create an object that already has an `id` (id={self.id}). ID is assigned by database.'
            )
        self.create_or_update()

    def update(self):
        """Update this object in Netdot.

        Raises:
            ValueError: If trying to update an object that has no `id`.
        """
        if self.id is None:
            raise ValueError('`id` is required to update an object. None provided.')
        self.create_or_update()

    def create_or_update(self: 'NetdotAPIDataclass'):
        """Create or update this object in Netdot.

        > NOTE: Upon creation, this object's `id` will be populated.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: if the object cannot be created for any reason. (error details can be found in Netdot's apache server logs)
            As an example, expect a generic HTTP 400 when:
              * an object breaks 'uniqueness' rules (Ex. 2 Sites named "Test"),
              * an object is missing required fields (Ex. a Person without a `lastname`),
              * an object is improperly formatted (Ex. a Device with a `date_installed` that is not a datetime),
        """
        self._assert_repository_attached()
        if self.id:  # UPDATE
            create_or_update_function = getattr(self.repository, 'update')
        else:  # CREATE
            create_or_update_function = getattr(self.repository, 'create_new')
        create_or_update_function(self)

    def delete(self, **kwargs):
        """Delete this object.

        Args:
            See :func:`netdot.Repository.delete`

        Requires:
            Must have repository attached. Use with_repository(...)
        """
        self._assert_repository_attached()
        self.repository.delete(self, **kwargs)

    def replace(self, **kwargs):
        """Return a new object replacing specified fields with new values.

        Returns:
            NetdotAPIDataclass: A copy of this object with the specified fields replaced with new values.
        """
        return dataclasses.replace(self, **kwargs)

    #
    #
    # __dunder__ methods (hooking into python functionality)
    #
    #
    def __post_init__(self):
        self._prepare_class()
        self._post_init = True

    def __setattr__(self, name, value):
        """We override setattr so that we can:
        * Handle associated '_xlink' field if a NetdotAPIDataclass is provided, and
        * Handle auto_update feature if enabled.
        """
        if not self._handle_xlink_setattr(name, value):
            super().__setattr__(name, value)
            # TODO: Figure out how to run auto-update for xlink fields (but not when setting the xlink field as part of `load_*` methods)
        self._attempt_auto_update_if_enabled(name, value)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['_auto_update_lock']
        del state['_repository']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Restore the unpicklable entries.
        self._auto_update_lock = threading.Lock()
        self._repository = None
    
    def _display(self, display_full_objects=None):
        display_full_objects = display_full_objects if display_full_objects is not None else config.DISPLAY_FULL_OBJECTS
        if display_full_objects:
            return self.__repr__()
        display_attributes = dict()
        display_attributes['id'] = self.id
        if self.DISPLAY_ATTRIBUTES:
            for attr in self.DISPLAY_ATTRIBUTES:
                if hasattr(self, attr):
                    display_attributes[attr] = getattr(self, attr)
        args_str = ', '.join(
            [f'{attr}={repr(value)}' for attr, value in display_attributes.items()]
        )
        return f'{self.__class__.__name__}({args_str})'

    #
    #
    # Override CSVDataclass methods (to enable using CSVReport and tabulate)
    #
    #
    @classmethod
    def table_header(cls) -> Tuple[str, ...]:
        return ['id'] + cls._updatable_fields(deduplicate_xlink=True, xlink_suffix=False)

    def as_table_row(self, select_columns=None, display_full_objects=None) -> Tuple[str, ...]:
        display_full_objects = display_full_objects if display_full_objects is not None else config.DISPLAY_FULL_OBJECTS
        table_row = list()
        for datum in super().as_table_row(select_columns):
            if isinstance(datum, NetdotAPIDataclass):
                datum_str = datum._display(display_full_objects)
            else:
                datum_str = str(datum)
            table_row.append(datum_str)
        return table_row

    #
    #
    # Helper functions
    #
    #
    @classmethod
    def _prepare_class(cls):
        if not cls._initialized:
            cls._generate_and_attach_others_getAll_methods()
            cls._generate_and_attach_my_getter_methods()
            cls._generate_and_attach_others_m2m_add_methods()
            cls._generate_and_attach_others_add_xlink_methods()
            cls._logged_unused_fields = set()
            cls._initialized = True

    @classmethod
    def _infer_xlink_class_map(cls):
        """Infer the xlink class map from the Attributes that have Union[..., NetdotAPIDataclass] type hint.

        Returns:
            Dict[str, str]: A dictionary mapping xlink field names to their associated dataclass names.

        Examples:
            
                >>> import netdot
                >>> netdot.BackboneCable._infer_xlink_class_map()
                {'end_closet': 'Closet', 'owner': 'Entity', 'start_closet': 'Closet', 'type': 'CableType'}
    
                >>> netdot.Site._infer_xlink_class_map()
                {'availability': 'Availability', 'contactlist': 'ContactList'}
        """
        xlink_class_map = dict()
        for field, string_parser in cls._infer_base_parsers().items():
            if typing_inspect.is_union_type(string_parser):
                for arg in typing_inspect.get_args(string_parser):
                    # ! NOTE: str(arg) and __forward_arg__ are, 'Python 3 implementation details'
                    if 'ForwardRef' in str(arg) and 'netdot.' in str(arg):
                        xlink_class_map[field] = arg.__forward_arg__.replace('netdot.', '')
                        break
                    elif str(arg).startswith('netdot.'):
                        xlink_class_map[field] = str(arg).replace('netdot.', '')
                        break
        return xlink_class_map

    @classmethod
    def _NETDOT_ASSOCIATIVE_TABLE_other_class(cls, other_cls: 'NetdotAPIDataclass'):
        """Get the class that is different from 'other_cls'."""
        if not cls._NETDOT_ASSOCIATIVE_TABLE:
            raise TypeError(
                'This method is only valid for associative tables (many to many relationship only).'
            )
        cls_options = list(cls._related_classes().values())
        if other_cls not in cls_options:
            raise TypeError(
                f'Provided class {other_cls} is not a valid option. Valid options: {cls_options}'
            )
        cls_options.remove(other_cls)
        return cls_options[0]

    @classmethod
    def _NETDOT_ASSOCIATIVE_TABLE_other_class_xlink_name(cls, other_cls: 'NetdotAPIDataclass'):
        inv_xlink_class_map = {v: k for k, v in cls._infer_xlink_class_map().items()}
        return (
            inv_xlink_class_map[other_cls.__name__]
            if other_cls.__name__ in inv_xlink_class_map
            else other_cls.__name__.lower()
        )

    def _handle_xlink_setattr(self, name, value) -> bool:
        """__setattr__ helper function"""
        if isinstance(value, NetdotAPIDataclass) and hasattr(self, f'{name}_xlink'):
            self.__setattr__(f'{name}_xlink', value.id)
            super().__setattr__(name, value)
            return True
        elif name.endswith('_xlink'):
            non_xlink_value = getattr(self, name.replace('_xlink', ''))
            if isinstance(non_xlink_value, NetdotAPIDataclass):
                return True
        else:
            return False

    def _attempt_auto_update_if_enabled(self, name, value):
        """__setattr__ helper function"""
        if (
            self._post_init  # Do not try to run updates until after __init__ is done
            and self.id  # Only try to run updates if this is an update-able object
            and self.repository  # Only try to run updates if this object has a repository
            and self.repository._dry_run  # Only try to run updates if this is a dry run
            and self.repository._auto_update_on_dry_run  # Only try to run updates if auto_update is enabled[]
            and name
            in self._updatable_fields()  # Only try to run updates if this is an updatable field
        ):
            if self._auto_update_lock.acquire(
                blocking=False
            ):  # Only ever auto-run update once at a time
                try:
                    self.update()
                finally:
                    self._auto_update_lock.release()

    def _intake_DTO(self, data: Dict):
        return self._update_my_fields(self.from_DTO(data))

    def _update_my_fields(self, response: 'NetdotAPIDataclass'):
        if not isinstance(response, type(self)):
            raise TypeError(
                f'Expected response to be of type {type(self)}, got {type(response)}'
            )
        fields_to_update = (
            self._updatable_fields()
            + ['id']
            # + self.foreign_key_field_names(remove_suffix=True)
        )
        # NOTE: Locking here ensures that auto_update is disabled when we do "_update_my_fields"
        # This might be a bit cons
        self._auto_update_lock.acquire(blocking=False)
        for field_name in fields_to_update:
            setattr(self, field_name, getattr(response, field_name))
        self._auto_update_lock.release()
        return self

    def _assert_repository_attached(self):
        if not self._repository:
            raise netdot.exceptions.NetdotError(
                'Must have repository attached to use methods like: create, add_*,load_*, update, delete. Use with_repository(...) to fix.'
            )

    @classmethod
    def _pep8_method_friendly_name(cls):
        return cls.__name__.lower()

    @classmethod
    def _name_pluralized(cls):
        return utils.pluralize(cls.__name__)

    @classmethod
    def _get_xlink_class_name(cls, xlink: str):
        try:
            xlink_classname = xlink.replace('_xlink', '')
            return cls._infer_xlink_class_map()[xlink_classname]
        except KeyError:
            raise ValueError(f"Unknown xlink class name: '{xlink}' for NetdotAPIDataclass: '{cls.__name__}'")
            # return xlink

    @classmethod
    def foreign_key_field_names(cls, remove_suffix=False) -> List[str]:
        """Get the names of all the foreign key fields for this class.

        Returns:
            List[str]: List of all the foreign key fields for this class.

        Examples:

        >>> import netdot
        >>> netdot.BackboneCable.foreign_key_field_names()
        ['end_closet_xlink', 'owner_xlink', 'start_closet_xlink', 'type_xlink']

        >>> netdot.Site.foreign_key_field_names()
        ['availability_xlink', 'contactlist_xlink']
        """
        # Get all keys ending with the _xlink suffix. Example: asset_id_xlink
        #
        new_keys = cls.__dataclass_fields__.keys()
        foreign_keys = list(
            filter(
                lambda field_name: field_name.endswith('_xlink'),
                new_keys,
            )
        )
        if remove_suffix:
            return [key.replace('_xlink', '') for key in foreign_keys]
        return foreign_keys

    @classmethod
    def _related_classes(cls) -> Dict[str, 'NetdotAPIDataclass']:
        """Provide a dictionary holding all of the 'xlink' field names and their associated dataclasses.

        Returns:
            Dict[str, "NetdotAPIDataclass"]: All the associated fields, and their data classes.

        Example:

            >>> import netdot
            >>> netdot.BackboneCable._related_classes()
            {'end_closet_xlink': <class '...Closet'>, 'owner_xlink': <class '...Entity'>, 'start_closet_xlink': <class '...Closet'>, 'type_xlink': <class '...CableType'>}

            >>> netdot.Site._related_classes()
            {'availability_xlink': <class 'netdot...Availability'>, 'contactlist_xlink': <class 'netdot...ContactList'>}

        """
        related_object_types = {}
        for xlink in cls.foreign_key_field_names():
            xlink_class_name = cls._get_xlink_class_name(xlink)
            xlink_class_name = xlink_class_name.replace('_xlink', '')
            for other_dataclass in NetdotAPIDataclass.__subclasses__():
                if xlink_class_name.lower() == other_dataclass.__name__.lower():
                    related_object_types[xlink] = other_dataclass

        return related_object_types

    @classmethod
    def _updatable_fields(cls, deduplicate_xlink=True, xlink_suffix=True) -> List[str]:
        """Fields that can be updated via the Netdot API.

        Args:
            deduplicate_xlink (bool, optional): If True, will only return 1 attribute for each '_xlink' field-pair. Defaults to True.
            xlink_suffix (bool, optional): If True, will keep the '_xlink' suffix on the field names. Defaults to True.

        Returns:
            List[str]: Names of the fields of this object that can be updated.

        Example:

            >>> import netdot
            >>> netdot.Site._updatable_fields()
            ['name', 'aliases', 'availability_xlink', 'contactlist_xlink', 'gsf', 'number', 'street1', 'street2', 'state', 'city', 'country', 'zip', 'pobox', 'info']
            >>> netdot.Site._updatable_fields(False)
            ['name', 'aliases', 'availability', 'availability_xlink', 'contactlist', 'contactlist_xlink', 'gsf', 'number', 'street1', 'street2', 'state', 'city', 'country', 'zip', 'pobox', 'info']

        """
        def filter_fields(field_name):
            if field_name.startswith('_'):
                # Filter 'private' (start with _)
                return False
            elif field_name.upper() == field_name:
                # Filter ALL_CAPS_FIELDS (these are constants)
                return False
            elif field_name == 'id':
                return False
                # Filter 'id' (should only be provided via URL path)
            elif deduplicate_xlink and field_name in cls.foreign_key_field_names(remove_suffix=xlink_suffix):
                # Deduplicate the _xlink fields
                return False
            else:
                return True
        return list(filter(filter_fields, cls.__dataclass_fields__.keys()))

    def to_DTO(self) -> Dict:
        """Convert to a Data Transfer Object (compliant with NetDot REST API).

        Returns:
            Dict: Use as input to Netdot API POST calls, for creation/update operations.

        Example:

            >>> import netdot
            >>> contact_list = netdot.ContactList(id=123, name='foo')
            >>> site = netdot.Site(name='foo', contactlist=contact_list, city='Eugene')
            >>> site.to_DTO()
            {'name': 'foo', 'contactlist': 123, 'city': 'Eugene'}

        """
        # Create a dict (DTO) that represents this object
        dto = {field: getattr(self, field) for field in self._updatable_fields(False)}
        return handle_bool_values(handle_None_values(handle_xlink_fields(dto)))

    @classmethod
    def _is_xlink_sibling(cls, field_name):
        return f'{field_name}_xlink' in vars(cls).keys()

    @classmethod
    def _parse_DTO_field(cls, field_name: str, data: dict, string_parser):
        
        dto_field_name = field_name.replace(name_collision_marker, '')
        field_value = str(data[dto_field_name])
        if field_value.strip() == '' and not isinstance(string_parser, str):
            return field_value  # Don't try to parse empty strings (just return them)
        if field_value.strip() == '0' and (  # Do not try to parse '0' into an:
            string_parser == ipaddress.ip_address  # IP Address,
            or string_parser == MACAddress  # MACAddress, or
            or cls._is_xlink_sibling(field_name)  # Foreign Key.
        ):
            return None  # Don't try to parse '0' into an IP Address or MACAddress
        return string_parser(data[dto_field_name])

    @classmethod
    def from_DTO(
        cls,
        DTO_data: Dict,
        DTO_field_parsers: Dict = DEFAULT_DTO_FIELD_PARSERS,
        raise_parse_errors=None,
        warn_missing_fields=None,
    ) -> 'NetdotAPIDataclass':
        """Parse data retrieved from Netdot API into a NetdotAPIDataclass.

        Args:
            data_transfer_object (Dict): Dictionary of raw data returned from Netdot API.
            dto_field_parsers (Dict, optional): A dictionary holding field_name -> parse_field() functions.
                This is useful for when data returned from the NetDot API is not a string but actually some other data type.
                Defaults to DEFAULT_STRING_PARSERS. By default, all fields are parsed as strings.
                field_name may contain a single wildcard at the beginning, e.g. *_xlink will expand to used_by_xlink, owner_xlink, parent_xlink, etc...
            continue_on_parse_error (bool, optional): If True, will continue parsing even if a field cannot be parsed.

        Returns:
            NetdotAPIDataclass: The appropriate subclass of NetdotAPIDataclass.
        """
        raise_parse_errors = raise_parse_errors if raise_parse_errors is not None else config.RAISE_FIELD_PARSE_ERRORS
        warn_missing_fields = warn_missing_fields if warn_missing_fields is not None else config.WARN_MISSING_FIELDS
        if not DTO_data:
            raise ValueError(
                f'Cannot parse empty Data Transfer Object (DTO): {DTO_data}.'
            )
        data = dict(DTO_data.copy())
        missing_fields = []
        if DTO_field_parsers:
            field_parsers = dict(DTO_field_parsers.copy())
            field_parsers.update(cls._infer_base_parsers())
            field_parsers.update(cls._expand_wildcard_parsers(field_parsers))
            for field_name, string_parser in field_parsers.items():
                # Handle Union data types (xlinks/foreign keys)
                if typing_inspect.is_union_type(string_parser):
                    for arg in typing_inspect.get_args(string_parser):
                        if not isinstance(arg, NetdotAPIDataclass):
                            # If we find any non NetdotAPIDataclass, then THAT is our DTO parser
                            # Why? Netdot DTO doesn't contain nested objects (only string representations of those nested objects... which sometimes can still be parsed, e.g. into an ipaddress)
                            string_parser = arg
                            break
                if field_name.startswith('_') or field_name.upper() == field_name:
                    continue  # Skip '_private' and 'ALL_CAPS' fields
                try:
                    data[field_name] = cls._parse_DTO_field(
                        field_name, data, string_parser
                    )
                    # Handle fields that collide with Python keywords (class, type, def, return, etc...)
                    if field_name.endswith(name_collision_marker):  # ? What does this do??
                        del data[field_name.replace(name_collision_marker, '')]
                except KeyError:
                    if field_name.endswith('_xlink'):
                        continue  # Expect _xlink to be absent if it is unset in Netdot
                    data[field_name] = data
                    missing_fields.append(field_name)
                except Exception as parse_error:
                    logger.warning(
                        textwrap.dedent(
                            f"""\
                            Unable to parse '{field_name}' for '{cls.__name__}', value: {data[field_name]}
                            (Using parser {str(string_parser)}, got error: {parse_error})"""
                        )
                    )
                    if raise_parse_errors:
                        raise parse_error
        if warn_missing_fields and set(missing_fields).difference(
            inconsistent_and_ignorable_fields
        ):
            logger.debug(
                f"NetDot '{cls.__name__}' response missing field(s): {missing_fields}"
            )
        return cls._parse_data_transfer_obj(data)

    @classmethod
    def _parse_data_transfer_obj(cls, data_transfer_object):
        """Parse some data retrieved from Netdot into a proper NetdotAPIDataclass.

        Args:
            data_transfer_object (Dict): Dictionary of raw data returned from Netdot API.

        Returns:
            NetdotAPIDataclass: The appropriate subclass of NetdotAPIDataclass.
        """
        cls._log_unknown_fields(data_transfer_object)

        # Construct the new object!
        fields_to_parse = cls._get_known_fields(data_transfer_object)
        data_to_parse = {key: data_transfer_object[key] for key in fields_to_parse}
        return cls(**data_to_parse)

    @classmethod
    def _get_known_fields(cls, data_transfer_object):
        valid_fields = set(
            [field_name.replace(name_collision_marker, '') for field_name in cls.__dataclass_fields__.keys()]
        )
        valid_fields |= set(cls.__dataclass_fields__.keys())
        provided_fields = set(data_transfer_object.keys())
        return provided_fields.intersection(valid_fields)

    @classmethod
    def _get_unknown_fields(cls, data_transfer_object):
        valid_fields = set(
            [field_name.replace(name_collision_marker,'') for field_name in cls.__dataclass_fields__.keys()]
        )
        valid_fields |= set(cls.__dataclass_fields__.keys())
        provided_fields = set(data_transfer_object.keys())
        return provided_fields.difference(valid_fields)

    @classmethod
    def _log_unknown_fields(cls, data_transfer_object):
        unused_fields = cls._get_unknown_fields(data_transfer_object)
        if unused_fields:
            unused_data = {key: data_transfer_object[key] for key in unused_fields}
            # Always log a debug message with ALL the data
            logger.debug(
                f'Unparsed data ({cls.__module__}.{cls.__name__}): {unused_data}'
            )
            # If this is the first time we've seen these 'unused field(s)', then log a warning!
            if not unused_fields.issubset(cls._logged_unused_fields):
                cls._logged_unused_fields = cls._logged_unused_fields.union(
                    unused_fields
                )
                logger.warning(
                    f'Received unknown field(s): {unused_data} '
                    + f'(to fix, add unknown field(s) to {cls.__module__}.{cls.__name__} )'
                )

    @classmethod
    def _expand_wildcard_parsers(cls, DTO_field_parsers: Dict[str, Callable]) -> None:
        """Expand any 'wildcard' parsers.
        NOTICE: This method updates the provided Dict in place.

        If any of DTO_field_parsers starts with "*", they will be expanded to match any of the fields available in DTO_data.

        Example:

            Assume we have NetdotAPIDataclass FooAddress.

            >> from dataclasses import dataclass
            >> @dataclass
            .. class FooAddress(NetdotAPIDataclass):
            ..     local_addr: ipaddress.ip_address
            ..     mgmt_addr: ipaddress.ip_address

            >> DTO_field_parsers = { '*_addr': ipaddress.ip_address }

            >> FooAddress.expand_wildcard_parsers(DTO_field_parsers)
            {'local_addr': <function ip_address ...>, 'mgmt_addr': <function ip_address ...>}
        """

        def is_wildcard_pattern(field_name):
            return field_name.startswith('*') or field_name.endswith('*')

        wildcard_patterns = filter(is_wildcard_pattern, DTO_field_parsers)
        wildcard_parsers = {
            pattern: DTO_field_parsers[pattern] for pattern in wildcard_patterns
        }
        for wildcard_pattern, parser in wildcard_parsers.items():
            del DTO_field_parsers[wildcard_pattern]
            pattern = wildcard_pattern.strip('*')
            for actual_field_name in cls.__dataclass_fields__:
                if (
                    wildcard_pattern.startswith('*')
                    and actual_field_name.endswith(pattern)
                ) or (
                    wildcard_pattern.endswith('*')
                    and actual_field_name.startswith(pattern)
                ):
                    DTO_field_parsers[actual_field_name] = parser
        return DTO_field_parsers

    @classmethod
    def _infer_base_parsers(cls) -> Dict[str, Callable]:
        base_parsers = {
            field_name: dataclass_field.type
            for field_name, dataclass_field in cls.__dataclass_fields__.items()
            # if dataclass_field.type is not str
        }
        for field_name, parser in base_parsers.items():
            if parser is bool:
                base_parsers[field_name] = parse.Boolean
        return base_parsers

    @classmethod
    def _table_name(cls):
        return cls._NETDOT_TABLE_NAME or cls.__name__

    @classmethod
    def _related_class_repeats(cls, other_cls: 'NetdotAPIDataclass'):
        return list(cls._related_classes().values()).count(other_cls) > 1

    #
    #
    # Methods for 'Generating and attaching methods'
    #
    #
    @classmethod
    def _attach_methods(cls, methods):
        for method in methods:
            setattr(cls, method.__name__, method)

    @classmethod
    def _generate_and_attach_others_m2m_add_methods(cls):
        for xlink, xlink_dataclass in cls._related_classes().items():
            if cls._NETDOT_ASSOCIATIVE_TABLE:
                xlink_adder = cls._generate_your_many_to_many_add_method(
                    xlink, xlink_dataclass
                )
                xlink_dataclass._attach_methods([xlink_adder])

    @classmethod
    def _generate_and_attach_others_add_xlink_methods(cls):
        for xlink, xlink_dataclass in cls._related_classes().items():
            xlink_adder = cls._generate_your_xlink_add_method(
                xlink,
                xlink_dataclass,
                include_xlink_in_name=cls._related_class_repeats(xlink_dataclass),
            )
            xlink_dataclass._attach_methods([xlink_adder])

    @classmethod
    def _generate_and_attach_my_getter_methods(cls):
        for xlink, xlink_dataclass in cls._related_classes().items():
            xlink_loader = cls._generate_my_xlink_load_method(xlink, xlink_dataclass)
            cls._attach_methods([xlink_loader])

    @classmethod
    def _generate_and_attach_others_getAll_methods(cls):
        """Generate all the 'load_XXXs' methods for classes that this class is referenced by."""
        for xlink, dataclass in cls._related_classes().items():
            xlink_loaders = list()
            if cls._NETDOT_ASSOCIATIVE_TABLE:
                xlink_loaders.append(
                    cls._generate_your_many_to_many_load_method(xlink, dataclass)
                )
                xlink_loaders.append(
                    cls._generate_your_xlink_load_method(xlink, dataclass)
                )
            else:
                xlink_loaders.append(
                    cls._generate_your_xlink_load_method(
                        xlink,
                        dataclass,
                        include_xlink_in_name=cls._related_class_repeats(dataclass),
                    )
                )
            dataclass._attach_methods(xlink_loaders)

    @classmethod
    def _generate_my_xlink_load_method(my_cls, xlink, other_cls):
        """Generate the `load_xlink()` method to be attached to cls.

        E.g. will generate load_site() when other_cls is netdot.Site.
        """
        def xlink_loader(self) -> other_cls:  # type: ignore
            self._assert_repository_attached()
            xlink_id = getattr(self, xlink)
            if not xlink_id:
                return None
            download_function_name = f'get_{other_cls._pep8_method_friendly_name()}'
            download_function = getattr(self.repository, download_function_name)
            return download_function(xlink_id)

        xlink_loader.__doc__ = f"""Load the {xlink.replace('_xlink', '')} ({other_cls.__name__}) associated to this {my_cls.__name__}.

    Returns:
        netdot.{other_cls.__name__}: The full {other_cls.__name__} object if available, else None.
            """
        xlink_loader.__name__ = f"load_{xlink.replace('_xlink', '').replace('_id','')}"
        return xlink_loader

    @classmethod
    def _generate_your_many_to_many_add_method(
        cls, xlink: str, my_cls: 'NetdotAPIDataclass'
    ):
        """Generate a `add_xlinks()` method to be attached to my_cls (NOT m2m_cls)

        E.g. will generate add_device() when my_cls is netdot.Device
        """
        m2m_cls = cls
        other_cls = m2m_cls._NETDOT_ASSOCIATIVE_TABLE_other_class(my_cls)
        other_cls_xlink_name = m2m_cls._NETDOT_ASSOCIATIVE_TABLE_other_class_xlink_name(
            other_cls
        )

        def xlink_adder(self, data: other_cls) -> other_cls:
            self._assert_repository_attached()
            new_object = m2m_cls(
                **{
                    other_cls_xlink_name: data,
                    my_cls._pep8_method_friendly_name(): self,
                }
            )
            return self.repository.create_new(new_object)

        xlink_adder.__doc__ = f"""Add a {other_cls.__name__} to this {my_cls.__name__} (via {m2m_cls.__name__}).

    Args:
        data (netdot.{other_cls.__name__}): The {other_cls.__name__} to add to this {my_cls.__name__}.

    Returns:
        netdot.{m2m_cls.__name__}: The newly created {m2m_cls.__name__}.

    Raises:
        ProtocolError: Can occur if your connection with Netdot has any issues.
        HTTPError: For any HTTP errors. (error details can be found in Netdot's apache server logs)
        """
        xlink_adder.__name__ = f'add_{other_cls_xlink_name}'
        return xlink_adder

    @classmethod
    def _generate_your_many_to_many_load_method(
        cls, xlink: str, my_cls: 'NetdotAPIDataclass'
    ):
        """Generate a `load_xlinks()` method to be attached to my_cls (NOT m2m_cls)

        E.g. will generate load_devices() when my_cls is netdot.Device.
        """
        m2m_cls = cls
        other_cls = m2m_cls._NETDOT_ASSOCIATIVE_TABLE_other_class(my_cls)
        other_cls_xlink_name = m2m_cls._NETDOT_ASSOCIATIVE_TABLE_other_class_xlink_name(
            other_cls
        )

        def xlink_loader(self, ignore_404=True) -> List[other_cls]:
            self._assert_repository_attached()
            try:
                # Download all the many-to-many objects
                download_m2m_function_name = f"get_{m2m_cls._name_pluralized().lower()}_by_{xlink.replace('_xlink','')}"
                download_m2m_function = getattr(
                    self.repository, download_m2m_function_name
                )
                downloaded_m2m_data = download_m2m_function(self.id)
                # Download the data itself
                download_function_name = f'get_{other_cls._pep8_method_friendly_name()}'
                download_function = getattr(self.repository, download_function_name)
                downloaded_data = list()
                # TODO Can we parallelize these requests? See _create_thread_pool
                for m2m_data in downloaded_m2m_data: 
                    try:
                        m2m_other_id = getattr(
                            m2m_data, f'{other_cls_xlink_name}_xlink'
                        )
                        downloaded_data.append(download_function(m2m_other_id))
                    except netdot.exceptions.HTTPError as e:
                        if (
                            hasattr(e.response, 'status_code')
                            and e.response.status_code == 404
                        ):
                            if ignore_404:
                                continue
                            else:
                                logger.error(
                                    f"404 {other_cls.__name__} with id {m2m_other_id}"
                                )
                        else:
                            raise e
                return downloaded_data
            except netdot.exceptions.HTTPError as e:
                if (
                    ignore_404
                    and hasattr(e.response, 'status_code')
                    and e.response.status_code == 404
                ):
                    return []
                else:
                    raise e

        xlink_loader.__doc__ = f"""Load the {utils.pluralize(other_cls_xlink_name)} ({other_cls._name_pluralized()}) associated to this {my_cls.__name__}.

    > NOTE: This will make `N+1` HTTP Requests (where N is the number of {other_cls._name_pluralized()} associated to this {my_cls.__name__}).

    You might prefer :func:`load_{m2m_cls._name_pluralized().lower()}` over this method, if you want to load the many-to-many objects themselves. (and not make N+1 HTTP Requests)

    Args:
        ignore_404 (bool, optional): If True, will continue upon encountering HTTP 404 errors. Defaults to True.

    Returns:
        List[netdot.{other_cls.__name__}]: Any/All {other_cls._name_pluralized()} related to this {my_cls.__name__}, or an empty list if none are found.

    Raises:
        ProtocolError: Can occur if your connection with Netdot has any issues.
        HTTPError: For any HTTP errors. (error details can be found in Netdot's apache server logs)
        """
        xlink_loader.__name__ = f'load_{utils.pluralize(other_cls_xlink_name)}'
        return xlink_loader

    @classmethod
    def _generate_your_xlink_load_method(
        my_cls, xlink: str, other_cls: 'NetdotAPIDataclass', include_xlink_in_name=False
    ):
        """Generate the `load_xlinks()` method to be attached to other_cls.

        E.g. will generate load_devices() when my_cls is netdot.Device.=T
        """

        def xlink_loader(self, ignore_404=True) -> List[my_cls]:
            self._assert_repository_attached()
            download_function_name = f"get_{my_cls._name_pluralized().lower()}_by_{xlink.replace('_xlink','')}"
            download_function = getattr(self.repository, download_function_name)
            try:
                return download_function(self.id)
            except netdot.exceptions.HTTPError as e:
                    if (
                        ignore_404
                        and hasattr(e.response, 'status_code')
                        and e.response.status_code == 404
                    ):
                        return []
                    else:
                        raise e

        docstring = f'Load the {my_cls._name_pluralized()} associated to this {other_cls.__name__}.'
        if other_cls.__name__.lower() != xlink.replace('_xlink', ''):
            docstring += (
                f" (Via the `{my_cls.__name__}.{xlink.replace('_xlink','')}` attribute)"
            )
        xlink_loader.__doc__ = f"""{docstring}

    Args:
        ignore_404 (bool, optional): If True, will continue upon encountering HTTP 404 errors. Defaults to True.

    Returns:
        List[netdot.{my_cls.__name__}]: All/Any {my_cls._name_pluralized()} related to this {other_cls.__name__}.
        
    Raises:
        ProtocolError: Can occur if your connection with Netdot has any issues.
        HTTPError: For any HTTP errors. (error details can be found in Netdot's apache server logs)
        """
        method_name = 'load'
        if include_xlink_in_name:
            method_name += f"_{xlink.replace('_xlink','')}"
        method_name += f'_{my_cls._name_pluralized().lower()}'
        xlink_loader.__name__ = method_name
        return xlink_loader

    @classmethod
    def _generate_your_xlink_add_method(
        my_cls, xlink: str, other_cls: 'NetdotAPIDataclass', include_xlink_in_name=False
    ):
        """Generate the `add_xlink()` method to be attached to other_cls.

        E.g. will generate add_device() when my_cls is netdot.Device.
        """

        def xlink_adder(self, data: my_cls) -> my_cls:
            self._assert_repository_attached()
            setattr(data, xlink.replace('_xlink', ''), self)
            return self.repository.create_new(data)

        xlink_adder.__doc__ = f"""Add a {my_cls.__name__} to this {other_cls.__name__}.

    Returns:
        netdot.{my_cls.__name__}: The created {my_cls.__name__}.

    Raises:
        ProtocolError: Can occur if your connection with Netdot has any issues.
        HTTPError: For any HTTP errors. (error details can be found in Netdot's apache server logs)
        """
        method_name = 'add'
        method_name += f'_{my_cls.__name__.lower()}'
        if include_xlink_in_name:
            method_name += f"_as_{xlink.replace('_xlink','')}"

        xlink_adder.__name__ = method_name
        return xlink_adder
