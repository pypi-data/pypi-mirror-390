import dataclasses
import textwrap

from assertpy import assert_that, contents_of

import netdot
from netdot.csv_util import CSVDataclass, as_csv, CSVReport


def test_as_csv():
    headers = ['col1', 'col2', 'col3']
    data = [(1, 2, 3), (4, 5, 6)]

    # Act
    csv_string = as_csv(data, headers)

    # Assert
    assert_that(csv_string).contains(
        textwrap.dedent(
            '''\
            col1,col2,col3
            1,2,3
            4,5,6'''
        )
    )


def test_escape_delim():
    headers = ['sentence_col1', 'col2', 'col3']
    data = [('To be, or not to be,', 2, 3), ('that is the question.', 5, 6)]

    # Act
    csv_string = as_csv(data, headers)

    # Assert
    assert_that(csv_string).contains("\"To be, or not to be,\"")


def test_csv_dataclass():
    # Arange & Act
    @dataclasses.dataclass
    class Foo(CSVDataclass):
        a: int

    # Assert
    foo = Foo(a=1)
    assert_that(foo.table_header()).is_equal_to(tuple(['a']))
    assert_that(foo.as_table_row()).is_equal_to(tuple(['1']))


def test_csv_dataclass_select_columns():
    # Arange & Act
    @dataclasses.dataclass
    class Foo(CSVDataclass):
        a: int
        b: int
        c: int
        d: int

    # Assert
    foo = Foo(a=1, b=2, c=3, d=4)
    data = foo.as_table_row(select_columns=['a', 'd'])
    assert_that(data).is_equal_to(tuple(['1', '4']))


def test_CSVReport():
    # Arange
    data = [
        netdot.Site(name='Test1', id=1),
        netdot.Site(name='Test2', id=2),
        netdot.Site(name='Test3', id=3),
    ]
    report = CSVReport[netdot.Site](data)

    # Act
    result = report.as_csv()

    # Assert
    assert_that(result).contains(
        'id,name,aliases,availability,contactlist,gsf,number,street1,street2,state,city,country,zip,pobox,info'
    )
    assert_that(result).contains('1,Test1,None,None')
    assert_that(result).contains('2,Test2,None,None')
    assert_that(result).contains('3,Test3,None,None')


def test_CSVReport_custom_header():
    # Arange
    data = [
        netdot.Site(name='Test1', number=1),
        netdot.Site(name='Test2', number=2),
        netdot.Site(name='Test3', number=3),
    ]
    header = ['name', 'number']
    report = CSVReport[netdot.Site](data, header)

    # Act
    result = report.as_csv()

    # Assert
    assert_that(result).contains('name,number')
    assert_that(result).contains('Test1,1')
    assert_that(result).contains('Test2,2')
    assert_that(result).contains('Test3,3')


def test_CSVReport_save_as_file(tmp_path):
    # Arange
    data = [
        netdot.Site(name='Test1', number=1),
        netdot.Site(name='Test2', number=2),
        netdot.Site(name='Test3', number=3),
    ]
    header = ['name', 'number']
    report = CSVReport[netdot.Site](data, header)

    # Act
    bytes_written = report.save_as_file('out', str(tmp_path)+"/auto-created-dir/")

    # Assert
    assert_that(bytes_written).is_greater_than(32)
    assert_that(f'{tmp_path}/auto-created-dir/out.csv').exists()
    assert_that(contents_of(f'{tmp_path}/auto-created-dir/out.csv')).contains(
        'name,number\nTest1,1\nTest2,2\nTest3,3'
    )


def test_CSVReport_override_header():
    # Arange
    data = [
        netdot.Site(name='Test1', number=1),
        netdot.Site(name='Test2', number=2),
        netdot.Site(name='Test3', number=3),
    ]
    header = ['name', 'number']
    report = CSVReport[netdot.Site](data, header)

    # Act
    header_labels = ['Site Name', 'Site ID (Building Number)']
    result = report.as_csv(override_header=header_labels)

    # Assert
    assert_that(result).contains('Site Name,Site ID (Building Number)')
    assert_that(result).contains('Test1,1')
    assert_that(result).contains('Test2,2')
    assert_that(result).contains('Test3,3')


def test_CSVReport_override_header_too_many():
    # Arange
    data = [
        netdot.Site(name='Test1', number=1),
        netdot.Site(name='Test2', number=2),
        netdot.Site(name='Test3', number=3),
    ]
    header = ['name', 'number']
    report = CSVReport[netdot.Site](data, header)
    # Header Labels are supposed to override header 1-for-1, so adding 'ID' is invalid here
    header_labels = ['ID', 'Site Name', 'Site Number']

    # Act & Assert
    assert_that(report.as_csv).raises(ValueError).when_called_with(
        override_header=header_labels
    )


def test_CSVReport_sort():
    # Arange
    data = [
        netdot.Site(id=3, number='A'),
        netdot.Site(id=2, number='B'),
        netdot.Site(id=1, number='C'),
    ]
    header = ['id', 'number']
    report = CSVReport[netdot.Site](data, header)

    # Act
    report.sort()

    # Assert
    assert_that(report.items[0].id).is_equal_to(1)
    assert_that(report.items[1].id).is_equal_to(2)
    assert_that(report.items[2].id).is_equal_to(3)


def test_CSVReport_sort_by_number():
    # Arange
    data = [
        netdot.Site(id=1, number='C'),
        netdot.Site(id=2, number='B'),
        netdot.Site(id=3, number='A'),
    ]
    header = ['id', 'number']
    report = CSVReport[netdot.Site](data, header)

    # Act
    report.sort('number')

    # Assert
    assert_that(report.items[0].number).is_equal_to('A')
    assert_that(report.items[1].number).is_equal_to('B')
    assert_that(report.items[2].number).is_equal_to('C')


def test_CSVReport_sort_multicol():
    # Arange
    data = [
        netdot.Site(id=1, name='TEST2', number='C'),
        netdot.Site(id=2, name='TEST2', number='B'),
        netdot.Site(id=3, name='TEST2', number='A'),
        netdot.Site(id=4, name='TEST1', number='Z'),
    ]
    header = ['id', 'number', 'name']
    report = CSVReport[netdot.Site](data, header)

    # Act
    report.sort('name', 'number')

    # Assert
    assert_that(report.items[0].name).is_equal_to('TEST1')
    assert_that(report.items[0].number).is_equal_to('Z')
    assert_that(report.items[1].name).is_equal_to('TEST2')
    assert_that(report.items[1].number).is_equal_to('A')
    assert_that(report.items[2].number).is_equal_to('B')
    assert_that(report.items[3].number).is_equal_to('C')


def test_CSVReport_empty_header():
    # Arange
    data = [
        (
            1,
            2,
        ),
        (
            3,
            4,
        ),
    ]
    report = CSVReport[dict](data)

    # Act & Assert
    assert_that(report.as_csv).raises(ValueError).when_called_with().contains(
        'Unable to determine table header for CSVReport'
    )
