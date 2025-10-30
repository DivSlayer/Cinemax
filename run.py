import argparse
import os


def main():
    used_servers = []
    commands = ['runserver', 'makemigrations', 'migrate']

    print('')
    for command in commands:
        print(f'{commands.index(command) + 1}: {command}')
    print('')
    command = input("Enter command: ")
    use_server = False
    command_dict = {}
    current_command = 1
    for used in commands:
        command_dict[str(current_command)] = used
        current_command += 1
    if command in command_dict.keys():
        command = command_dict[command]
        if command == "runserver":
            use_server = True
    elif command == '':
        raise "You should choose command"
    # Read Old Servers
    if use_server:
        with open('used_servers.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                used_servers.append(line.replace('\\n', ''))
        # Print Used Servers
        print('')
        for used in used_servers:
            print(f'{used_servers.index(used) + 1}: {used}')
        print('')
        server = input("Enter Server: ")
        server_dict = {}
        current = 1
        for used in used_servers:
            server_dict[str(current)] = used
            current += 1
        if server in server_dict.keys():
            server = server_dict[server]
        elif server == '':
            server = "127.0.0.1:8000"
        elif server not in used_servers:
            # Add New Server to used list
            with open('used_servers.txt', 'a+') as f:
                f.write("\n" + server)
        # Set Chosen Server
        with open('current_server.txt', 'w') as f:
            f.write(server.replace('\\n', '').replace(' ', '').replace('\n', ''))
    else:
        server = None
    os.system(
        f"cd venv/scripts && activate && cd .. && cd .. && python manage.py {command} {server} && cmd \k"
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        usage='%(prog)s <command> <server>',
        description='run server',
        epilog='python run.py command 192.168.0.1:80')
    parser.add_argument('command', type=str, help='Django Command')
    parser.add_argument('server', type=str, help="Server Address")
    args = parser.parse_args()

    # if not re.match(r"(\d{1,3}\.\d{1,3}).\d{1,3})", args.subnet) or any(a not in range(1,255) for a in map(int, args.subnet.split("."))):
    #     parser.error("This is not a valid subnet")
    return args.command, args.server


if __name__ == "__main__":
    main()
