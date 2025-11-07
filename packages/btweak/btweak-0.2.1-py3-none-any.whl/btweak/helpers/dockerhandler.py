from rich.console import Console
from rich.tree import Tree
from btweak.helpers.cmdhandler import run_system_commands
from rich import print


class ContainerDisplay:
    def __init__(self, parser, console=None):
        self.parser = parser
        self.console = console or Console()

    def show_all_groups(self):
        main_tree = Tree("[bold blue]═══ Container Groups ═══[/]")

        for idx, group in enumerate(self.parser.container_groups, start=1):
            group_branch = main_tree.add(f"[bold cyan]{idx}. {group.name}[/]")
            group_branch.add(f"[dim italic]{group.description}[/]")

            if hasattr(group, "categories") and group.categories:
                total_containers = sum(
                    len(cat.containers) for cat in group.categories
                )  # noqa
                group_branch.add(
                    f"[yellow]{len(group.categories)} categories, {total_containers} total containers[/]"  # noqa
                )

                categories_branch = group_branch.add(
                    "[bold magenta]Categories:[/]"
                )  # noqa
                for cat_idx, category in enumerate(group.categories, start=1):
                    cat_branch = categories_branch.add(
                        f"[magenta]{cat_idx}. {category.name}[/] [dim]({len(category.containers)} containers)[/]"  # noqa
                    )
                    cat_branch.add(f"[dim italic]{category.description}[/]")

            elif hasattr(group, "containers") and group.containers:
                containers_branch = group_branch.add(
                    f"[yellow]{len(group.containers)} containers available[/]"
                )
                for container in group.containers:
                    containers_branch.add(f"[green]▸ {container.name}[/]")

        self._print_tree(main_tree)

    def show_group(self, index: int):
        group = self._get_group_or_error(index)
        if group is None:
            return

        main_tree = Tree(f"[bold blue]{group.name}[/]")
        main_tree.add(f"[dim italic]{group.description}[/]")

        if hasattr(group, "categories") and group.categories:
            self._add_categorized_containers(main_tree, group)
        elif hasattr(group, "containers") and group.containers:
            self._add_flat_containers(main_tree, group)

        self._print_tree(main_tree)

    def show_category(self, group_index: int, category_index: int):
        group = self._get_group_or_error(group_index)
        if group is None:
            return

        if not (hasattr(group, "categories") and group.categories):
            self._show_error(
                f"The selected group '{group.name}' does not contain any categories."  # noqa
            )
            return

        category = self._get_category_or_error(group, category_index)
        if category is None:
            return

        main_tree = Tree(
            f"[bold magenta]Category: {category.name}[/] [dim]from Group:[/] [bold blue]{group.name}[/]"  # noqa
        )
        main_tree.add(f"[dim italic]{category.description}[/]")
        main_tree.add(
            f"[yellow]Listing {len(category.containers)} container(s)[/]"
        )  # noqa

        for idx, container in enumerate(category.containers, start=1):
            self._add_container_details(main_tree, container, f"{idx}. ")

        self._print_tree(main_tree)

    def search(self, search_term: str):
        results = self.parser.search_container(search_term)

        if not results:
            tree = Tree(f"[bold yellow]Search: '{search_term}'[/]")
            tree.add("[dim]No results found[/]")
            self._print_tree(tree)
            return

        tree = Tree(f"[bold cyan]Search Results for '{search_term}'[/]")
        tree.add(f"[yellow]Found {len(results)} container(s)[/]")

        for result in results:
            container = result[-1]
            location = self._format_result_location(result)

            result_branch = tree.add(f"[green]{container.name}[/]")
            result_branch.add(location)
            self._add_container_details(result_branch, container, prefix="")

        self._print_tree(tree)

    def run(self, search_term: str, terminal: bool = False):
        results = self.parser.search_container(search_term)

        if not results:
            tree = Tree(f"[bold yellow]Search: '{search_term}'[/]")
            tree.add("[dim]No results found[/]")
            self._print_tree(tree)
            return

        if len(results) == 1:
            container = results[0][-1]
            self._execute_container(container, terminal)
            return

        tree = Tree(f"[bold cyan]Multiple Results for '{search_term}'[/]")
        tree.add(f"[yellow]Found {len(results)} container(s)[/]")

        for result in results:
            container = result[-1]
            location = self._format_result_location(result)

            result_branch = tree.add(f"[green]{container.name}[/]")
            result_branch.add(location)
            self._add_container_details(result_branch, container, prefix="")

        self._print_tree(tree)

    def _get_group_or_error(self, index: int):
        group = self.parser.get_group_by_index(index)
        if group is None:
            self._show_error(
                f"Invalid index: {index}",
                f"Available indices: 1-{len(self.parser.container_groups)}",
            )
        return group

    def _get_category_or_error(self, group, category_index: int):
        try:
            return group.categories[category_index - 1]
        except IndexError:
            self._show_error(
                f"Category with index '{category_index}' not found in group '{group.name}'.",  # noqa
                f"Available indices for this group: 1 to {len(group.categories)}",  # noqa
            )
            return None

    def _add_categorized_containers(self, tree, group):
        total_containers = sum(len(cat.containers) for cat in group.categories)
        tree.add(
            f"[yellow]Total: {len(group.categories)} categories, {total_containers} containers[/]"  # noqa
        )

        for cat_idx, category in enumerate(group.categories, start=1):
            category_branch = tree.add(
                f"[bold magenta]{cat_idx}. {category.name}[/]"
            )  # noqa
            category_branch.add(f"[dim italic]{category.description}[/]")

            for idx, container in enumerate(category.containers, start=1):
                self._add_container_details(
                    category_branch, container, f"{cat_idx}.{idx}. "
                )

    def _add_flat_containers(self, tree, group):
        tree.add(f"[yellow]Total: {len(group.containers)} containers[/]")

        for idx, container in enumerate(group.containers, start=1):
            self._add_container_details(tree, container, f"{idx}. ")

    def _add_container_details(self, parent_branch, container, prefix=""):
        container_branch = parent_branch.add(
            f"[bold green]{prefix}{container.name}[/]"
        )  # noqa
        container_branch.add(f"[white]{container.description}[/]")

        commands_branch = container_branch.add("[bold cyan]Commands:[/]")
        commands_branch.add(f"[blue]Pull:[/] {container.command}")
        commands_branch.add(f"[yellow]Run:[/] {container.run}")

    def _format_result_location(self, result):
        if len(result) == 3:
            group_name, category_name, _ = result
            return f"[dim]Group: {group_name} → Category: {category_name}[/]"
        else:
            group_name, _ = result
            return f"[dim]Group: {group_name}[/]"

    def _execute_container(self, container, terminal):
        print(container.run)
        if container.runtime_comments:
            print("\n=== [b green]Runtime Information[/] ===")
            for i in container.runtime_comments:
                print(i)
            print("=== [b red]Runtime Information[/] ===\n")
        if terminal:
            run_system_commands(
                [f"kitty --hold tmux new-session {container.run}"]
            )  # noqa
        else:
            run_system_commands([f"{container.run}"])

    def _show_error(self, *messages):
        error_tree = Tree("[bold red]✗ Error[/]")
        for msg in messages:
            error_tree.add(msg)
        self._print_tree(error_tree)

    def _print_tree(self, tree):
        self.console.print()
        self.console.print(tree)
        self.console.print()
