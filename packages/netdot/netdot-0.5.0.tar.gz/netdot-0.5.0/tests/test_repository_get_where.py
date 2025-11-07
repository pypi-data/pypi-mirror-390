'''get_*_where test case for every Netdot object type.

Also ensure that web_url works for every class!
'''
from typing import List

import netdot
import pytest
from assertpy import assert_that
from netdot.repository import Repository


@pytest.mark.vcr
def test_get_AccessRights_where(repository: Repository):
    # Act
    access_rights: List[netdot.AccessRight] = repository.get_accessrights_where(
        id=1
    )

    # Assert
    assert_that(access_rights).is_length(1)
    response = repository.connection.http.get(access_rights[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_ASNs_where(repository: Repository):
    # Act
    asns: List[netdot.ASN] = repository.get_asns_where(id=1)

    # Assert
    assert_that(asns).is_length(1)
    response = repository.connection.http.get(asns[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Assets_where(repository: Repository):
    # Act
    assets: List[netdot.Asset] = repository.get_assets_where(id=45)

    # Assert
    assert_that(assets).is_length(1)
    response = repository.connection.http.get(assets[0].web_url)
    response.raise_for_status()

@pytest.mark.vcr
def test_get_Audits_where(repository: Repository):
    # Act
    audits: List[netdot.Audit] = repository.get_audits_where(id=42678005)

    # Assert
    assert_that(audits).is_length(1)
    response = repository.connection.http.get(audits[0].web_url)
    response.raise_for_status()

@pytest.mark.vcr
def test_get_Availabilities_where(repository: Repository):
    # Act
    availabilities: List[netdot.Availability] = repository.get_availabilities_where(
        id=1
    )

    # Assert
    assert_that(availabilities).is_length(1)
    response = repository.connection.http.get(availabilities[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_BackboneCables_where(repository: Repository):
    # Act
    backbone_cables: List[
        netdot.BackboneCable
    ] = repository.get_backbonecables_where(id=1)

    # Assert
    assert_that(backbone_cables).is_length(1)
    response = repository.connection.http.get(backbone_cables[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_BGPPeerings_where(repository: Repository):
    # Act
    bgp_peerings: List[netdot.BGPPeering] = repository.get_bgppeerings_where(id=430)

    # Assert
    assert_that(bgp_peerings).is_length(1)
    response = repository.connection.http.get(bgp_peerings[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_CableStrands_where(repository: Repository):
    # Act
    cable_strands: List[netdot.CableStrand] = repository.get_cablestrands_where(
        id=1
    )

    # Assert
    assert_that(cable_strands).is_length(1)
    response = repository.connection.http.get(cable_strands[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_CableTypes_where(repository: Repository):
    # Act
    cable_types: List[netdot.CableType] = repository.get_cabletypes_where(id=1)

    # Assert
    assert_that(cable_types).is_length(1)
    response = repository.connection.http.get(cable_types[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Circuits_where(repository: Repository):
    # Act
    circuits: List[netdot.Circuit] = repository.get_circuits_where(id=1)

    # Assert
    assert_that(circuits).is_length(1)
    response = repository.connection.http.get(circuits[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_CircuitStatuses_where(repository: Repository):
    # Act
    circuit_statuses: List[
        netdot.CircuitStatus
    ] = repository.get_circuitstatuses_where(id=1)

    # Assert
    assert_that(circuit_statuses).is_length(1)
    response = repository.connection.http.get(circuit_statuses[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_CircuitTypes_where(repository: Repository):
    # Act
    circuit_types: List[netdot.CircuitType] = repository.get_circuittypes_where(
        id=1
    )

    # Assert
    assert_that(circuit_types).is_length(1)
    response = repository.connection.http.get(circuit_types[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Closets_where(repository: Repository):
    # Act
    closets: List[netdot.Closet] = repository.get_closets_where(id=1)

    # Assert
    assert_that(closets).is_length(1)
    response = repository.connection.http.get(closets[0].web_url)
    response.raise_for_status()



@pytest.mark.vcr
def test_get_Contacts_where(repository: Repository):
    # Act
    contacts: List[netdot.Contact] = repository.get_contacts_where(id=480)

    # Assert
    assert_that(contacts).is_length(1)
    response = repository.connection.http.get(contacts[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_ContactLists_where(repository: Repository):
    # Act
    contact_lists: List[netdot.ContactList] = repository.get_contactlists_where(
        id=1
    )

    # Assert
    assert_that(contact_lists).is_length(1)
    response = repository.connection.http.get(contact_lists[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_ContactTypes_where(repository: Repository):
    # Act
    contact_types: List[netdot.ContactType] = repository.get_contacttypes_where(
        id=1
    )

    # Assert
    assert_that(contact_types).is_length(1)
    response = repository.connection.http.get(contact_types[0].web_url)
    response.raise_for_status()


# @pytest.mark.vcr
# def test_get_DataCaches_where(repository: Repository):
#     # Act
#     data_caches: List[netdot.DataCache] = repository.get_datacaches_where(id=3)

#     # Assert
#     assert_that(data_caches).is_length(1)


@pytest.mark.vcr
def test_get_Devices_where(repository: Repository):
    # Act
    devices: List[netdot.Device] = repository.get_devices_where(id=4330)

    # Assert
    assert_that(devices).is_length(1)
    response = repository.connection.http.get(devices[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_DeviceAttrs_where(repository: Repository):
    # Act
    device_attrs: List[netdot.DeviceAttr] = repository.get_deviceattrs_where(id=12)

    # Assert
    assert_that(device_attrs).is_length(1)
    response = repository.connection.http.get(device_attrs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_DeviceAttrNames_where(repository: Repository):
    # Act
    device_attr_names: List[
        netdot.DeviceAttrName
    ] = repository.get_deviceattrnames_where(id=1)

    # Assert
    assert_that(device_attr_names).is_length(1)
    response = repository.connection.http.get(device_attr_names[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_DeviceContacts_where(repository: Repository):
    # Act
    device_contacts: List[
        netdot.DeviceContacts
    ] = repository.get_devicecontacts_where(id=3411)

    # Assert
    assert_that(device_contacts).is_length(1)
    response = repository.connection.http.get(device_contacts[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_DeviceModules_where(repository: Repository):
    # Act
    device_modules: List[netdot.DeviceModule] = repository.get_devicemodules_where(
        id=1
    )

    # Assert
    assert_that(device_modules).is_length(1)
    response = repository.connection.http.get(device_modules[0].web_url)
    response.raise_for_status()
    assert_that(device_modules[0].class__KEYWORD_ESC).is_equal_to('chassis')


@pytest.mark.vcr
def test_get_DHCPAttrs_where(repository: Repository):
    # Act
    dhcp_attrs: List[netdot.DHCPAttr] = repository.get_dhcpattrs_where(id=1)

    # Assert
    assert_that(dhcp_attrs).is_length(1)
    response = repository.connection.http.get(dhcp_attrs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_DHCPAttrNames_where(repository: Repository):
    # Act
    dhcp_attr_names: List[netdot.DHCPAttrName] = repository.get_dhcpattrnames_where(
        id=1
    )

    # Assert
    assert_that(dhcp_attr_names).is_length(1)
    response = repository.connection.http.get(dhcp_attr_names[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_DHCPScopes_where(repository: Repository):
    # Act
    dhcp_scopes: List[netdot.DHCPScope] = repository.get_dhcpscopes_where(id=1)

    # Assert
    assert_that(dhcp_scopes).is_length(1)
    response = repository.connection.http.get(dhcp_scopes[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_DHCPScopeTypes_where(repository: Repository):
    # Act
    dhcp_scope_types: List[netdot.DHCPScopeType] = repository.get_dhcpscopes_where(
        id=1
    )

    # Assert
    assert_that(dhcp_scope_types).is_length(1)
    response = repository.connection.http.get(dhcp_scope_types[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_DHCPScopeUses_where(repository: Repository):
    # Act
    dhcp_scope_uses: List[netdot.DHCPScopeUse] = repository.get_dhcpscopeuses_where(
        id=487
    )

    # Assert
    assert_that(dhcp_scope_uses).is_length(1)
    response = repository.connection.http.get(dhcp_scope_uses[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Entities_where(repository: Repository):
    # Act
    entities: List[netdot.Entity] = repository.get_entities_where(id=202)

    # Assert
    assert_that(entities).is_length(1)
    response = repository.connection.http.get(entities[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_EntityRoles_where(repository: Repository):
    # Act
    entity_roles: List[netdot.EntityRole] = repository.get_entityroles_where(id=1)

    # Assert
    assert_that(entity_roles).is_length(1)
    response = repository.connection.http.get(entity_roles[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_EntitySites_where(repository: Repository):
    # Act
    entity_sites: List[netdot.EntitySite] = repository.get_entitysites_where(id=297)

    # Assert
    assert_that(entity_sites).is_length(1)
    response = repository.connection.http.get(entity_sites[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_EntityTypes_where(repository: Repository):
    # Act
    entity_types: List[netdot.EntityType] = repository.get_entitytypes_where(id=1)

    # Assert
    assert_that(entity_types).is_length(1)
    response = repository.connection.http.get(entity_types[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_FiberTypes_where(repository: Repository):
    # Act
    fiber_types: List[netdot.FiberType] = repository.get_fibertypes_where(id=1)

    # Assert
    assert_that(fiber_types).is_length(1)
    response = repository.connection.http.get(fiber_types[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Floors_where(repository: Repository):
    # Act
    floors: List[netdot.Floor] = repository.get_floors_where(id=1)

    # Assert
    assert_that(floors).is_length(1)
    response = repository.connection.http.get(floors[0].web_url)
    response.raise_for_status()


# # @pytest.mark.vcr
# def test_get_FloorPictures_NONE_AVAILABLE(repository: Repository):
#     # Act & Assert
#     # ! NO FloorPictures available
#     assert_that(repository.get_floorpictures).raises(
#         netdot.exceptions.HTTPError
#     ).when_called_with()


@pytest.mark.vcr
def test_get_FWTables_where(repository: Repository):
    # Act
    fw_tables: List[netdot.FWTable] = repository.get_fwtables_where(id=1)

    # Assert
    assert_that(fw_tables).is_length(1)
    response = repository.connection.http.get(fw_tables[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_FWTableEntries_where(repository: Repository):
    # Act
    fw_table_entries: List[
        netdot.FWTableEntry
    ] = repository.get_fwtableentries_where(id=1)

    # Assert
    assert_that(fw_table_entries).is_length(1)
    response = repository.connection.http.get(fw_table_entries[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_GroupRights_where(repository: Repository):
    # Act
    group_rights: List[netdot.GroupRight] = repository.get_grouprights_where(id=1)

    # Assert
    assert_that(group_rights).is_length(1)
    response = repository.connection.http.get(group_rights[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_HorizontalCables_where(repository: Repository):
    # Act
    horizontal_cables: List[
        netdot.HorizontalCable
    ] = repository.get_horizontalcables_where(id=1)

    # Assert
    assert_that(horizontal_cables).is_length(1)
    response = repository.connection.http.get(horizontal_cables[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_HostAudits_where(repository: Repository):
    # Act
    host_audits: List[netdot.HostAudit] = repository.get_hostaudits_where(
        id=13398890
    )

    # Assert
    assert_that(host_audits).is_length(1)
    response = repository.connection.http.get(host_audits[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Interfaces_where(repository: Repository):
    # Act
    interfaces: List[netdot.Interface] = repository.get_interfaces_where(id=100587)

    # Assert
    assert_that(interfaces).is_length(1)
    response = repository.connection.http.get(interfaces[0].web_url)
    response.raise_for_status()
    interface = interfaces[0]
    assert_that(interface.is_up).is_true()


@pytest.mark.vcr
def test_get_InterfaceVLANs_where(repository: Repository):
    # Act
    interface_vlans: List[
        netdot.InterfaceVLAN
    ] = repository.get_interfacevlans_where(id=14365)

    # Assert
    assert_that(interface_vlans).is_length(1)
    response = repository.connection.http.get(interface_vlans[0].web_url)
    response.raise_for_status()

@pytest.mark.vcr
def test_get_IPBlocks_where(repository: Repository):
    # Act
    ip_blocks: List[netdot.IPBlock] = repository.get_ipblocks_where(id=159)

    # Assert
    assert_that(ip_blocks).is_length(1)
    response = repository.connection.http.get(ip_blocks[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_IPBlockAttrs_where(repository: Repository):
    # Act
    ip_block_attrs: List[netdot.IPBlockAttr] = repository.get_ipblockattrs_where(
        id=11
    )

    # Assert
    assert_that(ip_block_attrs).is_length(1)
    response = repository.connection.http.get(ip_block_attrs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_IPBlockAttrNames_where(repository: Repository):
    # Act
    ip_block_attr_names: List[
        netdot.IPBlockAttrName
    ] = repository.get_ipblockattrnames_where(id=1)

    # Assert
    assert_that(ip_block_attr_names).is_length(1)
    response = repository.connection.http.get(ip_block_attr_names[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_IPBlockStatuses_where(repository: Repository):
    # Act
    ip_block_statuses: List[
        netdot.IPBlockStatus
    ] = repository.get_ipblockstatuses_where(id=1)

    # Assert
    assert_that(ip_block_statuses).is_length(1)
    response = repository.connection.http.get(ip_block_statuses[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_IPServices_where(repository: Repository):
    # Act
    ip_services: List[netdot.IPService] = repository.get_ipservices_where(id=1)

    # Assert
    assert_that(ip_services).is_length(1)
    response = repository.connection.http.get(ip_services[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_MaintContracts_where(repository: Repository):
    # Act
    maint_contracts: List[
        netdot.MaintContract
    ] = repository.get_maintcontracts_where(id=1)

    # Assert
    assert_that(maint_contracts).is_length(1)
    response = repository.connection.http.get(maint_contracts[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_MonitorStatuses_where(repository: Repository):
    # Act
    monitor_statuses: List[
        netdot.MonitorStatus
    ] = repository.get_monitorstatuses_where(id=1)

    # Assert
    assert_that(monitor_statuses).is_length(1)
    response = repository.connection.http.get(monitor_statuses[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_OUIs_where(repository: Repository):
    # Act
    ouis: List[netdot.OUI] = repository.get_ouis_where(id=82432)

    # Assert
    assert_that(ouis).is_length(1)
    response = repository.connection.http.get(ouis[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Persons_where(repository: Repository):
    # Act
    persons: List[netdot.Person] = repository.get_persons_where(id=1)

    # Assert
    assert_that(persons).is_length(1)
    response = repository.connection.http.get(persons[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_PhysAddrs_where(repository: Repository):
    # Act
    phys_addrs: List[netdot.PhysAddr] = repository.get_physaddrs_where(id=1)

    # Assert
    assert_that(phys_addrs).is_length(1)
    response = repository.connection.http.get(phys_addrs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_PhysAddrAttrs_NONE_AVAILABLE(repository: Repository):
    # Act & Assert
    # ! NO PhysAddrAttrs available
    assert_that(repository.get_physaddrattrs_where).raises(
        netdot.exceptions.HTTPError
    ).when_called_with()


@pytest.mark.vcr
def test_get_PhysAddrAttrNames_where(repository: Repository):
    # Act
    phys_addr_attr_names: List[
        netdot.PhysAddrAttrName
    ] = repository.get_physaddrattrnames_where(id=1)

    # Assert
    assert_that(phys_addr_attr_names).is_length(1)
    response = repository.connection.http.get(phys_addr_attr_names[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Products_where(repository: Repository):
    # Act
    products: List[netdot.Product] = repository.get_products_where(id=1)

    # Assert
    assert_that(products).is_length(1)
    response = repository.connection.http.get(products[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_ProductTypes_where(repository: Repository):
    # Act
    product_types: List[netdot.ProductType] = repository.get_producttypes_where(
        id=1
    )

    # Assert
    assert_that(product_types).is_length(1)
    response = repository.connection.http.get(product_types[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Rooms_where(repository: Repository):
    # Act
    rooms: List[netdot.Room] = repository.get_rooms_where(id=1)

    # Assert
    assert_that(rooms).is_length(1)
    response = repository.connection.http.get(rooms[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRs_where(repository: Repository):
    # Act
    rrs: List[netdot.RR] = repository.get_rr_where(id=1849)

    # Assert
    assert_that(rrs).is_length(1)
    response = repository.connection.http.get(rrs[0].web_url)
    response.raise_for_status()
    assert_that(rrs[0].infer_FQDN()).is_equal_to('flowbee.uoregon.edu')


@pytest.mark.vcr
def test_get_RRAddrs_where(repository: Repository):
    # Act
    rr_addrs: List[netdot.RRADDR] = repository.get_rraddr_where(id=6674)

    # Assert
    assert_that(rr_addrs).is_length(1)
    response = repository.connection.http.get(rr_addrs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRCNAMEs_where(repository: Repository):
    # Act
    rrcnames: List[netdot.RRCNAME] = repository.get_rrcname_where(id=4276)

    # Assert
    assert_that(rrcnames).is_length(1)
    response = repository.connection.http.get(rrcnames[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRDSs_where(repository: Repository):
    # Act
    rrds: List[netdot.RRDS] = repository.get_rrds_where(id=1)

    # Assert
    assert_that(rrds).is_length(1)
    response = repository.connection.http.get(rrds[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRHINFOs_where(repository: Repository):
    # Act
    rrhinfos: List[netdot.RRHINFO] = repository.get_rrhinfo_where(id=1)

    # Assert
    assert_that(rrhinfos).is_length(1)
    response = repository.connection.http.get(rrhinfos[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRLOCs_where(repository: Repository):
    # Act
    rrlocs: List[netdot.RRLOC] = repository.get_rrloc_where(id=11)

    # Assert
    assert_that(rrlocs).is_length(1)
    response = repository.connection.http.get(rrlocs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRMXs_where(repository: Repository):
    # Act
    rrmxs: List[netdot.RRMX] = repository.get_rrmx_where(id=112)

    # Assert
    assert_that(rrmxs).is_length(1)
    response = repository.connection.http.get(rrmxs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRNAPTR_NONE_AVAILABLE(repository: Repository):
    # Act & Assert
    # ! NO RRNAPTRs available
    assert_that(repository.get_rrnaptr_where).raises(
        netdot.exceptions.HTTPError
    ).when_called_with()


@pytest.mark.vcr
def test_get_RRNSs_where(repository: Repository):
    # Act
    rrns: List[netdot.RRNS] = repository.get_rrns_where(id=27)

    # Assert
    assert_that(rrns).is_length(1)
    response = repository.connection.http.get(rrns[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRPTRs_where(repository: Repository):
    # Act
    rrptrs: List[netdot.RRPTR] = repository.get_rrptr_where(id=760)

    # Assert
    assert_that(rrptrs).is_length(1)
    response = repository.connection.http.get(rrptrs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRSRVs_where(repository: Repository):
    # Act
    rrsrvs: List[netdot.RRSRV] = repository.get_rrsrv_where(id=1)

    # Assert
    assert_that(rrsrvs).is_length(1)
    response = repository.connection.http.get(rrsrvs[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_RRTXTs_where(repository: Repository):
    # Act
    rrtxts: List[netdot.RRTXT] = repository.get_rrtxt_where(id=61731)

    # Assert
    assert_that(rrtxts).is_length(1)
    response = repository.connection.http.get(rrtxts[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_SavedQueries_where(repository: Repository):
    # Act
    saved_queries: List[netdot.SavedQueries] = repository.get_savedqueries_where(
        id=30
    )

    # Assert
    assert_that(saved_queries).is_length(1)
    response = repository.connection.http.get(saved_queries[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_SchemaInfo_where(repository: Repository):
    # Act
    schema_info: List[netdot.SchemaInfo] = repository.get_schemainfo_where(id=1)

    # Assert
    assert_that(schema_info).is_length(1)
    response = repository.connection.http.get(schema_info[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Services_where(repository: Repository):
    # Act
    services: List[netdot.Service] = repository.get_services_where(id=1)

    # Assert
    assert_that(services).is_length(1)
    response = repository.connection.http.get(services[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Sites_where(repository: Repository):
    # Act
    sites: List[netdot.Site] = repository.get_sites_where(id=137)

    # Assert
    assert_that(sites).is_length(1)
    response = repository.connection.http.get(sites[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_SiteLinks_where(repository: Repository):
    # Act
    site_links: List[netdot.SiteLink] = repository.get_sitelinks_where(id=51)

    # Assert
    assert_that(site_links).is_length(1)
    response = repository.connection.http.get(site_links[0].web_url)
    response.raise_for_status()


# @pytest.mark.vcr
# def test_get_SitePictures_where(repository: Repository):
#     # Act
#     site_pictures: List[netdot.SitePicture] = repository.get_sitepictures_where(id=8)

#     # Assert
#     assert_that(site_pictures).is_length(1)


@pytest.mark.vcr
def test_get_SiteSubnets_where(repository: Repository):
    # Act
    site_subnets: List[netdot.SiteSubnet] = repository.get_sitesubnets_where(id=1)

    # Assert
    assert_that(site_subnets).is_length(1)
    response = repository.connection.http.get(site_subnets[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Splices_where(repository: Repository):
    # Act
    splices: List[netdot.Splice] = repository.get_splices_where(id=2420)

    # Assert
    assert_that(splices).is_length(1)
    response = repository.connection.http.get(splices[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_STPInstances_where(repository: Repository):
    # Act
    stp_instances: List[netdot.STPInstance] = repository.get_stpinstances_where(
        id=6138
    )

    # Assert
    assert_that(stp_instances).is_length(1)
    response = repository.connection.http.get(stp_instances[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_StrandStatuses_where(repository: Repository):
    # Act
    strand_statuses: List[
        netdot.StrandStatus
    ] = repository.get_strandstatuses_where(id=1)

    # Assert
    assert_that(strand_statuses).is_length(1)
    response = repository.connection.http.get(strand_statuses[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_SubnetZones_where(repository: Repository):
    # Act
    subnet_zones: List[netdot.SubnetZone] = repository.get_subnetzones_where(id=1)

    # Assert
    assert_that(subnet_zones).is_length(1)
    response = repository.connection.http.get(subnet_zones[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_UserRights_where(repository: Repository):
    # Act
    user_rights: List[netdot.UserRight] = repository.get_userrights_where(id=233)

    # Assert
    assert_that(user_rights).is_length(1)
    response = repository.connection.http.get(user_rights[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_UserTypes_where(repository: Repository):
    # Act
    user_types: List[netdot.UserType] = repository.get_usertypes_where(id=1)

    # Assert
    assert_that(user_types).is_length(1)
    response = repository.connection.http.get(user_types[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_VLANs_where(repository: Repository):
    # Act
    vlans: List[netdot.VLAN] = repository.get_vlans_where(id=1)

    # Assert
    assert_that(vlans).is_length(1)
    response = repository.connection.http.get(vlans[0].web_url)
    response.raise_for_status()
    assert_that(vlans[0].has_valid_vid).is_true()


@pytest.mark.vcr
def test_get_VLANGroups_where(repository: Repository):
    # Act
    vlan_groups: List[netdot.VLANGroup] = repository.get_vlangroups_where(id=1)

    # Assert
    assert_that(vlan_groups).is_length(1)
    response = repository.connection.http.get(vlan_groups[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_Zones_where(repository: Repository):
    # Act
    zones: List[netdot.Zone] = repository.get_zones_where(id=1)

    # Assert
    assert_that(zones).is_length(1)
    response = repository.connection.http.get(zones[0].web_url)
    response.raise_for_status()


@pytest.mark.vcr
def test_get_ZoneAliases_where(repository: Repository):
    # Act
    zone_aliases: List[netdot.ZoneAlias] = repository.get_zonealiases_where(id=1)

    # Assert
    assert_that(zone_aliases).is_length(1)
    response = repository.connection.http.get(zone_aliases[0].web_url)
    response.raise_for_status()
