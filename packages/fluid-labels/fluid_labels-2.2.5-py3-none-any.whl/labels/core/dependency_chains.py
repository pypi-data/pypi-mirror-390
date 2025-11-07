from labels.model.file import DependencyChain
from labels.model.package import Package, PackageType
from labels.model.relationship import Relationship


def calculate_dependency_paths_for_packages(
    packages: list[Package],
    relationships: list[Relationship],
) -> list[Package]:
    rel_map = build_relationship_map(relationships)

    package_names_cache = {pkg.id_: f"{pkg.name}@{pkg.version}" for pkg in packages}

    for pkg in packages:
        if pkg.type != PackageType.NpmPkg:
            continue
        for location in pkg.locations:
            node_id = f"{pkg.id_}@{location.location_id()}"
            chains = find_all_paths_to_top_level(
                node_id, rel_map, package_names_cache, pkg.name, pkg.version
            )
            location.dependency_chains = chains

    return packages


def build_relationship_map(relationships: list[Relationship]) -> dict[str, list[str]]:
    rel_map: dict[str, list[str]] = {}
    for rel in relationships:
        if rel.type.value == "dependency-of":
            if rel.from_ not in rel_map:
                rel_map[rel.from_] = []
            rel_map[rel.from_].append(rel.to_)
    return rel_map


def find_all_paths_to_top_level(
    node_id: str,
    rel_map: dict[str, list[str]],
    package_names_cache: dict[str, str],
    current_name: str,
    current_version: str,
) -> list[DependencyChain]:
    top_parent_to_path: dict[str, list[str]] = {}

    def _convert_ids_to_names(path_ids: list[str]) -> list[str]:
        path_names = []
        for idx, id_str in enumerate(path_ids):
            pkg_id = id_str.split("@")[0]
            pkg_name_version = package_names_cache.get(pkg_id, pkg_id)

            if idx == len(path_ids) - 1:
                path_names.append(f"{current_name}@{current_version}")
            else:
                path_names.append(pkg_name_version)
        return path_names

    def dfs(current_id: str, path_ids: list[str], visited: set[str]) -> None:
        if current_id in visited:
            return

        new_visited = visited | {current_id}
        parents = rel_map.get(current_id, [])

        if not parents:
            top_pkg_id = path_ids[0].split("@")[0]
            top_pkg_name_version = package_names_cache.get(top_pkg_id, "")
            top_parent_key = top_pkg_name_version if top_pkg_name_version else top_pkg_id

            path_names = _convert_ids_to_names(path_ids)

            if top_parent_key not in top_parent_to_path or len(path_names) < len(
                top_parent_to_path[top_parent_key]
            ):
                top_parent_to_path[top_parent_key] = path_names

            return

        for parent_id in parents:
            dfs(parent_id, [parent_id, *path_ids], new_visited)

    dfs(node_id, [node_id], set())

    if not top_parent_to_path:
        return [
            DependencyChain(
                depth=0,
                chain=[f"{current_name}@{current_version}"],
            )
        ]

    unique_chains = list(top_parent_to_path.values())
    return [DependencyChain(depth=len(chain) - 1, chain=chain) for chain in unique_chains]
