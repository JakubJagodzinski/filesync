import argparse


def get_user_input() -> str | None:
    print("Enter your id (pass empty if you want to use ip instead)")
    user_id = input("> ").strip()

    if user_id == "":
        user_id = None

    return user_id


def parse_arguments():
    parser = argparse.ArgumentParser(description="USP Client")

    parser.add_argument("--server-ip", type=str, help="Server IP address")
    parser.add_argument("--server-port", type=int, help="Server TCP port")

    return parser.parse_args()
