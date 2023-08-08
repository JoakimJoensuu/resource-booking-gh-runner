from typing import Callable, NoReturn, cast

from booking_client.cli import main_arg_parser
from booking_client.interactive_cli import interactive_cli_arg_parser

# TODO: Read configuration and environment


def entrypoint():
    interactive_cli_parser = interactive_cli_arg_parser()
    main_parser = main_arg_parser(interactive_cli_parser)

    args = vars(main_parser.parse_args())
    subcommand = cast(Callable[..., NoReturn], args.pop("func"))
    subcommand(**args)


if __name__ == "__main__":
    entrypoint()
