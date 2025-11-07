import logging
from dataclasses import dataclass
from typing import Union

import netdot
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass

logger = logging.getLogger(__name__)


@dataclass
class ContactList(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None


@dataclass
class ContactType(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None


@dataclass
class AccessRight(NetdotAPIDataclass, CSVDataclass):

    access: str = None
    object_class: str = None
    object_id: int = None


@dataclass
class GroupRight(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_ASSOCIATIVE_TABLE = True

    accessright: Union[str,'netdot.AccessRight'] = None
    accessright_xlink: int = None
    contactlist: Union[str,'netdot.ContactList'] = None
    contactlist_xlink: int = None


@dataclass
class Audit(NetdotAPIDataclass, CSVDataclass):

    fields: str = None
    label: str = None
    object_id: int = None
    operation: str = None
    tablename: str = None
    tstamp: parse.DateTime = None
    username: str = None
    vals: str = None


@dataclass
class UserType(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None


@dataclass
class Person(NetdotAPIDataclass, CSVDataclass):
    _xlink_class_map = {
        "location": "Site",
        "user_type": "UserType",
    }

    aliases: str = None
    cell: str = None
    email: str = None
    emailpager: str = None
    entity: Union[str,'netdot.Entity'] = None
    entity_xlink: int = None
    extension: int = None
    fax: str = None
    firstname: str = None
    home: str = None
    info: str = None
    lastname: str = None
    location: Union[str,'netdot.Site'] = None
    location_xlink: int = None
    office: str = None
    pager: str = None
    position: str = None
    room: Union[str,'netdot.Room'] = None
    room_xlink: int = None
    user_type: Union[str,'netdot.UserType'] = None
    user_type_xlink: int = None
    username: str = None
    password: str = None  # TODO Should we use HiddenString?


@dataclass
class Contact(NetdotAPIDataclass, CSVDataclass):
    _xlink_class_map = {
        "notify_pager": "Availability",
        "notify_email": "Availability",
        "notify_voice": "Availability",
    }
    contactlist: Union[str,'netdot.ContactList'] = None
    contactlist_xlink: int = None
    contacttype: Union[str,'netdot.ContactType'] = None
    contacttype_xlink: int = None
    escalation_level: int = None
    info: str = None
    notify_email: Union[str,'netdot.Availability'] = None
    notify_email_xlink: int = None
    notify_pager: Union[str,'netdot.Availability'] = None
    notify_pager_xlink: int = None
    notify_voice: Union[str,'netdot.Availability'] = None
    notify_voice_xlink: int = None
    person: Union[str,'netdot.Person'] = None
    person_xlink: int = None


@dataclass
class UserRight(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_ASSOCIATIVE_TABLE = True

    accessright: Union[str,'netdot.AccessRight'] = None
    accessright_xlink: int = None
    person: Union[str,'netdot.Person'] = None
    person_xlink: int = None
