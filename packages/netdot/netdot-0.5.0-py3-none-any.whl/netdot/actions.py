from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, List, Tuple, TypeVar

import netdot
from netdot import config
from netdot.csv_util import CSVDataclass
from netdot.dataclasses import NetdotAPIDataclass

U = TypeVar('U', bound='netdot.NetdotAPIDataclass')


class ActionTypes(IntEnum):
    CREATE = 1
    UPDATE = 2
    DELETE = 3

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'


def diff_string(old: str, new: str) -> str:
    """Create a 'diff string' if a pair of strings have any differences.

    The intention is to be able to provide a useful text representation of a diff that
    fits well into a CSV format.

    Args:
        old (str): The old string
        new (str): The new string.

    Returns:
        str: If 'new' and 'old' are different, return "[-old-]+new+". (Otherwise, return the old string).
    """
    if new == old:
        return old
    elif old:
        return f'[-{old}-]+{new}+'
    else:
        return f'+{new}+'


@dataclass(frozen=True)
class NetdotAction(CSVDataclass):
    action_type: ActionTypes
    id: int
    new_data: NetdotAPIDataclass
    old_data: NetdotAPIDataclass

    def table_header(self) -> Tuple[str, ...]:
        """Return a list of columns, to be used as a table header for objects of this class.

        > Works will with the as_table_row() method.

        Returns:
            Tuple[str,...]: A list of columns.
        """
        data = self.new_data if self.new_data else self.old_data
        if not data:
            raise ValueError("Cannot generate table header for action with no data (provide either `new_data` or `old_data` for all of your NetdotActions to avoid this error)")
        header = ['action'] + list(data.table_header())
        return tuple(header)

    def as_table_row(self, select_columns: Iterable[str] = None, maxchars=None, display_full_objects=None) -> Tuple[str, ...]:
        """Return a representation of this action as a table row (tuple).

        Args:
            select_columns (Iterable[str], optional): Which attributes of this object to be returned. Defaults to `table_header()` if None provided.
            maxchars (int, optional): Truncate each attribute to this many characters. Defaults to config.TERSE_MAX_CHARS.
            display_full_objects (bool, optional): If a cell contains a Netdot Object, use it's full __repr__ function, to display the dataclass with all of its attributes. Defaults to False (so will only DISPLAY_ATTRIBUTES per each dataclass).

        Returns:
            List[str, ...]: String representations of the attributes of this object.
        """
        maxchars = maxchars or config.TERSE_MAX_CHARS
        display_full_objects = display_full_objects if display_full_objects is not None else config.DISPLAY_FULL_OBJECTS
        table_row = [self.action_type.name[:maxchars]]
        for datum in self._as_table_row(select_columns):
            if isinstance(datum, NetdotAPIDataclass):
                datum_str = datum._display(display_full_objects)
            else:
                datum_str = str(datum)
            table_row.append(datum_str[:maxchars])
        return table_row


    def generate_log_for_action(self, truncate=None, completed=False) -> str:
        """Generate a log message for this action.

        Args:
            truncate (int, optional): Truncate the message to this many characters. Defaults to None.
            completed (bool, optional): Whether the action has been completed. Defaults to False.

        Returns:
            str: A log message indicating exactly what will change if this action is (was) completed.
        """
        take_action = self.action_type.name
        object_type = (
            self.old_data.__class__.__name__
            if self.action_type == ActionTypes.DELETE
            else self.new_data.__class__.__name__
        )
        data = (
            self.old_data if self.action_type == ActionTypes.DELETE else self.new_data
        )
        first_word = 'Will' if not completed else 'Finished'
        message = f'{first_word} {take_action} {object_type}: {data}'
        if self.action_type == ActionTypes.UPDATE:
            message += f" (replacing: {self.old_data})"
        if truncate:
            truncate = max(config.TRUNCATE_MIN_CHARS, truncate)
            truncate = truncate - len('...')
            if len(message) < truncate:
                return message
            else:
                return message[:truncate]+'...'

        else:
            return message

    def _as_table_row(self, fields=None) -> Tuple[str, ...]:
        """Represent this action as a table row, ordered per `table_header` property.

        > Works well with the table_header Class Property.

        If there is a difference, the 'diff' is represented according to the
        netdot.actions.diff_string() function.=

        Returns:
            Tuple: Representation of this action as a row of data.
        """
        as_table_row_methods = {
            ActionTypes.CREATE: self._as_table_row_CREATE,
            ActionTypes.DELETE: self._as_table_row_DELETE,
            ActionTypes.UPDATE: self._as_table_row_UPDATE,
        }
        return tuple(as_table_row_methods[self.action_type](fields))

    def _as_table_row_DELETE(self, fields=None):
        fields = self._fields_sans_action(fields)
        return [getattr(self.old_data, field) for field in fields]

    def _as_table_row_UPDATE(self, fields=None):
        fields = self._fields_sans_action(fields)
        return [
            diff_string(getattr(self.old_data, field), getattr(self.new_data, field))
            for field in fields
        ]

    def _as_table_row_CREATE(self, fields=None):
        fields = self._fields_sans_action(fields)
        return [getattr(self.new_data, field) for field in fields]

    def _fields_sans_action(self, fields) -> List[str]:
        """The 'action' field is not part of the inner dataclass, so remove it from the list of fields and handle it separately (see as_table_row).
        """
        if not fields:
            fields = self.table_header()
        if 'action' in fields:
            fields = list(fields)
            fields.remove('action')
        return fields