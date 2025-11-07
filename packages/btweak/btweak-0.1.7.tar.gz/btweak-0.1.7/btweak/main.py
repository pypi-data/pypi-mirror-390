import argparse
from importlib import resources
from btweak.helpers.fixthings import fix_berserkarch_gpg_pacman, fix_db_lck
from btweak.helpers.toolhandler import (
    print_groups,
    print_specific_group_by_index,
    install_group,
)  # noqa
from btweak.helpers.fileparser import ToolGroupParser, ContainersGroupParser
from btweak.helpers.dockerhandler import ContainerDisplay


def parse_args():
    parser = argparse.ArgumentParser(
        prog="btweak", description="Berserk Arch Tweak Tool"
    )

    subcmd = parser.add_subparsers(dest="command", required=True)

    # fix things in berserkarch
    fix_subcmd = subcmd.add_parser("fix", help="Fix things in berserkarch")
    fix_subcmd.add_argument(
        "-g", "--gpg", action="store_true", help="Fix pacman gpg key issue"
    )
    fix_subcmd.add_argument(
        "--db-lck",
        action="store_true",
        help="Fix pacman -- unable to lock database error",
    )

    # tools group
    tools_subcmd = subcmd.add_parser(
        "tools", help="List, install and remove tools"
    )  # noqa
    tools_subcmd.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all tools categories and profiles",
    )
    tools_subcmd.add_argument(
        "-g", "--group", type=int, help="List info about a specific group"
    )
    tools_subcmd.add_argument(
        "-i", "--install", type=int, help="Install a specific group"
    )

    # docker containers for systems and tools
    docker_subcmd = subcmd.add_parser(
        "docker", help="List and manage docker images for systems and tools"
    )
    docker_subcmd.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all available options",
    )
    docker_subcmd.add_argument(
        "-g", "--group", type=int, help="List info about a specific group"
    )
    docker_subcmd.add_argument(
        "-c",
        "--category",
        type=int,
        help="List containers in a specific category. Must be used with the --group (-g) flag.",  # noqa
    )
    docker_subcmd.add_argument(
        "-s", "--search", type=str, help="Search for available containers"
    )

    docker_subcmd.add_argument(
        "-r", "--run", type=str, help="Run any available containers"
    )
    docker_subcmd.add_argument(
        "-t",
        "--terminal",
        action="store_true",
        help="Run container in separate terminal. Must be used with --run (-r) flag.",  # noqa
    )

    return parser, parser.parse_args()


def main():
    parser, args = parse_args()

    match args.command:
        case "fix":
            if args.gpg:
                fix_berserkarch_gpg_pacman()
            elif args.db_lck:
                fix_db_lck()
            else:
                parser.parse_args(["fix", "--help"])
        case "tools":
            toolsp = ToolGroupParser(
                resources.files("btweak.data").joinpath("tools.yaml")
            )
            groups = toolsp.parse()
            if args.list:
                print_groups(groups)
            elif args.group:
                print_specific_group_by_index(args.group, toolsp)
            elif args.install:
                install_group(args.install, toolsp)
            else:
                parser.parse_args(["tools", "--help"])

        case "docker":
            dockerp = ContainersGroupParser(
                resources.files("btweak.data").joinpath("docker.yaml")
            )
            dockerp.parse()
            display = ContainerDisplay(dockerp)

            if args.group and args.category:
                display.show_category(args.group, args.category)
            elif args.group:
                display.show_group(args.group)
            elif args.category:
                print(
                    "Error: The --category (-c) flag must be used with the --group (-g) flag."  # noqa
                )
                parser.parse_args(["docker", "--help"])
            elif args.list:
                display.show_all_groups()
            elif args.search:
                display.search(args.search)
            elif args.run:
                if args.terminal:
                    display.run(args.run, True)
                else:
                    display.run(args.run)
            elif args.terminal:
                print(
                    "Error: The --terminal (-t) flag must be used with the --run (-r) flag."  # noqa
                )
                parser.parse_args(["docker", "--help"])
            else:
                parser.parse_args(["docker", "--help"])
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
