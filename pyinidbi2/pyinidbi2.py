import os
from datetime import datetime, timezone

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0


class Section:
    def __init__(self, name: str) -> None:
        self.name = name
        self._content: dict[str, str] = {}

    def __len__(self):
        return len(self._content)

    def get(self, key: str) -> str | bool:
        try:
            return self._content[key]
        except KeyError:
            return False

    def keys(self) -> tuple[str, ...]:
        return tuple(self._content.keys())

    def set(self, key: str, value: str) -> None:
        self._content[key] = value

    def remove(self, key: str) -> bool:
        result = False
        try:
            _ = self._content.pop(key)
            result = True
        except KeyError:
            pass
        return result

    def as_string(self) -> str:
        content = f"[{self.name}]\n"
        if len(self._content) > 0:
            for k, v in self._content.items():
                content += f'{k}="{v}"\n'
        return content


class INIFile:
    def __init__(self, db_name: str, filename: str, path: str | None = "db/") -> None:
        self.version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
        self.db_name = db_name
        self.filename = filename
        self.file_path = f"{path}{filename}"
        self._sections: list[Section] = []
        if os.path.isfile(self.file_path):
            self._load()
            if len(self._sections) == 0:
                self._sections.append(self._add_meta())
        else:
            self._sections.append(self._add_meta())
        self._fd = open(self.file_path, "w")
        _ = self.write()

    def __del__(self) -> None:
        _ = self.write()
        self._fd.close()

    @property
    def sections(self) -> list[str]:
        return [n.name for n in self._sections if n.name != "meta"]

    @staticmethod
    def _list_to_section(lines: list[str]) -> Section:
        line = lines.pop(0)
        name = line[line.find("[") + 1 : line.find("]")]
        section = Section(name)

        for line in lines:
            idx = line.find("=")
            if idx != -1:
                key = line[:idx]
                value = line[idx + 1 :].strip("\n")
                section.set(key, value[1:-1])
        return section

    @staticmethod
    def get_time(*, utc: bool = True) -> str:
        if utc:
            return str(datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None))
        else:
            return str(datetime.now().replace(microsecond=0))

    def _add_meta(self) -> Section:
        meta = Section("meta")
        meta.set("db_name", self.db_name)
        meta.set("create_date_utc", self.get_time(utc=True))
        meta.set("create_date_server", self.get_time(utc=False))
        return meta

    def _load(self) -> None:
        sec_list: list[str] = []
        with open(self.file_path) as fd:
            for line in fd.readlines():
                if (line.find("[")) == 0:
                    if len(sec_list) > 0:
                        section = self._list_to_section(sec_list)
                        self._sections.append(section)
                        sec_list = sec_list[:0]
                sec_list.append(line)

        # handle data from last section that didn't get process before fd closed
        if len(sec_list) > 0:
            section = self._list_to_section(sec_list)
            self._sections.append(section)

    def get(self, name: str) -> Section | None:
        try:
            idx = self.sections.index(name)
            return self._sections[1:][idx]
        except ValueError:
            return None

    def add(self, section: Section) -> bool:
        try:
            idx = self.sections.index(section.name)
            self._sections[idx] = section
        except ValueError:
            self._sections.append(section)
        return self.write()

    def remove(self, name: str) -> bool:
        result = False
        section = self.get(name)
        if section is not None:
            self._sections = [x for x in self._sections if x.name != name]
            result = True
        return result

    def as_string(self) -> str:
        output = ""
        for s in self._sections:
            output += s.as_string()
        return output

    def write(self, flush: bool = False) -> bool:
        result = False
        try:
            _ = self._fd.seek(0)
            _ = self._fd.truncate()
            for section in self._sections:
                _ = self._fd.write(section.as_string())
            if flush:
                self._fd.flush()
            result = True
        except (FileNotFoundError, PermissionError):
            pass
        return result

    def delete(self) -> bool:
        result = False
        try:
            self._fd.flush()
            os.remove(self.file_path)
            result = True
        except (FileNotFoundError, PermissionError):
            pass

        return result
