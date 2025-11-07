from .config import PigeonTransitionsConfig
import argparse
import yaml
from pigeon.utils import setup_logging


def main():
    parser = argparse.ArgumentParser(
        prog="pigeon-transitions",
        description="The main state machine for controller the image acquisition system.",
    )
    parser.add_argument("config", type=str)
    parser.add_argument(
        "-g",
        "--graph",
        type=str,
        help="Instead of running, save a graph of the state machine to the specified file.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="The STOMP message broker to connect to.",
    )
    parser.add_argument(
        "--port", type=int, default=61616, help="The STOMP port to connect to."
    )
    parser.add_argument(
        "--username",
        type=str,
        help="The username to use when connecting to the STOMP server.",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="The password to use when connecting to the STOMP server.",
    )

    args = parser.parse_args()

    config = PigeonTransitionsConfig.load_file(args.config)

    setup_logging()

    machine = config.root(config=config.machines, **config.machines.config)

    if args.graph:
        machine.save_graph(args.graph)
    else:
        machine.add_client(
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password,
        )
        machine._run()


if __name__ == "__main__":
    main()
