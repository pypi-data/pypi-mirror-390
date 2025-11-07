import datetime
import ipaddress
from typing import List

import pytest
from assertpy import assert_that

import netdot
import netdot.exceptions
from netdot import Repository
from netdot.mac_address import MACAddress


def test__Repository_initialization_of_methods():
    # Arrange (assert)
    # Depending on test execution order -- pytest has likely already initialized repository!
    # assert_that(Repository._initialized).is_false()

    # Act
    Repository._prepare_class()

    # Assert
    assert_that(Repository._initialized).is_true()
    Repository_attribute_names = vars(Repository).keys()
    assert_that(Repository_attribute_names).contains("get_device")
    assert_that(Repository_attribute_names).contains("get_devices_where")
    assert_that(Repository_attribute_names).contains("get_site")
    assert_that(Repository_attribute_names).contains("get_devices_by_site")
    assert_that(Repository_attribute_names).contains("get_devices_by_asset_id")
    assert_that(Repository_attribute_names).contains("get_interfaces_by_device")


@pytest.mark.vcr()
def test_discover_sites_devices(repository: Repository):
    # Arrange
    site = repository.get_site(142)  # 142 => 1900 Millrace Drive

    # Act
    devices = site.load_devices()

    # Assert
    assert_that(devices).is_length(3)


@pytest.mark.vcr()
def test_get_devices_by_site(repository: Repository):
    # Arrange
    site = repository.get_site(142)  # 142 => 1900 Millrace Drive

    # Act
    devices = repository.get_devices_by_site(site)

    # Assert
    assert_that(devices).is_length(3)


@pytest.mark.vcr()
def test_get_site_from_device(repository: Repository):
    # Arrange
    MILLRACE_BLDG_NUMBER = "043"
    # A device from 1900 Millrace Drive (rrpnet-1900-millrace-drive-poe-sw1.net.uoregon.edu)
    MILLRACE_DEVICE_ID = 9061
    device = repository.get_device(MILLRACE_DEVICE_ID)

    # Act
    site = device.load_site()

    # Assert
    assert_that(site.number).is_equal_to(MILLRACE_BLDG_NUMBER)


@pytest.mark.vcr()
def test_discover_device_interfaces(repository: Repository):
    # Arrange
    device = repository.get_device(9643)  # 9643 => alder-building-mdf-poe-sw1

    # Act
    interfaces = device.load_interfaces()

    # Assert
    assert_that(interfaces).is_length(58)
    interface = interfaces[0]
    assert_that(interface.physaddr).is_equal_to(MACAddress("B033A673763B"))


@pytest.mark.vcr()
def test_get_ipblock_StaticAddress(repository: Repository):
    # Act
    ipblock_address: netdot.IPBlock = repository.get_ipblock(
        177611046
    )  # "uoregon.edu" IP address

    # Assert
    assert_that(ipblock_address.address).is_equal_to(
        ipaddress.ip_address("184.171.111.233")
    )
    assert_that(ipblock_address.prefix).is_equal_to(32)
    assert_that(ipblock_address.status).is_equal_to("Static")
    assert_that(ipblock_address.used_by).is_none()


@pytest.mark.vcr()
def test_get_ipblock_Subnet(repository: Repository):
    # Act
    # Subnet associated to "uoregon.edu" IP address
    ipblock_subnet = repository.get_ipblock(271514934)

    # Assert
    assert_that(ipblock_subnet.address).is_equal_to(
        ipaddress.ip_address("184.171.111.0")
    )
    assert_that(ipblock_subnet.prefix).is_equal_to(24)
    assert_that(ipblock_subnet.status).is_equal_to("Subnet")
    assert_that(ipblock_subnet.used_by).is_equal_to("Information Services")


@pytest.mark.vcr()
def test_get_ipblock_Container(repository: Repository):
    # Act
    # Container associated to "uoregon.edu" Subnet
    ipblock_container = repository.get_ipblock(177611409)

    # Assert
    assert_that(ipblock_container.address).is_equal_to(
        ipaddress.ip_address("184.171.96.0")
    )
    assert_that(ipblock_container.prefix).is_equal_to(19)
    assert_that(ipblock_container.status).is_equal_to("Container")


@pytest.mark.vcr()
def test_discover_ipblock_Subnet_from_StaticAddress(repository: Repository):
    # Arrange
    ipblock_address = repository.get_ipblock(177611046)

    # Act
    ipblock_subnet = ipblock_address.load_parent()

    # Assert
    assert_that(ipblock_subnet.address).is_equal_to(
        ipaddress.ip_address("184.171.111.0")
    )
    assert_that(ipblock_subnet.prefix).is_equal_to(24)
    assert_that(ipblock_subnet.status).is_equal_to("Subnet")
    assert_that(ipblock_subnet.used_by).is_equal_to("Information Services")


@pytest.mark.vcr()
def test_get_ipblock_by_address_StaticAddress(repository: Repository):
    # Act
    ipblock_address = repository.get_ipblock_by_address("184.171.111.233")

    # Assert
    assert_that(ipblock_address.address).is_equal_to(
        ipaddress.ip_address("184.171.111.233")
    )
    assert_that(ipblock_address.prefix).is_equal_to(32)
    assert_that(ipblock_address.status).is_equal_to("Static")
    assert_that(ipblock_address.used_by).is_none()


@pytest.mark.vcr()
def test_get_ipblock_by_address_StaticAddressIPv6(repository: Repository):
    # Act
    ipblock_address = repository.get_ipblock_by_address("2605:bc80:200f:2::5")

    # Assert
    assert_that(ipblock_address.address).is_equal_to(
        ipaddress.ip_address("2605:bc80:200f:2::5")
    )
    assert_that(ipblock_address.prefix).is_equal_to(128)
    assert_that(ipblock_address.status).is_equal_to("Reserved")


@pytest.mark.vcr()
def test_get_ipblock_by_address_Subnet(repository: Repository):
    # Act
    ipblock_subnet = repository.get_ipblock_by_address("184.171.111.0")
    ipblock_subnet.load_children()

    # Assert
    assert_that(ipblock_subnet.address).is_equal_to(
        ipaddress.ip_address("184.171.111.0")
    )
    assert_that(ipblock_subnet.prefix).is_equal_to(24)
    assert_that(ipblock_subnet.status).is_equal_to("Subnet")
    assert_that(ipblock_subnet.used_by).is_equal_to("Information Services")


@pytest.mark.vcr()
def test_get_product_with_wierd_name(repository: Repository):
    # Act
    product = repository.get_product(377)

    # Assert
    assert_that(product.name).is_equal_to("800-????5-02")
    assert_that(product.type).is_equal_to("Module")


@pytest.mark.vcr()
def test_get_product(repository: Repository):
    # Act
    product = repository.get_product(802)

    # Assert
    assert_that(product.name).is_equal_to("EX3400-24P")
    assert_that(product.type).is_equal_to("Switch")


@pytest.mark.vcr()
def test_get_products_all(repository: Repository):
    # Act
    products = repository.get_products_where("all")

    # Assert
    assert_that(products).is_length(800)


@pytest.mark.vcr()
def test_get_usertypes(repository: Repository):
    # Act
    user_types: List[netdot.UserType] = repository.get_usertypes_where("all")

    # Assert
    assert_that(user_types).is_length(3)
    assert_that(user_types[0].name).is_equal_to("Admin")


@pytest.mark.vcr()
def test_get_ASNs(repository: Repository):
    # Act
    ASNs: List[netdot.ASN] = repository.get_asns_where("all")

    # Assert
    assert_that(ASNs).is_length(11)
    assert_that(ASNs[0].number).is_equal_to(3582)
    assert_that(ASNs[0].description).is_equal_to('UOnet Main External ASN')
    assert_that(ASNs[0].info).is_equal_to(
        'Carries all routes to advertise to external peers.'
    )


@pytest.mark.vcr()
def test_get_physaddr(repository: Repository):
    # Act
    physaddr = repository.get_physaddr(17206353813)

    # Assert
    assert_that(physaddr.address).is_equal_to(MACAddress("8C3BADDA9EF1"))
    assert_that(physaddr.static).is_equal_to(False)



@pytest.mark.vcr()
def test_get_interface(repository: Repository):
    # Act
    interface = repository.get_interface(364234)

    # Assert
    assert_that(interface.device).is_equal_to("white-stag-1st-poe-sw1.net.uoregon.edu")
    assert_that(interface.jack).is_equal_to("814B0091")
    assert_that(interface.snmp_managed).is_equal_to(True)
    assert_that(interface.oper_up).is_equal_to(True)
    assert_that(interface.overwrite_descr).is_equal_to(True)
    assert_that(interface.web_url).is_equal_to("https://nsdb.uoregon.edu/generic/view.html?table=Interface&id=364234")


@pytest.mark.vcr()
def test_get_physaddr_by_MACAddress(repository: Repository):
    # Act
    physaddr = repository.get_physaddr_by_MACAddress(MACAddress("9C8ECD25905B"))

    # Assert
    assert_that(physaddr.id).is_equal_to(9629748756)
    assert_that(physaddr.address).is_equal_to(MACAddress("9C8ECD25905B"))
    assert_that(physaddr.static).is_equal_to(False)
    assert_that(physaddr.first_seen).is_equal_to(
        datetime.datetime(2020, 6, 9, 16, 39, 3)
    )
    assert_that(physaddr.last_seen).is_after(datetime.datetime(2022, 9, 2, 17, 0, 3))


@pytest.mark.vcr()
def test_get_FWTableEntry(repository: Repository):
    # Act
    entry = repository.get_fwtableentry(285686)

    # Assert
    assert_that(entry.interface).is_equal_to(
        "resnet-llc-s-bb.net.uoregon.edu [Port-channel1]"
    )
    assert_that(entry.physaddr).is_equal_to(MACAddress("2c2131adee70"))
    assert_that(entry.infer_timestamp()).is_type_of(datetime.datetime)
    assert_that(entry.web_url).is_equal_to(
        "https://nsdb.uoregon.edu/generic/view.html?table=FWTableEntry&id=285686"
    )


@pytest.mark.vcr()
def test_find_edge_port(repository: Repository):
    # Act
    interface = repository.find_edge_port("58BC27FED341")

    # Assert
    assert_that(interface.device).is_equal_to("arena-bb.net.uoregon.edu")
    assert_that(interface.name).is_equal_to("GigabitEthernet2/0/5")


@pytest.mark.vcr()
def test_find_edge_port_unknown_MACAddress(repository: Repository):
    # Act & Assert
    assert_that(repository.find_edge_port).raises(
        netdot.exceptions.HTTPError
    ).when_called_with("58BCDEADBEEF")


@pytest.mark.vcr()
def test_get_ResourceRecord(repository: Repository):
    # Act
    dns_record = repository.get_rr(54482)

    # Assert
    assert_that(dns_record.info).is_equal_to(
        "LOC: 215A Oregon Hall CON: Chris LeBlanc, 6-2931 "
    )
    assert_that(dns_record.name).is_equal_to("metadata2")
    # TODO fix the web_url logic
    # assert_that(dns_record.web_url).is_equal_to('https://nsdb.uoregon.edu/management/host.html?id=54482')


@pytest.mark.vcr()
def test_get_ResourceRecord_by_ipaddress1(repository: Repository):
    # Act
    dns_record = repository.get_rr_by_address("128.223.37.93")

    # Assert
    assert_that(dns_record.info).is_equal_to(
        "LOC: 215A Oregon Hall CON: Chris LeBlanc, 6-2931 "
    )
    assert_that(dns_record.name).is_equal_to("metadata2")


@pytest.mark.vcr()
def test_get_ResourceRecord_by_ipaddress2(repository: Repository):
    # Act
    dns_record = repository.get_rr_by_address("128.223.93.66")

    # Assert
    assert_that(dns_record.info).is_equal_to(
        "LOC: Onyx Bridge 361 CON: Solar Radiation Monitoring Lab, 346-4745 CON: Peter Harlan, 346-4745 "
    )
    assert_that(dns_record.name).is_equal_to("solardat")


@pytest.mark.vcr()
def test_get_person(repository: Repository):
    # Act
    person: netdot.dataclasses.Person = repository.get_person(870)

    # Assert
    assert_that(person.firstname).is_equal_to("Ryan")
    assert_that(person.lastname).is_equal_to("Leonard")
    assert_that(person.email).is_equal_to("rleonar7@uoregon.edu")
    assert_that(person.user_type).is_equal_to("Admin")


@pytest.mark.vcr()
def test_get_ipblockAttribute(repository: Repository):
    # Act
    attribute: netdot.IPBlockAttr = repository.get_ipblockattr(284)

    # Assert
    assert_that(attribute.name).is_equal_to("CTX-PRINTER")


@pytest.mark.vcr()
def test_get_ContactLists(repository: Repository):
    # Act
    contact_lists: List[netdot.ContactList] = repository.get_contactlists_where("all")

    # Assert
    assert_that(contact_lists).is_length(331)
    assert_that(contact_lists[0].name).is_equal_to("Network Services Contacts")
    assert_that(contact_lists[0].info).is_equal_to("")


@pytest.mark.vcr()
def test_get_AccessRights(repository: Repository):
    # Act
    access_rights: List[netdot.AccessRight] = repository.get_accessrights_where("all")

    # Assert
    assert_that(access_rights).is_length(3708)


@pytest.mark.vcr()
def test_get_ArpCache(repository: Repository):
    # Act
    arpcache: netdot.ArpCache = repository.get_arpcache(160)

    # Assert
    assert_that(arpcache.device).is_equal_to("uonet4-gw.net.uoregon.edu")
    assert_that(arpcache.id).is_equal_to(160)
    assert_that(arpcache.tstamp).is_equal_to(datetime.datetime(2025, 8, 31, 23, 0, 4))


@pytest.mark.vcr()
def test_get_ArpCacheEntry(repository: Repository):
    # Act
    arpcache_entry: netdot.ArpCacheEntry = repository.get_arpcacheentry(49056)

    # Assert
    assert_that(arpcache_entry.interface).is_equal_to("uonet4-gw.net.uoregon.edu [GigabitEthernet0]")
    assert_that(arpcache_entry.infer_timestamp()).is_equal_to(datetime.datetime(2025, 8, 31, 23, 0, 4))


@pytest.mark.vcr()
def test_get_Availabilities(repository: Repository):
    # Act
    availabilities: List[netdot.Availability] = repository.get_availabilities_where("all")

    # Assert
    assert_that(availabilities).is_length(5)


@pytest.mark.vcr()
def test_load_site_entities(repository: Repository):
    # Arrange
    site = repository.get_site(137)

    # Act
    entities = site.load_entities()

    # Assert
    assert_that(entities[0]).is_type_of(netdot.Entity)


@pytest.mark.vcr()
def test_load_site_entitysites(repository: Repository):
    # Arrange
    site = repository.get_site(137)

    # Act
    entity_sites = site.load_entitysites()

    # Assert
    assert_that(entity_sites[0]).is_type_of(netdot.EntitySite)


@pytest.mark.vcr()
def test_load_device_contacts(repository: Repository):
    # Arrange
    device = repository.get_device(9826)

    # Act
    contactlists = device.load_contactlists()

    # Assert
    assert_that(contactlists[0]).is_type_of(netdot.ContactList)


@pytest.mark.vcr()
def test_load_device_devicecontacts(repository: Repository):
    # Arrange
    device = repository.get_device(9826)

    # Act
    device_contacts = device.load_devicecontacts()

    # Assert
    assert_that(device_contacts[0]).is_type_of(netdot.DeviceContacts)


@pytest.mark.vcr()
def test_ipblock_load_sites(repository: Repository):
    # Arrange
    ipblock = repository.get_ipblock_by_address('128.223.61.0')

    # Act
    sites = ipblock.load_sites()

    # Assert
    assert_that(sites[0]).is_type_of(netdot.Site)


@pytest.mark.vcr()
def test_ipblock_load_sites__without_site_returns_EMPTY_LIST(repository: Repository):
    # Arrange
    ipblock = repository.get_ipblock_by_address('128.223.61.69')

    # Act
    sites = ipblock.load_sites()

    # Assert
    assert_that(sites).is_length(0)


@pytest.mark.vcr()
def test_ipblock_load_sites__without_site_RAISES_404(repository: Repository):
    # Arrange
    ipblock = repository.get_ipblock_by_address('128.223.61.69')

    # Act & Assert
    assert_that(ipblock.load_sites).raises(
        netdot.exceptions.HTTPError
    ).when_called_with(ignore_404=False)


@pytest.mark.vcr()
def test_update_Device_contacts(repository: Repository):
    # Arrange
    repository.disable_propose_changes()
    site = repository.get_site(137)
    zone = repository.get_zone(1)
    rr = repository.create_new(
        netdot.RR(
            expiration='2020-01-01 00:00:00',
            info='test-info',
            name='test-name',
            zone=zone,
            created='2020-01-01 00:00:00',
            modified='2020-01-01 00:00:00',
        )
    )
    new_contact_list = repository.create_new(
        netdot.ContactList(
            name='Test Contact List',
        )
    )
    device = repository.create_new(
        netdot.Device(
            site=site,
            name=rr,
        )
    )

    # Act
    # Delete any 'default contacts'
    default_contacts = device.load_devicecontacts()
    assert len(default_contacts) == 1  # Expect a single default contact
    for contact in default_contacts:
        contact.delete(confirm=False)
    # Add the 'new contact'
    device.add_contactlist(new_contact_list)

    # Assert
    retrieved_contact_lists = device.load_contactlists()
    assert_that(retrieved_contact_lists).is_length(1)
    retrieved_contact_list = retrieved_contact_lists[0]
    assert_that(retrieved_contact_list.name).is_equal_to('Test Contact List')
    assert_that(retrieved_contact_list.id).is_equal_to(new_contact_list.id)

    # Cleanup
    for obj in [device, rr, new_contact_list]:
        obj.delete(confirm=False)


@pytest.mark.vcr()
def test_get_host(repository: Repository):
    # Act
    host = repository.get_host_by_name('is-rleonar7-d1.uoregon.edu')

    # Assert
    assert str(host.ipblocks[0].address) == '128.223.250.170'
    assert host.RRs[1].name == 'is-rleonar7-d1'


@pytest.mark.vcr()
def test_get_host_not_found_raises_HTTPError(repository: Repository):
    # Act & Assert
    assert_that(repository.get_host_by_name).raises(
        netdot.exceptions.HTTPError
    ).when_called_with('nonexistent-hostname.example.com')


TINKER_NETWORK='10.253.249.0/24'
TINKER_NETWORK_STARTS_WITH='10.253.249.'
@pytest.mark.vcr()
def test_create_host_tinker_uoregon_edu(repository: Repository):
    # Arrange
    repository.disable_propose_changes()
    
    # Act
    rr = repository.create_host(TINKER_NETWORK, 'tinker.uoregon.edu')
    
    # Assert
    assert rr.zone == 'uoregon.edu'
    assert rr.name == 'tinker'

@pytest.mark.vcr()
def test_get_host_by_cname(repository: Repository):
    # Act
    host = repository.get_host_by_name('nsdb.uoregon.edu')
    assert len(host.addresses) == 0
    rrcnames = repository.get_rrcname_by_rr(host.RRs[0])
    host = repository.get_host_by_name(rrcnames[0].cname)

    # TODO How do you actually get the "address" (CNAMDover)
    # Assert
    assert len(host.addresses) == 1
    assert len(host.names) > 0
    assert any('nsdb' in name for name in host.names)



@pytest.mark.parametrize(
    'hostname,              addr_starts_with', [
    ('tinker',              TINKER_NETWORK_STARTS_WITH),
    ('tinker.uoregon.edu',  TINKER_NETWORK_STARTS_WITH),
    ('is-nsdb1',            '128.223.60.51'),
    # ('nsdb',              '128.223.60.'),
    ('is-rleonar7-d1',      '128.223.250.'),
    ('is-github-blob',      '128.223.250.'),
    ('is-github',           '128.223.250.'),
    ('is-github-run1',      '128.223.250.'),
    ('is-github-run2',      '128.223.250.'),
    ('is-github-run3',      '128.223.250.'),
])
@pytest.mark.vcr()
def test_get_host_ensure_subnet_correct(repository: Repository, hostname: str, addr_starts_with: str):
    # Act
    host = repository.get_host_by_name(hostname)
    
    # Assert
    assert len(host.addresses) == 1
    assert host.addresses[0].startswith(addr_starts_with)
    assert len(host.names) > 0
    assert any(name == hostname.split('.')[0] for name in host.names)
    # assert host.addresses[0] == '10.253.249.11'  #  Replay test, more fragile...

