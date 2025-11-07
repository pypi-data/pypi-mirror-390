from rich.console import Console
from rich.tree import Tree
from btweak.helpers.cmdhandler import run_system_commands
from btweak.helpers.fixthings import fix_db_lck

console = Console()


def print_groups(tool_groups):
    tree = Tree("[=== [b u blue]All Tool Groups[/] ===]")
    for ind, i in enumerate(tool_groups, start=1):
        group = tree.add(f"{ind}. [b cyan]{i.name}[/]")
        group.add(f"[dim]{i.description}[/]")
        group.add(f"[yellow]{len(i.packages)} packages[/]")
    console.print(tree)
    print()


def print_specific_group_by_index(index: int, parser):
    group = parser.get_group_by_index(index)
    if group is None:
        console.print(f"[red]Error: Invalid index {index}[/]")
        return

    tree = Tree(f"[b u cyan]{group.name}[/]")
    tree.add(f"[dim]{group.description}[/]")

    packages_branch = tree.add(f"[yellow]{len(group.packages)} packages[/]")
    for i in group.packages:
        packages_branch.add(f"[green]{i.name}[/]").add(
            f"[dim]{i.description}[/]"
        )  # noqa

    console.print(tree)
    print()


def install_group(index: int, parser):
    pkgs = " ".join(i.name for i in parser.get_packages_by_index(index))
    fix_db_lck()

    run_system_commands(
        [
            "sudo pacman -Syy --noconfirm yay",
            "yay -Syy --noconfirm {}".format(pkgs),
        ]  # noqa
    )
