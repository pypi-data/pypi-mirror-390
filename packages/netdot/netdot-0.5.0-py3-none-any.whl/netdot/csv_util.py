"""Classes and functions that generate CSV files.

This module is focused on generating a CSV file via the CSVReport class, which 
is a collections of CSVDataclass objects.
"""
import logging
import operator
import os
from typing import Generic, Iterable, List, Tuple, TypeVar

import pathvalidate

from . import io

logger = logging.getLogger(__name__)


class CSVDataclass:
    """Base class that provides a "table_header" class property 
    as well as a "as_table_row()" method for simple dataclasses.dataclass.
    """
    @classmethod
    def table_header(cls) -> Tuple[str, ...]:
        """Return the *names* from all attributes of this class.

        Returns:
            Tuple[str,...]: The names of the attributes for this class.
        """
        return tuple(cls.__dataclass_fields__.keys())

    def as_table_row(self, select_columns: Iterable[str] = None) -> Tuple[str, ...]:
        """Return the data from all attributes of this object.

        Args:
            select_columns (Iterable[str], optional): Which data to be returned? If unset, all data returned.

        Returns:
            Tuple[str,...]: The values of all the attributes for this object.
        """
        obj_data = vars(self)
        if select_columns:
            row = tuple(obj_data[col] for col in select_columns)
        else:
            row = tuple(obj_data.values())
        row_as_strs = tuple(str(datum) for datum in row)
        return row_as_strs


CSVDataclass_t = TypeVar('CSVDataclass_t', bound=CSVDataclass)

class CSVReport(Generic[CSVDataclass_t]):
    """Base class for reports that can be exported to Comma Separated Values (CSV).
    """
    def __init__(self, items: List[CSVDataclass_t], table_header: Tuple[str,...] = None):
        self._header: Tuple[str,...] = table_header
        self._items: List[CSVDataclass_t] = items

    def sort(self, *sort_by: str):
        """Sort this report. (in-place)

        Args:
            sort_by (Union[str,List[str]], optional): The column(s) to be sorted by. By default sort by the first column indicated by table_header.
        """
        if not sort_by:
            sort_by = self.table_header()
        self.items.sort(key=operator.attrgetter(*sort_by))

    @property
    def items(self) -> List[CSVDataclass_t]:
        return self._items

    def table_header(self) -> Tuple[str, ...]:
        """Return the CSV header for this Report.

        Returns:
            Tuple[str,...]: Names of columns for this report.
        """
        if self._header: 
            return self._header
        try:
            return self.items[0].table_header()
        except (IndexError, AttributeError):
            raise ValueError(f'No header provided. Unable to determine table header for {self.__class__.__name__} with data "{self.items}".')

    def _as_tuples(self) -> List[Tuple]:
        select_cols = self.table_header()
        return [item.as_table_row(select_cols) for item in self.items]

    def as_csv(self, delim=',', override_header: Iterable[str] = None) -> str:
        """Produce this data structure into a CSV.

        Args:
            delim (str, optional): CSV delimiter to be used. Defaults to ','.
            override_header (Iterable[str], optional): Enables overriding the default CSV header (labels only, cannot be used to 'select columns'). (Must be same length as this report's default `table_header`).

        Raises:
            ValueError: If override_header is invalid.

        Returns:
            str: This report, in CSV format.
        """        
        header = self.table_header()
        if override_header:
            if len(override_header) != len(header):
                raise ValueError(f'''override_header must be length {len(header)}, to align with table_header: {header}. override_header length: {len(override_header)}. override_header: {override_header})''')
            header = override_header
        return as_csv(self._as_tuples(), header, delim)

    def save_as_file(self, filename: str, output_directory: str = './', **kwargs) -> int:
        """Save this CSVReport to a file.

        Args:
            output_directory (str): The path where the CSV will be saved.
            filename (str): Will be used as the file name.
            kwargs: Additional arguments are passed to `as_csv()` (e.g. override_header)

        Returns:
            int: Amount of bytes written to the file. (See `TextIOBase.write()`)
        """
        io.ensure_directory_exist(output_directory)
        filename = _sanitize_csv_filename(filename)
        out_file_path = os.path.join(output_directory, filename)
        with open(out_file_path, 'w') as out_file:
            return out_file.write(self.as_csv(**kwargs))


def as_csv(data: Iterable[Tuple], header: Iterable[str] = None, delim=',') -> str:
    """Convert a list of tuples into a CSV table.

    Args:
        data (Iterable[Tuple]): The data tuples. Each tuple should be the same size, and the same size as the header.
        header (Iterable[str]): Header for the CSV table. Optional.
        delim (str, optional): CSV delimiter. Defaults to ','.

    Returns:
        str: The data, represented as a CSV.
    """
    csv_lines = []
    if header:
        csv_lines.append(delim.join(header))

    def sanitize(datum):
        return f'"{datum}"' if delim in str(datum) else str(datum)
    for line_data in data:
        line_data = list(map(sanitize, line_data))
        csv_lines.append(delim.join(line_data))

    return '\n'.join(csv_lines)


def _sanitize_csv_filename(filename: str) -> str:
    if not filename.endswith('.csv'):
        filename = f'{filename}.csv'
    return pathvalidate.sanitize_filename(filename)
