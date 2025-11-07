import logging
import pickle
import shutil
import threading
from typing import List

from tabulate import tabulate
from tqdm import tqdm

import netdot
from netdot import NetdotAPIDataclass, actions, config, utils
from netdot.csv_util import CSVDataclass

logger = logging.getLogger(__name__)


class UnitOfWork:
    """Prepare some set of changes to be made in Netdot. Submit these changes using save_changes()."""

    _initialized = False

    def __init__(
        self,
    ):
        UnitOfWork.prepare_class()
        self._actions: List[actions.NetdotAction] = list()
        self._completed_actions = list()
        self._responses = list()
        self._action_in_progress: actions.NetdotAction = None
        self._failed_actions: List[actions.NetdotAction] = list()
        self._failed_actions_exceptions: List[Exception] = list()
        self._lock = threading.Lock()

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['_lock']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Restore the unpicklable entries.
        self._lock = threading.Lock()

    def __len__(self):
        return len(self._actions)

    @classmethod
    def prepare_class(cls):
        if not cls._initialized:
            netdot.initialize()
            cls._initialized = True

    @classmethod
    def from_action_list(cls, action_list: List['actions.NetdotAction'], **kwargs):
        new_unit_of_work = cls(**kwargs)
        new_unit_of_work._actions = action_list
        return new_unit_of_work

    def save_as_pickle(self, filename: str = config.ERROR_PICKLE_FILENAME) -> str:
        """Save this Unit of Work to a file.

        To be loaded in the future using :func:`load()`.

        Args:
            filename (str, optional): The file to save to. Defaults to a dynamic "defaults.ERROR_PICKLE_FILENAME" (which includes version and timestamp).
        """
        with open(filename, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        return filename

    @staticmethod
    def load(filename):
        """Load a Unit of Work from a pickle file.

        Args:
            filename (str): The file to load from.

        Returns:
            UnitOfWork: The Unit of Work that was loaded.
        """
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def as_list(self):
        """Get a copy of to-be-completed actions in this Unit of Work.

        Returns:
            List[NetdotAction]: The list of to-be-completed actions.
        """
        return list(self._actions)

    def _append_deduplicated_update(self, new_action: actions.NetdotAction):
        """Add an UPDATE action to this Unit of Work, ensuring that any prior updates to that same object are removed (since the latest update will contain all changes)"""

        for action in self._actions:
            if action.action_type != actions.ActionTypes.UPDATE:
                continue
            if not isinstance(new_action.new_data, type(action.new_data)):
                continue
            if action.id != new_action.id:
                continue
            # Cleanup any action that is updating the same object
            self._actions.remove(action)
        self._actions.append(new_action)

    def create(self, new_data: NetdotAPIDataclass, print_changes=False, one_line=True):
        """Create a new object in Netdot.

        Args:
            new_data (netdot.NetdotAPIDataclass): The new data to use when creating the object in Netdot.
            truncate (int): Truncate the message to this many characters. Defaults to None.

        Raises:
            TypeError: If new_data is not a subclass of NetdotAPIDataclass.
        """
        if not isinstance(new_data, NetdotAPIDataclass):
            raise TypeError(
                f'Expect new_data to be subclass of NetdotAPIDataclass, instead got: {type(new_data)}'
            )
        action = actions.NetdotAction(
            actions.ActionTypes.CREATE,
            id=None,
            new_data=new_data,
            old_data=None,
        )
        if print_changes:  # pragma: no cover
            max_chars = None
            if one_line:
                max_chars = shutil.get_terminal_size().columns
            print(action.generate_log_for_action(truncate=max_chars))
        self._actions.append(action)

    def update(
        self,
        old_data: NetdotAPIDataclass,
        new_data: NetdotAPIDataclass,
        print_changes=False,
        one_line=True,
        deduplicate=True,
    ):
        """Update an existing object in Netdot.

        Args:
            new_data (netdot.NetdotAPIDataclass): The new data to use when updating.
            old_data (netdot.NetdotAPIDataclass): The old data that is going to be replaced.
            deduplicate (bool): If True, consolidate duplicate UPDATE actions that are added to this Unit of Work.

        Raises:
            TypeError: If new_data and old_data are not the same type (or not a subclass of NetdotAPIDataclass).
        """
        if (
            # fmt: off
            not isinstance(old_data, type(new_data))
            or not isinstance(new_data, NetdotAPIDataclass)
            # fmt: on
        ):
            raise TypeError(
                f"""Invalid argument, expecting both new_data and old_data to be the same subclass of NetdotAPIDataclass, but got: 
    new_data: {new_data}  
    old_data: {old_data}
    """
            )
        action = actions.NetdotAction(
            actions.ActionTypes.UPDATE,
            id=old_data.id,
            new_data=new_data,
            old_data=old_data,
        )

        if print_changes:  # pragma: no cover
            max_chars = None
            if one_line:
                max_chars = shutil.get_terminal_size().columns
            print(action.generate_log_for_action(truncate=max_chars))
        if deduplicate:
            self._append_deduplicated_update(action)
        else:
            self._actions.append(action)

    def delete(self, old_data: NetdotAPIDataclass, print_changes=False, one_line=True):
        """Delete an existing object from Netdot.

        Args:
            old_data (netdot.NetdotAPIDataclass): The object that will be deleted (must include an 'id').

        Raises:
            TypeError: If old_data is not a subclass of NetdotAPIDataclass.
        """
        if not isinstance(old_data, NetdotAPIDataclass):
            raise TypeError(
                f'Expect old_data to be subclass of NetdotAPIDataclass, instead got: {old_data}'
            )
        action = actions.NetdotAction(
            actions.ActionTypes.DELETE,
            id=old_data.id,
            new_data=None,
            old_data=old_data,
        )
        if print_changes:  # pragma: no cover
            max_chars = None
            if one_line:
                max_chars = shutil.get_terminal_size().columns
            print(action.generate_log_for_action(truncate=max_chars))

        self._actions.append(action)

    def without_action_types(self, action_types: List['actions.ActionTypes']):
        """Get a copy of this Unit of Work with the selected actions removed.

        Args:
            action_types (List[actions.NetdotAction]): The types of actions to be removed.

        """

        def is_action_of_interest(action: actions.NetdotAction):
            return action.action_type not in action_types

        filtered_actions_list = list(filter(is_action_of_interest, self._actions))
        return UnitOfWork.from_action_list(filtered_actions_list)

    def with_action_types(self, action_types: List['actions.SiteActionTypes']):
        """Get a copy of this Unit of Work containing ONLY the selected actions.

        Args:
            action_types (List[actions.NetdotAction]): The types of actions to keep.
        """

        def is_action_of_interest(action: actions.NetdotAction):
            return action.action_type in action_types

        filtered_actions_list = list(filter(is_action_of_interest, self._actions))
        return UnitOfWork.from_action_list(filtered_actions_list)

    def with_data_type(self, data_type: NetdotAPIDataclass):
        """Get a copy of this Unit of Work containing actions of ONLY the selected data type.

        Args:
            data_type (NetdotAPIDataclass): The type of data to keep.
        """

        def is_action_of_interest(action: actions.NetdotAction):
            return isinstance(action.new_data, data_type) or isinstance(
                action.old_data, data_type
            )

        filtered_actions_list = list(filter(is_action_of_interest, self._actions))
        return UnitOfWork.from_action_list(filtered_actions_list)

    def failed_action(self, index=-1) -> actions.NetdotAction:
        """Get the action that failed when trying to save changes to Netdot.

        Args:
            index (int, optional): Index for accessing the list of actions that have failed. Defaults to -1 (latest failed action).

        Returns:
            actions.NetdotAction: The action that failed when trying to save changes to Netdot.
        """
        if self._failed_actions:
            return self._failed_actions[index]

    def failed_action_exception(self, index=-1) -> Exception:
        """Get the exception that occurred when trying to save changes to Netdot.

        Args:
            index (int, optional): Index for accessing the list of exceptions that have occurred. Defaults to -1 (latest exception).

        Returns:
            Exception: The exception that occurred when trying to save changes to Netdot.
        """
        if self._failed_actions_exceptions:
            return self._failed_actions_exceptions[index]

    def failed_action_msg(self, index=-1) -> str:
        """If 'save_changes' failed on some action, use this to get info about the failed action.

        Returns:
            str: A message indicating what the action would have done, and what exception occurred that prevented it from being completed.
        """
        if self.failed_action(index):
            return f"""{self.failed_action(index).generate_log_for_action()}
---> Failed with exception: {self.failed_action_exception(index)}
"""
        return None

    def failed_actions_msgs(self) -> str:
        """Print a message for each action that has failed.

        Returns:
            str: A single long message that includes all failed actions and their exceptions.
        """
        messages = []
        for index in range(len(self._failed_actions)):
            messages.append(f'{index+1}. {self.failed_action_msg(index)}')
        return '\n\n'.join(messages)

    def status_report(self, terse=None):
        """Show a report of all actions that have been completed, and all actions that remain to be completed (including any failed action(s)).

        Args:
            terse (bool, optional): Whether to truncate each line according to your terminal width. Defaults to config.TERSE.
        """
        terse = terse if terse is not None else config.TERSE
        message = f"""
Completed Actions:

{self.dry_run_of_actions(self._completed_actions, one_line=terse, completed=True)}

Remaining Actions:

{self.dry_run(terse=terse)}

"""
        if self.failed_action():
            message += 'Failed Action(s):\n\n'
            message += self.failed_actions_msgs()
        return message

    def changes_as_tables(
        self, terse=None, select_cols=None, display_full_objects=None
    ) -> str:
        """Show ASCII table(s) representing all of the changes to be made (grouped into tables based on Netdot Data Types).

        Args:
            terse (bool, optional): Whether to truncate data in each column. Defaults to config.TERSE
            select_cols (List[str], optional): Which columns to include in the table. Defaults to None (all columns).
        """
        tabulated_results = []
        for dataclass in sorted(
            NetdotAPIDataclass.__subclasses__(), key=lambda c: c.__name__
        ):
            terse = terse if terse is not None else config.TERSE
            display_full_objects = (
                display_full_objects
                if display_full_objects is not None
                else config.DISPLAY_FULL_OBJECTS
            )
            column_width = None
            columns = None
            if select_cols:
                columns = sorted(
                    list(
                        set(select_cols).intersection(dataclass.table_header())
                    )
                )

            if terse:
                column_width = config.TERSE_COL_WIDTH
                if not select_cols:
                    # ! Does NOT dynamically adjust number of columns based on data, only based on terminal width
                    console_width = shutil.get_terminal_size().columns
                    terse_col_count_max = console_width // column_width
                    columns = dataclass.table_header()[:terse_col_count_max]
            data_as_table = self._tabulate_planned_changes(
                dataclass,
                columns or dataclass.table_header(),
                column_width,
                display_full_objects,
            )
            if data_as_table:
                tabulated_results.append(
                    f'## {dataclass.__name__} Changes' + '\n\n' + data_as_table
                )
        return '\n\n\n'.join(tabulated_results)

    def dry_run(self, terse=None) -> str:
        """Show a 'dry run' of all planned changes to be made (but don't actually make the changes).

        Args:
            terse (bool, optional): Whether to truncate each line according to your terminal width. Defaults to config.TERSE."""
        terse = terse if terse is not None else config.TERSE
        return self.dry_run_of_actions(self._actions, one_line=terse)

    @staticmethod
    def dry_run_of_actions(
        actions, one_line=True, completed=False, empty_message='None, yet...'
    ) -> str:
        """Return a 'dry run' of some 'actions'.

        Args:
            actions: The actions to be included in the dry run.
            one_line (bool, optional): Whether to truncate each line according to your terminal width. Defaults to True.
            completed (bool, optional): Whether to show actions as 'COMPLETED'. Defaults to False.

        Returns:
            str: Each planned action, printed in a nicely enumerated list.
        """
        if not actions:
            return empty_message
        indentation = utils.calculate_list_indent(actions)
        max_chars = None
        if one_line:
            terminal_width = shutil.get_terminal_size().columns
            max_chars = terminal_width - indentation - len('. ')
        dry_run_actions = list()
        for count, action in enumerate(actions):
            msg = action.generate_log_for_action(max_chars, completed)
            dry_run_actions.append(f'{count+1:{indentation}d}. {msg}')
        return '\n'.join(dry_run_actions)

    def _tabulate_planned_changes(
        self,
        dataclass: CSVDataclass,
        selected_columns,
        maxcolwidths=None,
        display_full_objects=None,
    ):
        display_full_objects = (
            display_full_objects
            if display_full_objects is not None
            else config.DISPLAY_FULL_OBJECTS
        )
        table_data = self.with_data_type(dataclass)
        if not table_data:
            return

        rows = [
            row.as_table_row(
                selected_columns, display_full_objects=display_full_objects
            )
            for row in table_data.as_list()
        ]
        return tabulate(
            rows,
            ['action'] + selected_columns,
            # table_data[0].table_header()[:len(['action'] + selected_columns)],
            maxcolwidths=maxcolwidths,
        )

    def save_changes(self, netdot_repo: 'netdot.Repository'):
        """Save the changes back to Netdot.

        Args:
            netdot_repo (netdot.Repository): The repository to use when saving changes.
        """
        if netdot_repo._dry_run:
            raise RuntimeError(
                'Repository cannot be in dry run mode. Use disable_propose_changes() or build a new Repository with (dry_run=False).'
            )
        save_functions = {
            actions.ActionTypes.UPDATE: lambda action: netdot_repo.update(
                action.new_data,
            ),
            actions.ActionTypes.CREATE: lambda action: netdot_repo.create_new(
                action.new_data
            ),
            actions.ActionTypes.DELETE: lambda action: netdot_repo.delete(
                action.old_data, confirm=False, ignore_404=False
            ),
        }

        def save_change(action: 'actions.NetdotAction', one_line=True):
            max_chars = None
            if one_line:
                max_chars = shutil.get_terminal_size().columns
            save_function = save_functions[action.action_type]
            logger.info(action.generate_log_for_action(truncate=max_chars))
            result = save_function(action)
            logger.info(
                action.generate_log_for_action(truncate=max_chars, completed=True)
            )
            return result

        if self._lock.acquire(blocking=False):
            try:
                for action in tqdm(list(self._actions)):
                    # Remove action before performing it.
                    # ! Why? Ensure that action will not be performed twice.
                    self._actions.remove(action)
                    self._action_in_progress = action
                    response = save_change(action)
                    self._action_in_progress = None
                    self._completed_actions.append(action)
                    self._responses.append(response)
            except Exception as e:
                self._failed_actions.append(self._action_in_progress)
                self._failed_actions_exceptions.append(e)
                logger.exception(
                    f"""Failed to save changes to Netdot. Summary: {len(self._completed_actions)} completed actions, {len(self._actions)+1} remaining actions, including failed action: {self._action_in_progress}
To learn more, use the 'status_report()' method.
"""
                )
                raise e
            finally:
                self._lock.release()
        else:
            raise RuntimeError('Unable to acquire lock for save_changes()')
