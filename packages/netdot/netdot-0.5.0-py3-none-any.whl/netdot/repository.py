import logging
import textwrap
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import AbstractContextManager
from getpass import getpass
from typing import Callable, ClassVar, Dict, List, Union

import uologging

import netdot.dataclasses
from netdot.actions import ActionTypes
from netdot.dataclasses.base import NetdotAPIDataclass
from netdot.unitofwork import UnitOfWork

from . import client, config, exceptions, utils

logger = logging.getLogger(__name__)
trace = uologging.trace(logger)


class Repository(AbstractContextManager):
    _initialized: ClassVar[bool] = False
    _existing_connection: ClassVar = None

    #
    #
    # __Dunder__ methods
    #
    #
    def __exit__(self):  # pragma: no cover
        self.disconnect()

    def __str__(self):
        return f"Repository('{self.connection.netdot_url}', '{self.user}')"

    #
    #
    # Public API
    #
    #
    def __init__(
        self,
        netdot_url,
        user,
        password,
        dry_run=True,
        auto_update=True,
        print_changes=False,
        threads=None,
        trace_downloads=None,
        trace_threshold_bytes=None,
        **kwargs,
    ):
        """Work with Netdot API using Python objects.

        Args:
            netdot_url (str): The URL of the Netdot server, e.g. "https://nsdb.uoregon.edu"
            user (str): The Netdot username to use for authentication.
            password (str): The Netdot password to use for authentication.
            dry_run (bool, optional): Only **'propose changes'** until user calls `save_changes`. Defaults to True.
            print_changes (bool, optional): (When dry_run=True) Print any 'proposed changes' as they occur. Defaults to False.
            auto_update (bool, optional): (When dry_run=True) Automatically 'propose changes' on Netdot objects. Defaults to True. (If an attribute is updated on any Netdot object, that update will be immediately reflected in this repository's 'proposed changes')
            threads (int, optional): How many threads can be used when making GET requests? Defaults to config.THREADS.
        """
        threads = threads or config.THREADS
        trace_downloads = trace_downloads if trace_downloads is not None else config.TRACE_DOWNLOADS
        trace_threshold_bytes = trace_threshold_bytes or config.TRACE_THRESHOLD
        Repository._prepare_class()
        self.netdot_url = netdot_url
        self.user = user
        self._connection = client.Client(
            netdot_url,
            user,
            utils.HiddenString(password),
            trace_downloads=trace_downloads,
            trace_threshold_bytes=trace_threshold_bytes,
            **kwargs,
        )
        self._thread_count = threads
        self._dry_run = dry_run
        self._auto_update_on_dry_run = auto_update
        self._print_dry_run_changes = print_changes
        self.proposed_changes = UnitOfWork()
        self._lock = threading.Lock()
        # Indexes
        self._products_indexed_by_name: Dict[str, netdot.Product] = None

    @classmethod
    def connect(
        cls, _input=input, _getpass=getpass, propose_changes=True, **kwargs
    ):  # pragma: no cover
        """Connect to NetDot for interactive use.

        Args:
            propose_changes: Enable the 'propose changes' or DRY RUN features on this Netdot Repository. Defaults to True.

        Example:
        This method is interactive, and requires you to provide your credentials
             >> repo = Repository.connect()
            What is the URL of the NetDot server? [https://nsdb.uoregon.edu]: ('enter' to use default)
            NetDot username: netdot_user
            NetDot password: (uses getpass module, to securely collect your password)

        With `repo`, you can now retrieve data and better understand the capabilities of this API.
        As an example, you may retrieve ipblock information about a particular IP address.

             >> repo.get_ipblock_by_address('10.0.0.0')
            [IPBlock(id=5065, address=IPv4Address('10.0.0.0'), description='RFC1918 Addresses', ... omitted for brevity...

        Returns:
            netdot.Repository: A repository. Use `help(netdot.Repository)` to learn more.
        """
        # Offer to return an existing connection that has been established before
        if cls._existing_connection:
            use_existing_connection = _input(
                textwrap.dedent(
                    f"""
                Noticed an existing connection:
                    {cls._existing_connection}

                Would you like to retrieve it instead of setting up a new connection?
                Reply 'yes', or 'no' [yes]: """
                )
            )
            if not use_existing_connection.lower().startswith('n'):
                return cls._existing_connection
        if propose_changes:
            # Enable dry_run and each of its sub-settings when propose_changes=True
            kwargs['dry_run'] = True
            kwargs['auto_update'] = True
            kwargs['print_changes'] = True
        connection = cls._connect(_input, _getpass, **kwargs)
        cls._existing_connection = connection
        if propose_changes:
            msg = """
                NOTICE: Proposing changes (this is a DRY RUN).


                Call `save_changes` to actually create, update, and delete NetDot data.

                How do I use this feature?
                1. Retrieve data using `get_*` methods (and `load_*` methods on those objects).
                2. Update the objects you retrieved directly in code, then either:
                   a) call `create_or_update`, `add_*`, or `delete` directly the object, or
                   b) call `update`, create_new`, or `delete`  on this repository.
                3. [Optional] Call `show_changes` to review what changes have been proposed.
                4. Call `save_changes` to actually create, update, and delete NetDot data!

                > Call `disable_propose_changes` anytime to disable this feature and directly modify NetDot.
                >
                > Alternately, use `connect(propose_changes=False)`.
                """
            print(textwrap.dedent(msg))
        return connection

    def disconnect(self):  # pragma: no cover
        """Disconnect from Netdot."""
        self.connection.logout()

    def create_new(self, new_data: NetdotAPIDataclass) -> NetdotAPIDataclass:
        """Create some new object in Netdot.

        > NOTE: Upon creation, the `id` field of new_data will be populated.

        Args:
            new_data (netdot.NetdotAPIDataclass): The new data to use for the new Netdot object.

        Returns:
            netdot.NetdotAPIDataclass: The new object (with `id` populated).

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: if the object cannot be created for any reason. (error details can be found in Netdot's apache server logs)
            As an example, expect a generic HTTP 400 when:
              * an object breaks 'uniqueness' rules (Ex. 2 Sites named "Test"),
              * an object is missing required fields (Ex. a Person without a `lastname`),
              * an object is improperly formatted (Ex. a Device with a `date_installed` that is not a datetime),
        """
        if self._dry_run:
            self.proposed_changes.create(
                new_data, print_changes=self._print_dry_run_changes
            )
            return new_data.with_repository(self)
        response = self.connection.create_object(
            new_data.__class__.__name__, new_data.to_DTO()
        )
        return new_data._intake_DTO(response).with_repository(self)

    def update(self, new_data: NetdotAPIDataclass) -> NetdotAPIDataclass:
        """Update an existing object in Netdot.

        Args:
            id (int): The ID of the object to update.
            new_data (netdot.NetdotAPIDataclass): The new data to use when updating the object.

        Returns:
            netdot.NetdotAPIDataclass: The object provided by Netdot in response to this HTTP POST.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: if the object cannot be updated for some reason. (error details can be found in Netdot's apache server logs)
        """
        if self._dry_run:
            getter_function = getattr(
                self, f'get_{new_data._pep8_method_friendly_name()}'
            )
            old_data = getter_function(new_data.id)
            self.proposed_changes.update(
                old_data, new_data, print_changes=self._print_dry_run_changes
            )
            return new_data.with_repository(self)
        return self._update_by_id(new_data.id, new_data).with_repository(self)

    def delete(
        self,
        data: NetdotAPIDataclass,
        confirm=True,
        ignore_404=True,
    ):
        """Delete an existing object from Netdot.

        > ⚠ WARNING: This is irreversible. Use with caution.

        Args:
            data (NetdotAPIDataclass): The object to be deleted.
            confirm (bool): Assume interactive and ask user 'Proceed? ...' before deleting. Default True.
            ignore_404 (bool): Default True. Ignore HTTP 404 errors. (Why? no need to delete an object if it doesn't exist!)

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: Could occur for various reasons. (error details can be found in Netdot's apache server logs)
            NetdotDeleteError: If the object cannot be deleted for some other reason.
            TypeError: If data is not a subclass of NetdotAPIDataclass.
        """
        if self._dry_run:
            self.proposed_changes.delete(
                data, print_changes=self._print_dry_run_changes
            )
            return
        if confirm:  # pragma: no cover (manually tested on Oct 30, 2023)
            if not utils.user_confirmation('Deleting is irreversible. Proceed?'):
                print(
                    'Nothing done. Type "yes" to proceed next time (or use confirm=False)'
                )
                return

        id = data.id
        try:
            self.connection.delete_object_by_id(data.__class__.__name__, id)
        except exceptions.HTTPError as e:
            if (
                ignore_404
                and hasattr(e.response, 'status_code')
                and e.response.status_code == 404
            ):
                return
            raise exceptions.NetdotDeleteError(
                f'Unable to delete {data.__class__.__name__} with id {id}',
                status_code=e.response.status_code,
                response=e.response.content,
            )

    #
    #
    # Netdot "Infer from Index" methods
    #
    #
    def infer_product(self, device_asset_id: str) -> 'netdot.dataclasses.Product':
        """Infer the Product of some device, based on its `asset_id` string returned from Netdot REST API.

        > NOTE: One HTTP Request is made to retrieve all Products from Netdot.
        > All subsequent calls to this method will use the cached results.

        Args:
            device_asset_id (str): The "asset_id" string returned from Netdot.

        Returns:
            netdot.dataclasses.Product: The Product associated to this Device.

        Raises:
            NetdotError: If no Product can be inferred from the provided asset_id string.
        """
        if not self._products_indexed_by_name:
            self.reload_product_index()
        conjoined_tokens = device_asset_id.split(',')
        asset_tokens = list()
        for token in conjoined_tokens:
            asset_tokens.extend(token.split(' '))
        for token in asset_tokens:
            if token in self._products_indexed_by_name:
                return self._products_indexed_by_name[token]
        raise exceptions.NetdotError(
            f'Unable to infer product from asset string "{device_asset_id}" given products: {self._products_indexed_by_name.keys()}'
        )

    #
    #
    # Indexing Helper methods
    #
    # (These methods are used to speed up lookups by indexing data from Netdot)
    #
    def reload_product_index(self):
        """Reload all Products from Netdot, and index them by name."""
        products = self.get_products_where('all')
        self._products_indexed_by_name = {product.name: product for product in products}

    #
    #
    # Netdot "Getter" methods
    #
    #
    def get_ipblock_children(self, id: int, **url_params) -> List['netdot.IPBlock']:
        """Get the children of some parent IPBlock.

        Args:
            id (int): The ID of the parent IPBlock.

        Returns:
            List[netdot.IPBlock]: The children IPBlocks

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: If no such IPBlocks are found. (error details can be found in Netdot's apache server logs)
        """
        data = self.connection.get_objects_by_filter(
            netdot.IPBlock._table_name(),
            'parent',
            str(id),
            **url_params,
        )
        return [
            netdot.IPBlock.from_DTO(ipblock).with_repository(self) for ipblock in data
        ]

    def get_hosts(self, **url_params) -> 'netdot.Host':
        """Retrieve relevant RR (DNS) objects Hosts from Netdot.

        Args:
            **url_params: URL parameters to filter the results. See examples below.

        Returns:
            netdot.Host: A collection of DNS Resource Records and related IP Blocks.

        Examples:
            >> repo.get_hosts(zone='uoregon.edu')
            >> repo.get_hosts(name='myhost')
            >> repo.get_hosts(rrid=1234)
            >> repo.get_hosts(subnet='10.1.1.1/24')
        """
        data = self.connection.get('/host', **url_params)
        return netdot.Host.from_DTO(data)

    def get_host_by_name(self, hostname: str) -> 'netdot.Host':
        """Retrieve DNS Resource Records with name "hostname", and related IP Block records.

        NOTE: This is part of, "The special resource '/rest/host' provides a simplified interface for manipulating DNS and DHCP records."

        Args:
            hostname (str): The hostname to lookup, e.g. "myhost.example.com"
        Returns:
            netdot.Host: A collection of DNS Resource Records and related IP Blocks for the given hostname.
        """
        return self.get_hosts(name=hostname)

    def get_hosts_by_subnet(self, subnet: str) -> 'netdot.Host':
        """Retrieve all Hosts (DNS Resource Records) within a given subnet.

        NOTE: This is part of "The special resource '/rest/host' provides a simplified interface for manipulating DNS and DHCP records."

        Args:
            subnet (str): The subnet to lookup, e.g. "10.1.1.1/24"

        Returns:
            List[netdot.Host]: A list of Hosts (DNS Resource Records) within the given subnet.
        """
        return self.get_hosts(subnet=subnet)

    def create_host(self, subnet: str, hostname: str) -> 'netdot.RR':
        """Create new A record named 'hostname' using next available address in given 'subnet'

        NOTE: This function does not work when this Repository is in `dry_run` mode.
        NOTE: A subsequent call to `get_host_by_name` is needed to retrieve the created IP Address.
        NOTE: This is part of "The special resource '/rest/host' provides a simplified interface for manipulating DNS and DHCP records."

        Args:
            subnet (str): The subnet to create the host in.
            hostname (str): The hostname for the new host.

        Returns:
            netdot.RR: The DNS Resource Record (RR) object that was created for the new host.

        Example:
                >> repo.create_host('10.0.0.1/24', 'tinker.example.com')
                RR(id=1234, name='tinker', zone='example.com', type='A', ...)

            To get the create IP Address, you'll need to lookup the host again:

                >> repo.get_host_by_name('tinker.example.com')
                >> repo.addresses
                ['10.0.0.123']
        """
        if self._dry_run:
            raise exceptions.NetdotError(
                "create_host does not support dry_run mode. Disable dry_run to use this method."
            )
        else:
            data = self.connection.post(
                '/host',
                {
                    'subnet': subnet,
                    'name': hostname
                },
            )
            return netdot.RR.from_DTO(data)

    def get_physaddr_by_MACAddress(self, address: str) -> 'netdot.PhysAddr':
        """Get some Physical Address from Netdot Address Space.

        Args:
            address (str): The MAC Address to lookup, e.g. "00:00:00:00:00:00"

        Returns:
            netdot.PhysAddr: The Physical Address object that matched the provided address, or None.
        """
        return self._get_entity_by_address(address, netdot.PhysAddr)

    def find_edge_port(self, mac_address: str) -> 'netdot.Interface':
        """Get the Edge Port (Interface) associated to some MAC Address.

        > NOTE: This will make `N+M` HTTP Requests (where N ).

        The idea is to get all device ports whose latest forwarding tables included this address.
        If we get more than one, select the one whose forwarding table had the least entries.

        Args:
            mac_address (str): A MAC Address to lookup.

        Returns:
            netdot.Interface: The edge port associated to the provided MAC Address.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: If the MAC Address cannot be found, or if any subsequent HTTP requests fail. (error details can be found in Netdot's apache server logs)
        """
        physaddr = self.get_physaddr_by_MACAddress(mac_address)
        entries = self.get_fwtableentries_by_physaddr(physaddr)
        if len(entries) == 1:
            return entries[0].load_interface()
        elif len(entries) == 0:  # pragma: no cover
            # Defensive programming: HTTPError will be raised before this could occur.
            return
        timestamps = [entry.infer_timestamp() for entry in entries]
        most_recent_scan_time = max(timestamps)
        most_recent_entries = list(
            filter(
                lambda entry: entry.infer_timestamp() == most_recent_scan_time, entries
            )
        )

        # TODO can we omit the calls to get_fwtableentries_by_interface? Perhaps the "entries" already loaded is sufficient to lookup interface_counts.
        def get_related_fwtableentries(entry: netdot.FWTableEntry):
            interface = entry.load_interface()
            return self.get_fwtableentries_by_interface(
                interface, fwtable=entry.fwtable_xlink
            )

        with self._create_thread_pool() as executor:
            related_fwtableentries = executor.map(
                get_related_fwtableentries, most_recent_entries
            )
            least_fwtableentries = min(related_fwtableentries, key=len)
            most_recent_entry = max(least_fwtableentries, key=id)
            return most_recent_entry.load_interface()

    def get_rr_by_address(self, address: str) -> 'netdot.RR':
        """Get a Resource Record from Netdot Address Space, by IP Address.

        Args:
            address (str): The IP Address to lookup, e.g. "10.0.0.123"

        Returns:
            netdot.RR: The Resource Record that matched the provided address.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: If the Resource Record cannot be found. (error details can be found in Netdot's apache server logs)
        """
        ipblock = self.get_ipblock_by_address(address)
        rraddr = self._get_unique_by_filter(netdot.RRADDR, 'ipblock', ipblock.id)
        return self.get_rr(rraddr.rr_xlink)

    def get_ipblock_by_address(self, address: str) -> 'netdot.IPBlock':
        """Get some IP Block from Netdot Address Space.

        Args:
            address (str): The IP Address to lookup, e.g. "10.0.0.0"

        Returns:
            IPBlock: The IPBlock object that matched the provided address, or None.
        """
        return self._get_entity_by_address(address, netdot.IPBlock)

    #
    #
    # "Proposed Changes" (UnitOfWork) methods
    #
    #
    def save_changes(self, confirm=True):
        """Save all proposed changes to Netdot.

        Args:
            confirm (bool, optional): If any delete actions are planned, confirm them with the user first. Defaults to True.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: For any HTTP errors. (error details can be found in Netdot's apache server logs)
            RuntimeError: If this Repository's multithreading lock cannot be acquired.
        """
        proposed_deletions = self.proposed_changes.with_action_types(
            [ActionTypes.DELETE]
        )
        if (
            proposed_deletions and confirm
        ):  # pragma: no cover (manually tested on Oct 30, 2023)
            print(proposed_deletions.dry_run())
            if not utils.user_confirmation('Deleting is irreversible. Proceed?'):
                print(
                    'Nothing done. Review changes using `show_changes` Type "yes" to proceed next time (or use confirm=False)'
                )
                return

        if self._lock.acquire(blocking=False):
            try:
                prior_dry_run_state = self._dry_run
                self._dry_run = False
                if len(self.proposed_changes.as_list()) == 0:
                    print('No changes need to be saved.')
                else:
                    self.proposed_changes.save_changes(self)
                    print('Changes saved!')
            except Exception:
                if config.SAVE_AS_FILE_ON_ERROR:
                    try:
                        # Save proposed changes to file for recovery
                        self.proposed_changes.save_as_pickle(
                            config.ERROR_PICKLE_FILENAME
                        )
                        logger.exception(
                            f'Saved proposed changes to file "{config.ERROR_PICKLE_FILENAME}" for recovery.'
                        )
                    except Exception:
                        logger.exception(
                            f'Unable to save changes to file "{config.ERROR_PICKLE_FILENAME}"'
                        )
                raise exceptions.NetdotError(
                    f"""Unable to complete changes.
Failed to: {self.proposed_changes.failed_action_msg()}."""
                )
            finally:
                self._dry_run = prior_dry_run_state
                self._lock.release()
        else:
            raise RuntimeError(
                'Unable to acquire lock for save_changes(). Is another thread using this repository at this moment?'
            )

    def clear_proposed_changes(self):
        """Reset the proposed changes (dry run) for this Netdot Repository."""
        self.proposed_changes = UnitOfWork()

    def disable_propose_changes(self):
        """Disable the 'propose changes' or DRY RUN feature on this Netdot Repository.

        After this, all changes will be applied immediately to Netdot.
        """
        self._dry_run = False

    def enable_propose_changes(self, print_changes=True, auto_update=True):
        """Enable the 'propose changes' or DRY RUN feature on this Netdot Repository.

        After this, all changes will be queued, only to be applied when `save_changes` is called.
        """
        self._dry_run = True
        self._print_dry_run_changes = print_changes
        self._auto_update_on_dry_run = auto_update

    #
    #
    # UnitOfWork wrapper methods
    #
    #
    def show_all_changes(self, terse=None):
        # See UnitOfWork.status_report for more details
        terse = terse if terse is not None else config.TERSE
        print(self.proposed_changes.status_report(terse))

    show_all_changes.__doc__ = UnitOfWork.status_report.__doc__

    def show_failed_changes(self):
        # See UnitOfWork.failed_actions_msgs for more details
        print(self.proposed_changes.failed_actions_msgs())

    show_failed_changes.__doc__ = UnitOfWork.failed_actions_msgs.__doc__

    def show_changes(self, terse=None):  # pragma: no cover  (wrapper method)
        # See UnitOfWork.dry_run for more details
        terse = terse if terse is not None else config.TERSE
        print(self.proposed_changes.dry_run(terse))

    show_changes.__doc__ = UnitOfWork.dry_run.__doc__

    def show_changes_as_tables(self, terse=None, select_cols=None):
        # See UnitOfWork.changes_as_tables for more details
        terse = terse if terse is not None else config.TERSE
        print(self.proposed_changes.changes_as_tables(terse, select_cols))

    show_changes_as_tables.__doc__ = UnitOfWork.changes_as_tables.__doc__

    #
    #
    # Client wrapper methods
    #
    #
    def enable_trace_downloads(self, threshold_bytes: int = None):
        # See client.Client.enable_trace_downloads for more details
        self.connection.enable_trace_downloads(threshold_bytes or config.TRACE_THRESHOLD)

    enable_trace_downloads.__doc__ = client.Client.enable_trace_downloads.__doc__

    def disable_trace_downloads(self):
        # See client.Client.disable_trace_downloads for more details
        self.connection.disable_trace_downloads()

    disable_trace_downloads.__doc__ = client.Client.disable_trace_downloads.__doc__

    #
    #
    # Helper methods
    #
    #
    def _create_thread_pool(self):
        return ThreadPoolExecutor(self._thread_count)

    def _update_by_id(
        self, id: int, new_data: NetdotAPIDataclass
    ) -> NetdotAPIDataclass:
        """Update an existing object in Netdot.

        Args:
            id (int): The ID of the object to update.
            new_data (netdot.NetdotAPIDataclass): The new data to use when updating the object.

        Returns:
            netdot.NetdotAPIDataclass: The object provided by Netdot in response to this HTTP POST.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: if the object cannot be updated for some reason. (error details can be found in Netdot's apache server logs)
        """
        obj_url_path = f'/{new_data.__class__.__name__}/{id}'
        response = self.connection.post(obj_url_path, new_data.to_DTO())
        return new_data._intake_DTO(response)

    @classmethod
    def _attach_methods(cls, methods):
        for method in methods:
            setattr(cls, method.__name__, method)

    @classmethod
    def _prepare_class(cls):
        if not cls._initialized:
            netdot.initialize()
            dataclasses = netdot.NetdotAPIDataclass.__subclasses__()
            cls._attach_methods(_generate_CRUD_for_all_dataclasses(dataclasses))
            cls._initialized = True

    @classmethod
    def _connect(cls, _input=input, _getpass=getpass, **kwargs):  # pragma: no cover
        netdot_url = (
            _input(f'What is the URL of the NetDot server? [{config.SERVER_URL}]: ')
            or config.SERVER_URL
        )
        user = _input('NetDot username: ')
        password = utils.HiddenString(_getpass('NetDot password: '))
        return cls(netdot_url, user, password, **kwargs)

    @property
    def connection(self) -> 'client.Client':
        if not self._connection:
            raise exceptions.NetdotError(
                'Must establish a connection before using this repository.'
            )
        return self._connection

    #
    #
    # Helper methods
    #
    #
    def _get_entity_by_address(self, address: str, cls, **url_params):
        return self._get_unique_by_filter(cls, 'address', address, **url_params)

    def _get_unique_by_filter(
        self, cls: NetdotAPIDataclass, search_field: str, search_term: str, **url_params
    ) -> NetdotAPIDataclass:
        """Try to retrieve a SINGLE object from netdot.

        Logs a WARNING to the console if multiple objects from netdot match this search.

        Args:
            cls (NetdotAPIDataclass): The type of object to retrieve.
            search_field (str): Which field of 'cls' should we be filtering by?
            search_term (str): The unique search term.

        Returns:
            NetdotAPIDataclass: The parsed object that matches the provided search_field and search_term.
        """
        data = self.connection.get_objects_by_filter(
            cls._table_name(), search_field, search_term, **url_params
        )
        matching_entities = [
            cls.from_DTO(entity_data).with_repository(self) for entity_data in data
        ]
        if len(matching_entities) > 1:
            logger.warning(
                f'Found more than one matching address for {search_term} ({cls.__name__}): {matching_entities}'
            )
        elif len(matching_entities) < 1:
            return None
        return matching_entities[0]


#
# Functions for 'Generating and attaching methods'
#
def _generate_CRUD_for_all_dataclasses(dataclasses) -> List:
    """Generate the 'CRUD' operations for this repository for all Netdot dataclasses."""
    CRUD_methods = []
    for dataclass in dataclasses:
        CRUD_methods.extend(_generate_getters_for_dataclass(dataclass))
    return CRUD_methods


def _generate_getters_for_dataclass(dataclass: NetdotAPIDataclass) -> List:
    methods_for_dataclass = _generate_xlink_getters(dataclass) + [
        _generate_all_getter(dataclass),
        _generate_by_id_getter(dataclass),
    ]
    return methods_for_dataclass


def _generate_by_id_getter(dataclass: NetdotAPIDataclass):
    #
    #
    # Generate a custom `get_by_id` method for dataclass
    #
    #
    def get_by_id(self, id: int) -> dataclass:
        data = self.connection.get_object_by_id(dataclass._table_name(), str(id))
        return dataclass.from_DTO(data).with_repository(self)

    get_by_id.__doc__ = f"""Get info about a {dataclass.__name__} from Netdot.

    Args:
        id (int): The ID of the {dataclass.__name__} to retrieve.

    Returns:
        netdot.{dataclass.__name__}: The {dataclass.__name__} with `id`. (raises ValueError if `id` is not found)

    Raises:
        ValueError: if the {dataclass.__name__} cannot be retrieved for some reason.
        NetdotError: if some internal error happens (in this Python Netdot API wrapper, or on the Netdot Server itself).
        """
    get_by_id.__name__ = f'get_{dataclass._pep8_method_friendly_name()}'
    return get_by_id


def _generate_all_getter(dataclass) -> Callable:
    get_all_function_name = f'get_{dataclass._name_pluralized().lower()}_where'

    def get_all(self, *args, **url_params) -> List[dataclass]:
        if args:
            if len(args) == 1 and args[0].lower() == 'all':
                pass
            else:
                raise ValueError(
                    f'{get_all_function_name} only accepts keyword arguments (or the special positional argument "all")'
                )
        data_list = self.connection.get_all(dataclass._table_name(), **url_params)
        return [dataclass.from_DTO(data).with_repository(self) for data in data_list]

    get_all.__doc__ = f"""Get info about {dataclass._name_pluralized()} from Netdot.

    > NOTE: This will return ALL {dataclass._name_pluralized()} from Netdot if no kwargs (URL Parameters) are provided.
    > You can provide the special positional argument "all" if you like (for semantic clarity in your scripts).

    Args:
        **kwargs: URL Parameters - Any keyword args will be used as URL Parameters. Ex. (id=1) will be translated to `?id=1` in the URL.

    Returns:
        List[netdot.{dataclass.__name__}]: {dataclass._name_pluralized()} from Netdot (that match provided URL Parameters).

    Raises:
        ProtocolError: Can occur if your connection with Netdot has any issues.
        HTTPError: For any HTTP errors (including HTTP 404 if no matches are found). (error details can be found in Netdot's apache server logs)
        NetdotError: if some internal error happens (in this Python Netdot API wrapper, or on the Netdot Server itself).
        """
    get_all.__name__ = get_all_function_name
    return get_all


def _generate_xlink_by_id_getter(dataclass, xlink, xlink_class):
    def xlink_by_id_getter(self, other: Union[int, NetdotAPIDataclass], **url_params):
        if isinstance(other, NetdotAPIDataclass):
            other = other.id
        data_list = self.connection.get_objects_by_filter(
            dataclass._table_name(),
            xlink.replace('_xlink', ''),
            other,
            **url_params,
        )
        return [dataclass.from_DTO(data).with_repository(self) for data in data_list]

    xlink_by_id_getter.__doc__ = f"""Get the list of {dataclass._name_pluralized()} associated to a particular {xlink_class.__name__}.

    Args:
        other (int,NetdotAPIDataclass): The particular {xlink_class.__name__} or its `id`.

    Returns:
        List[netdot.{dataclass.__name__}]: The list of {dataclass._name_pluralized()} associated to the {xlink_class.__name__}.
        """
    xlink_by_id_getter.__name__ = (
        f"get_{dataclass._name_pluralized().lower()}_by_{xlink.replace('_xlink','')}"
    )

    return xlink_by_id_getter


def _generate_xlink_getters(my_cls) -> List:
    """Generate custom `get_A[s]_by_B` methods for dataclass, based on its foreign_key_field_names."""
    xlink_getters = []

    for xlink, other_cls in my_cls._related_classes().items():
        xlink_by_id_getter = _generate_xlink_by_id_getter(my_cls, xlink, other_cls)
        xlink_getters.append(xlink_by_id_getter)

    return xlink_getters
