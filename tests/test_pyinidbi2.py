import os
import re

import pytest

from pyinidbi2.pyinidbi2 import INIFile, Section

DBNAME = "db_name"
FILENAME = "This is a test database file.ini"
FILEPATH = f"tests/{FILENAME}"


@pytest.fixture
def sample_db_obj():
    return INIFile(DBNAME, FILENAME)


def test_should_create_inifile_with_meta_section(sample_db_obj: INIFile):
    assert isinstance(sample_db_obj, INIFile)
    assert os.path.isfile(sample_db_obj.file_path) is True
    with open(sample_db_obj.file_path) as fd:
        first_line = fd.readline()
    assert first_line == "[meta]\n"
    os.remove(sample_db_obj.file_path)


def test_should_contain_meta_data(sample_db_obj: INIFile):
    with open(sample_db_obj.file_path) as fd:
        line = fd.readline()
        assert line == "[meta]\n"
        line = fd.readline()
        assert re.fullmatch('^db_name = ".*"\n$', line) is not None
        line = fd.readline()
        assert (
            re.fullmatch(
                '^create_date_utc = "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9|:]{8}"\n', line
            )
            is not None
        )
        line = fd.readline()
        assert (
            re.fullmatch(
                '^create_date_server = "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9|:]{8}"\n', line
            )
        ) is not None
    os.remove(sample_db_obj.file_path)


def test_should_insert_section_with_content(sample_db_obj: INIFile):
    title = "test_section"
    key = "test_key"
    value = "test_str"
    section = Section(title)
    section.set(key, value)
    sample_db_obj.add(section)
    found = False

    with open(sample_db_obj.file_path) as fd:
        for line in fd:
            if line == f"[{title}]\n":
                line = next(fd)
                if line == f'{key} = "{value}"\n':
                    found = True
                    break
    assert found is True
    # os.remove(sample_db_obj.file_path)
