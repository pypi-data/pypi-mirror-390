import yaml
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Package:
    name: str
    description: str


@dataclass
class ToolGroup:
    name: str
    description: str
    packages: List[Package] = field(default_factory=list)


@dataclass
class Container:
    name: str
    description: str
    command: str
    run: str
    runtime_comments: Optional[List[str]] = None


@dataclass
class Category:
    name: str
    description: str
    containers: List[Container] = field(default_factory=list)


@dataclass
class ContainersGroup:
    name: str
    description: str
    containers: List[Container] = field(default_factory=list)
    categories: List[Category] = field(default_factory=list)


class ToolGroupParser:
    def __init__(self, yaml_file: str):
        self.yaml_file = yaml_file
        self.tool_groups: List[ToolGroup] = []

    def parse(self) -> List[ToolGroup]:
        with open(self.yaml_file, "r") as f:
            data = yaml.safe_load(f)

        for i in data:
            packages = []
            for pkg_data in i.get("packages", []):
                pkg = Package(
                    name=pkg_data["name"],
                    description=pkg_data["description"],
                )
                packages.append(pkg)

            tool_group = ToolGroup(
                name=i["name"],
                description=i["description"],
                packages=packages,
            )
            self.tool_groups.append(tool_group)

        return self.tool_groups

    def get_packages_by_index(self, index: int) -> Optional[List[Package]]:
        try:
            return self.tool_groups[index - 1].packages
        except IndexError:
            return None

    def get_group_by_index(self, index: int) -> Optional[ToolGroup]:
        try:
            return self.tool_groups[index - 1]
        except IndexError:
            return None

    def search_package(self, search_term: str) -> List[tuple]:
        results = []
        for group in self.tool_groups:
            for pkg in group.packages:
                if search_term.lower() in pkg.name.lower():
                    results.append((group.name, pkg))
        return results

    def get_all_packages(self) -> Dict[str, List[Package]]:
        return {group.name: group.packages for group in self.tool_groups}


class ContainersGroupParser:
    def __init__(self, yaml_file: str):
        self.yaml_file = yaml_file
        self.container_groups: List[ContainersGroup] = []

    def parse(self) -> List[ContainersGroup]:
        with open(self.yaml_file, "r") as f:
            data = yaml.safe_load(f)

        for i in data:
            container_group = ContainersGroup(
                name=i["name"],
                description=i["description"],
            )

            if "categories" in i:
                for cat_data in i["categories"]:
                    containers = []
                    for container_data in cat_data.get("containers", []):
                        container = Container(
                            name=container_data["name"],
                            description=container_data["description"],
                            command=container_data["command"],
                            run=container_data["run"],
                            runtime_comments=container_data.get(
                                "runtime_comments"
                            ),  # noqa
                        )
                        containers.append(container)

                    category = Category(
                        name=cat_data["name"],
                        description=cat_data["description"],
                        containers=containers,
                    )
                    container_group.categories.append(category)

            elif "containers" in i:
                for container_data in i["containers"]:
                    container = Container(
                        name=container_data["name"],
                        description=container_data["description"],
                        command=container_data["command"],
                        run=container_data["run"],
                        runtime_comments=container_data.get("runtime_comments"),  # noqa
                    )
                    container_group.containers.append(container)

            self.container_groups.append(container_group)

        return self.container_groups

    def get_containers_by_index(self, index: int) -> Optional[List[Container]]:
        try:
            group = self.container_groups[index - 1]
            if group.categories:
                all_containers = []
                for category in group.categories:
                    all_containers.extend(category.containers)
                return all_containers
            return group.containers
        except IndexError:
            return None

    def get_group_by_index(self, index: int) -> Optional[ContainersGroup]:
        try:
            return self.container_groups[index - 1]
        except IndexError:
            return None

    def search_container(self, search_term: str) -> List[tuple]:
        results = []
        for group in self.container_groups:
            for container in group.containers:
                if search_term.lower() in container.name.lower():
                    results.append((group.name, container))

            for category in group.categories:
                for container in category.containers:
                    if search_term.lower() in container.name.lower():
                        results.append((group.name, category.name, container))

        return results

    def get_all_containers(self) -> Dict[str, List[Container]]:
        result = {}
        for group in self.container_groups:
            all_containers = []
            all_containers.extend(group.containers)
            for category in group.categories:
                all_containers.extend(category.containers)
            result[group.name] = all_containers
        return result
