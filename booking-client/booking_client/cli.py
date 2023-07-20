import argparse
import asyncio

from booking_client.commands import main

# TODO: client book machine_type_1 --wait
# TODO: client book machine_type_1 --workflow_id 345634
# TODO: client book machine_type_1 machine_type_1_identifier_123265324
# TODO: client cancel 123456
# TODO: client wait <booking_id>

# This command line tool shall go into interactive mode when `book --wait` or `wait` command is ran

def entry():
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="booking")
    parser.add_argument("--foo", action="store_true", help="foo help")
    subparsers = parser.add_subparsers(help="sub-command help", required=True)

    # create the parser for the "a" command
    parser_a = subparsers.add_parser("a", help="a help")
    parser_a.add_argument("bar", type=int, help="bar help")

    # create the parser for the "b" command
    parser_b = subparsers.add_parser("b", help="b help")
    parser_b.add_argument("--baz", choices="XYZ", help="baz help")

    # parse some argument lists
    args = parser.parse_args()

    print(args)

    asyncio.run(main())
    print("ASdD")
    # TODO: When running book with --wait, prevent accidental SIGINT
    # TODO: To receive notifications https://stackoverflow.com/a/51610341/12820664
    # TODO: Argcomplete https://stackoverflow.com/a/15289025/12820664
