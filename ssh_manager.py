#! /usr/bin/env python3
import subprocess
import os
import argparse
import json
from datetime import datetime

EXP_FILE = "expiration_dates.json"


def generate_keys(key_type: str, key_name: str, comment=None):
    """
    summary: generates ssh key pairs. If rsa key is specified, it will generate a 4096 bit key by default

    Arguments:
            key_type: accepted arguments - rsa, ed25519
            key_name: custom name of file, if left blank default name will be applied
    """
    creation_date = generate_timestamp()[0]
    if key_type == "rsa":
        key_name = f"id_rsa_{key_name}_{creation_date}"
    else:
        key_name = f"id_ed25519_{key_name}_{creation_date}"

    key_path = f"{get_ssh_dir()}/{key_name}"

    key_size = "4096"

    command_rsa = [
        "ssh-keygen",
        "-t",
        key_type,
        "-b",
        key_size,
        "-f",
        key_path,
    ]

    command_ed25519 = ["ssh-keygen", "-t", key_type, "-f", key_path]

    if key_type == "rsa":
        result = subprocess.run(
            command_rsa, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr)
    elif key_type == "ed25519":
        result = subprocess.run(
            command_ed25519, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            print("")
        else:
            print(result.stderr)
    else:
        print("Please specify key type")

    update_ssh_config(key_name)


def generate_timestamp():
    timestamp = datetime.now().replace(microsecond=0)
    formatted_timestamp = timestamp.strftime("%Y-%m-%d")
    # Split timestamp to isolate each element
    split_timestamp = formatted_timestamp.split("-")
    # Get current year
    current_year = split_timestamp[0]
    # Get current month
    current_month = split_timestamp[1]
    # Get current day
    current_day = split_timestamp[2]
    # Calculate expiration year, adding one for a 12 month expiration
    expiration_year = int(current_year) + 1
    expiration_date = f"{str(expiration_year)}-{current_month}-{current_day}"

    return formatted_timestamp, expiration_date


def update_expiration_file(
    formatted_timestamp: str, expiration_date: str, key_name: str
):
    try:
        with open(f"{get_ssh_dir()}/{EXP_FILE}", "r", encoding="utf-8") as ex_file:
            data = json.load(ex_file)
            data["Keys"].update(
                dict(
                    {
                        key_name: {
                            "dateOfCreation": formatted_timestamp,
                            "expiration": expiration_date,
                        }
                    }
                )
            )
            with open(f"{get_ssh_dir()}/{EXP_FILE}", "w", encoding="utf-8") as updated:
                json.dump(data, updated, indent=4)
            print(
                f"\nKey created on {formatted_timestamp}. Key will expire on {expiration_date}"
            )
    except FileNotFoundError:
        with open(f"{get_ssh_dir()}/{EXP_FILE}", "w", encoding="utf-8") as ex_file:
            data = {
                "Keys": {
                    key_name: {
                        "dateOfCreation": formatted_timestamp,
                        "expires": expiration_date,
                    }
                }
            }
            json.dump(data, ex_file, indent=4)
            print(
                f"\n----------\nExpiration Date file was not found, so it was created with the following path: {get_ssh_dir()}/{EXP_FILE}"
            )


def read_expiration_file() -> dict:
    ssh_path = get_ssh_dir()
    with open(f"{ssh_path}/{EXP_FILE}", "r", encoding="utf-8") as ex_file:
        data = json.load(ex_file)
        return data


def prune_json() -> tuple[dict, bool]:
    data = read_expiration_file()
    current_keys = get_system_keys()
    keys_to_check = list(data["Keys"].keys())
    modified = False
    for key in keys_to_check:
        if f"{key}.pub" not in current_keys:
            data["Keys"].pop(key)
            modified = True
        else:
            continue

    return data, modified


def synchronize_json() -> tuple[dict, bool]:
    current_sys_keys = get_system_keys()
    ex_keys = read_expiration_file()
    timestamp = generate_timestamp()
    modified = False
    for i in current_sys_keys:
        if i.split(".")[0] not in ex_keys["Keys"].keys():
            ex_keys["Keys"].update(
                dict(
                    {
                        i.split(".")[0]: {
                            "dateOfCreation": timestamp[0],
                            "expiration": timestamp[1],
                        }
                    }
                )
            )
            modified = True
        else:
            continue
    return ex_keys, modified


def write_sync_changes():
    ssh_path = get_ssh_dir()
    data = (prune_json()[0], synchronize_json()[0])
    modified = (prune_json()[1], synchronize_json()[1])
    if modified[0]:
        with open(f"{ssh_path}/{EXP_FILE}", "w", encoding="utf-8") as ex_file:
            json.dump(data[0], ex_file, indent=4)
            print("Keys have been synchronized. Old keys have been removed.")
    if modified[1]:
        with open(f"{ssh_path}/{EXP_FILE}", "w", encoding="utf-8") as ex_file:
            json.dump(data[1], ex_file, indent=4)
            print("Keys have been synchronized. System keys added to database.")
    if not modified[0] and not modified[1]:
        print("Keys are already in sync.")


def get_ssh_dir() -> str:
    home = os.path.expanduser("~")
    ssh_dir = os.path.join(home, ".ssh")
    return ssh_dir


def update_ssh_config(key_name: str):
    to_update = input(
        "Would you like to add this Key to the SSH config? (y or n): "
    ).lower()
    if to_update == "y":
        # Prompt user for SSH Hostname entry in config file
        host = input("Enter SSH hostname: ")
        # Prompt user for username for config file
        user = input("Enter SSH username: ")
        # Fetch the path to .ssh
        ssh_dir = get_ssh_dir()
        # Format data to write to the config file
        data = f"Host {host}\n    HostName {host}\n    User {user}\n    IdentityFile {ssh_dir}/{key_name}\n"
        try:
            with open(f"{ssh_dir}/config", "a", encoding="utf-8") as config_file:
                config_file.write(data)
                # Generate timestamp
                date = generate_timestamp()
                # Get creation date
                creation = date[0]
                # Get expiration date
                expires = date[1]
                # Update expiration file
                update_expiration_file(
                    formatted_timestamp=creation,
                    expiration_date=expires,
                    key_name=key_name,
                )
        except FileNotFoundError as e:
            print(f"{e}")
    else:
        return None


def list_keys():
    # Get .ssh path
    # ssh_path = get_ssh_dir()
    # # Ensure the path exists
    # if os.path.exists(ssh_path):
    #     with os.scandir(ssh_path) as entries:
    #         # Get a list of the current .pub keys in the .ssh directory
    #         ssh_keys = [entry.name for entry in entries if ".pub" in entry.name]
    #         sorted_keys = sorted(ssh_keys, key=lambda x: os.path.getmtime(x))
    #         counter = 0
    #         print("----------")
    #         for key in sorted_keys:
    #             counter += 1
    #             print(f"\n\n{counter}. {key}\n\n----------")
    current_keys = read_expiration_file()
    counter = 0
    print("----------")
    for k, v in current_keys["Keys"].items():
        counter += 1
        print(
            f"\n\n{counter}: {k} Created On: {v.get('dateOfCreation')} | Expires on: {v.get('expiration')}\n\n----------"
        )


def get_system_keys() -> list[str]:
    ssh_path = get_ssh_dir()
    # Ensure the path exists
    if os.path.exists(ssh_path):
        with os.scandir(ssh_path) as entries:
            # Get a list of the current .pub keys in the .ssh directory
            ssh_keys = [entry.name for entry in entries if ".pub" in entry.name]
        return ssh_keys


def get_config_contents():
    ssh_dir = get_ssh_dir()
    with open(f"{ssh_dir}/config", "r", encoding="utf-8") as config_file:
        data = config_file.read()
        print(f"__________\n\n{data}\n__________\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate and manage SSH keys and SSH config."
    )
    # Default arguments for creating key pairs
    parser.add_argument(
        "-n", "--name", type=str, default=None, help="Unique name for the SSH key."
    )
    parser.add_argument(
        "-kt",
        "--key-type",
        type=str,
        default="rsa",
        help="The type of key to generate: currently accepts rsa and ed25519.",
    )
    # Arguments for viewing config file and listing current keys, as well as what they go to
    parser.add_argument(
        "-lc",
        "--list-config",
        action="store_true",
        help="List the current contents of the .ssh config file.",
    )
    parser.add_argument(
        "-l",
        "--list-keys",
        action="store_true",
        help="List current public SSH keys stored in .ssh directory as well as the expiration date. Expiration dates are set at 12 months by default.",
    )
    parser.add_argument(
        "-s",
        "--sync-keys",
        action="store_true",
        help="Check the current .ssh directy and prune expiration_date.json to match current keys.",
    )

    args = parser.parse_args()
    if args.list_keys:
        list_keys()
    elif args.list_config:
        get_config_contents()
    elif args.sync_keys:
        write_sync_changes()
    else:
        if args.name and args.key_type:
            generate_keys(key_name=args.name, key_type=args.key_type)
        else:
            print(
                "Provide --list-config, --list-keys, or provide -n (name of key) AND --key-type (type of SSH key) to generate a key."
            )


if __name__ == "__main__":
    main()
