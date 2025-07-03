from client.cli import get_user_input, parse_arguments
from client.core.runner import run_client


def main():
    args = parse_arguments()

    client_id = get_user_input()

    run_client(args.server_ip, args.server_port, client_id)


if __name__ == "__main__":
    main()
