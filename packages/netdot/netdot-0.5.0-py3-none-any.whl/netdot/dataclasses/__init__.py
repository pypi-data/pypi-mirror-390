from .arpcache import ArpCache, ArpCacheEntry
from .asset import Asset
from .base import NetdotAPIDataclass
from .bgp import ASN, BGPPeering
from .cables import (
    BackboneCable,
    CableStrand,
    CableType,
    Circuit,
    CircuitStatus,
    CircuitType,
    FiberType,
    HorizontalCable,
    Splice,
    StrandStatus,
)
from .device import (
    OUI,
    Device,
    DeviceAttr,
    DeviceAttrName,
    DeviceContacts,
    DeviceModule,
    STPInstance,
)
from .dhcp import (
    DHCPAttr,
    DHCPAttrName,
    DHCPScope,
    DHCPScopeType,
    DHCPScopeUse,
)
from .dns import (
    RR,
    RRADDR,
    RRCNAME,
    RRDS,
    RRHINFO,
    RRLOC,
    RRMX,
    RRNAPTR,
    RRNS,
    RRPTR,
    RRSRV,
    RRTXT,
    Zone,
    ZoneAlias,
)
from .entity import Entity, EntityRole, EntitySite, EntityType
from .fwtable import FWTable, FWTableEntry
from .host import Host
from .interface import Interface, InterfaceVLAN
from .ipblock import (
    IPBlock,
    IPBlockAttr,
    IPBlockAttrName,
    IPBlockStatus,
    IPService,
    Service,
    SubnetZone,
)
from .misc import (
    Availability,
    # DataCache,
    HostAudit,
    MaintContract,
    MonitorStatus,
    SavedQueries,
    SchemaInfo,
)
from .physaddr import PhysAddr, PhysAddrAttr, PhysAddrAttrName
from .products import Product, ProductType
from .site import (
    Closet,
    Floor,
    # ClosetPicture,
    Room,
    # FloorPicture,
    Site,
    SiteLink,
    # SitePicture,
    SiteSubnet,
)
from .users import (
    AccessRight,
    Audit,
    Contact,
    ContactList,
    ContactType,
    GroupRight,
    Person,
    UserRight,
    UserType,
)
from .vlan import VLAN, VLANGroup

_initialized = False


def initialize():
    # ? Why not do this at module-level?? B/c, that is MUCH harder to test.
    global _initialized
    if not _initialized:
        AccessRight()
        ArpCache()
        ArpCacheEntry()
        ASN()
        Asset()
        Audit()
        Availability()
        BackboneCable()
        BGPPeering()
        CableStrand()
        CableType()
        Circuit()
        CircuitStatus()
        CircuitType()
        Closet()
        # ClosetPicture()
        Contact()
        ContactList()
        ContactType()
        # DataCache()
        Device()
        DeviceAttr()
        DeviceAttrName()
        DeviceContacts()
        DeviceModule()
        DHCPAttr()
        DHCPAttrName()
        DHCPScope()
        DHCPScopeType()
        DHCPScopeUse()
        Entity()
        EntityRole()
        EntitySite()
        EntityType()
        FiberType()
        Floor()
        # FloorPicture()
        FWTable()
        FWTableEntry()
        GroupRight()
        HorizontalCable()
        HostAudit()
        Interface()
        InterfaceVLAN()
        IPBlock()
        IPBlockAttr()
        IPBlockAttrName()
        IPBlockStatus()
        IPService()
        MaintContract()
        MonitorStatus()
        OUI()
        Person()
        PhysAddr()
        PhysAddrAttr()
        PhysAddrAttrName()
        Product()
        ProductType()
        Room()
        RR()
        RRADDR()
        RRCNAME()
        RRCNAME()
        RRDS()
        RRHINFO()
        RRLOC()
        RRMX()
        RRNAPTR()
        RRNS()
        RRPTR()
        RRSRV()
        RRTXT()
        SavedQueries()
        SchemaInfo()
        Service()
        Site()
        SiteLink()
        # SitePicture()
        SiteSubnet()
        Splice()
        STPInstance()
        StrandStatus()
        SubnetZone()
        UserRight()
        UserType()
        VLAN()
        VLANGroup()
        Zone()
        ZoneAlias()
        _initialized = True


Subnet = IPBlock
IPAddr = IPBlock
IPContainer = IPBlock

__all__ = [
    "initialize",
    "NetdotAPIDataclass",
    "AccessRight",
    "ArpCache",
    "ArpCacheEntry",
    "ASN",
    "Asset",
    "Audit",
    "Availability",
    "BackboneCable",
    "BGPPeering",
    "CableStrand",
    "CableType",
    "Circuit",
    "CircuitStatus",
    "CircuitType",
    "Closet",
    # "ClosetPicture",
    "Contact",
    "ContactList",
    "ContactType",
    "DataCache",
    "Device",
    "DeviceAttr",
    "DeviceAttrName",
    "DeviceContacts",
    "DeviceModule",
    "DHCPAttr",
    "DHCPAttrName",
    "DHCPScope",
    "DHCPScopeType",
    "DHCPScopeUse",
    "Entity",
    "EntityRole",
    "EntitySite",
    "EntityType",
    "FiberType",
    "Floor",
    # "FloorPicture",
    "FWTable",
    "FWTableEntry",
    "GroupRight",
    "HorizontalCable",
    "Host",
    "HostAudit",
    "Interface",
    "InterfaceVLAN",
    "IPBlock",
    "IPBlockAttr",
    "IPBlockAttrName",
    "IPBlockStatus",
    "IPService",
    "MaintContract",
    "MonitorStatus",
    "OUI",
    "Person",
    "PhysAddr",
    "PhysAddrAttr",
    "PhysAddrAttrName",
    "Product",
    "ProductType",
    "Room",
    "RR",
    "RRADDR",
    "RRCNAME",
    "RRCNAME",
    "RRDS",
    "RRHINFO",
    "RRLOC",
    "RRMX",
    "RRNAPTR",
    "RRNS",
    "RRPTR",
    "RRSRV",
    "RRTXT",
    "SavedQueries",
    "SchemaInfo",
    "Service",
    "Site",
    "SiteLink",
    # "SitePicture",
    "SiteSubnet",
    "Splice",
    "STPInstance",
    "StrandStatus",
    "SubnetZone",
    "UserRight",
    "UserType",
    "VLAN",
    "VLANGroup",
    "Zone",
    "ZoneAlias",
]
