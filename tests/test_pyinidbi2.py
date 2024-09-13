import os
import re

import pytest

from pyinidbi2.pyinidbi2 import INIFile, Section

DBNAME = "db_name"
FILENAME = "This is a test database file.ini"
FILEPATH = f"db/{FILENAME}"
EXISTFILE = "XDF_Op_TigerTrap.ini"


@pytest.fixture
def sample_db_obj() -> INIFile:
    if os.path.isfile(FILEPATH):
        os.remove(FILEPATH)
    ini = INIFile(DBNAME, FILENAME)
    ini.write(True)
    return ini


@pytest.fixture
def sample_section() -> Section:
    section = Section("sample_section")
    section.set("key_one", "value_one")
    section.set("key_two", "value_two")
    section.set("key_three", "value_three")
    return section


def test_read_existing_ini_file():
    section_list: list[str] = []
    with open(f"db/{EXISTFILE}") as fd:
        for line in fd.readlines():
            if (line.find("[")) == 0:
                section_list.append(line)

    ini = INIFile(DBNAME, EXISTFILE)
    assert len(section_list) == len(ini.sections) + 1


def test_create_inifile_with_meta_section(sample_db_obj: INIFile):
    with open(sample_db_obj.file_path) as fd:
        first_line = fd.readline()
    assert first_line == "[meta]\n"
    os.remove(sample_db_obj.file_path)


def test_should_contain_meta_data(sample_db_obj: INIFile):
    with open(sample_db_obj.file_path) as fd:
        line = fd.readline()
        assert line == "[meta]\n"
        line = fd.readline()
        assert re.fullmatch('^db_name=".*"\n$', line) is not None
        line = fd.readline()
        assert (
            re.fullmatch(
                '^create_date_utc="[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9|:]{8}"\n', line
            )
            is not None
        )
        line = fd.readline()
        assert (
            re.fullmatch(
                '^create_date_server="[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9|:]{8}"\n', line
            )
        ) is not None
    os.remove(sample_db_obj.file_path)


def test_compare_content_with_existing_ini_file():
    with open(f"db/{EXISTFILE}") as fd:
        output = "".join(fd.readlines())

    ini = INIFile(DBNAME, EXISTFILE)
    assert output == ini.as_string()


def test_add_new_item_to_section(sample_section: Section, sample_db_obj: INIFile):
    sample_db_obj.add(sample_section)
    sample_db_obj.write(True)
    section = sample_db_obj.get("sample_section")
    output = ""
    if section is not None:
        section.set("odd_key", '["odd_value"]')
        sample_db_obj.add(section)
        sample_db_obj.write(True)
        section = sample_db_obj.get('sample_section')
        if section is not None:
            output = section.as_string()

    assert (
        output
        == """[sample_section]
key_one="value_one"
key_two="value_two"
key_three="value_three"
odd_key="["odd_value"]"
"""
    )
    os.remove(sample_db_obj.file_path)


def test_return_all_keys_from_a_section(sample_section: Section):
    assert sample_section.keys() == ("key_one", "key_two", "key_three")


def test_remove_item_from_section(sample_section: Section):
    section = sample_section
    _ = section.remove("key_two")
    assert (
        section.as_string()
        == """[sample_section]
key_one="value_one"
key_three="value_three"
"""
    )


def test_get_a_section(sample_section: Section, sample_db_obj: INIFile):
    sample_db_obj.add(sample_section)
    section = sample_db_obj.get("sample_section")
    output = ""

    if section is not None:
        output = section.as_string()

    assert (
        output
        == """[sample_section]
key_one="value_one"
key_two="value_two"
key_three="value_three"
"""
    )


def test_delete_section_from_ini_file(sample_section: Section):
    ini = INIFile(DBNAME, FILENAME)
    ini.add(sample_section)
    section = Section("new_section")
    section.set("new_key", "new_value")
    ini.add(section)
    ini.remove("sample_section")
    ini.write(True)
    assert ini.sections == ["new_section"]
    os.remove(ini.file_path)
