from datetime import datetime, timezone


class Section:
    def __init__(self, name: str) -> None:
        self.name = name
        self._content: dict[str, str] = {}
        self._items_count = 0

    def __len__(self):
        return len(self._content)

    def set(self, key: str, value: str) -> None:
        self._content[key] = value
        self._items_count = len(self._content)

    def as_string(self) -> str:
        content = f"[{self.name}]\n"
        for k, v in self._content.items():
            content += f'{k} = "{v}"\n'

        return content


class INIFile:
    def __init__(
        self, db_name: str, filename: str, path: str | None = "tests/"
    ) -> None:
        self.db_name = db_name
        self.filename = filename
        self.file_path = f"{path}{filename}"
        self._sections: list[Section] = []
        with open(self.file_path, "w") as fd:
            self.fd = fd
            meta = Section("meta")
            meta.set("db_name", db_name)
            meta.set(
                "create_date_utc",
                str(datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)),
            )
            meta.set(
                "create_date_server", str(datetime.now().replace(microsecond=0))
            )
            self._sections.append(meta)
            _ = fd.write(meta.as_string())

    @property
    def sections(self) -> list[str]:
        return [n.name for n in self._sections]
