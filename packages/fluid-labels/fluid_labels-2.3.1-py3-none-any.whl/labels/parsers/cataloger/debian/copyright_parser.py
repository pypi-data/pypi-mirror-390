import re
from pathlib import Path
from typing import TextIO

from labels.model.file import Location
from labels.model.resolver import Resolver
from labels.utils.licenses.validation import validate_licenses


def get_licenses_from_copyright(
    resolver: Resolver, db_location: Location, package_name: str
) -> list[str]:
    copyright_reader, copyright_location = _fetch_copyright_contents(
        resolver, db_location, package_name
    )

    if copyright_reader is not None and copyright_location is not None:
        licenses_strs = _parse_licenses_from_copyright(copyright_reader)
        return validate_licenses(licenses_strs)

    return []


def _fetch_copyright_contents(
    resolver: Resolver,
    db_location: Location,
    package_name: str,
) -> tuple[TextIO | None, Location | None]:
    copyright_path = Path("/usr/share/doc").joinpath(package_name, "copyright")
    location = resolver.relative_file_path(db_location, str(copyright_path))

    if not location:
        return None, None

    reader = resolver.file_contents_by_location(location)

    return reader, location


def _parse_licenses_from_copyright(reader: TextIO) -> list[str]:
    result = []
    for raw_line in reader:
        line = raw_line.rstrip("\n")
        if value := _find_license_clause(r"^License: (?P<license>.*)", "license", line):
            result.append(value)
        if value := _find_license_clause(
            r"/usr/share/common-licenses/(?P<license>[0-9A-Za-z_.\-]+)",
            "license",
            line,
        ):
            result.append(value)

    return list(set(result))


def _find_license_clause(pattern: str, value_group: str, line: str) -> str | None:
    match = re.search(pattern, line)
    if match:
        license_value = match.group(value_group)
        return _ensure_is_single_license(license_value)
    return None


def _ensure_is_single_license(candidate: str) -> str | None:
    candidate = candidate.strip()
    if " or " in candidate or " and " in candidate:
        return None
    if candidate and candidate.lower() != "none":
        return candidate.rstrip(".")
    return None
