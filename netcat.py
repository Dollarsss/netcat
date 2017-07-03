import socket
import argparse
import subprocess
import traceback


class netcat:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._init_args_parser()
        self.args = self.parser.parse_args()
        self.client_socket = None
        self.server_socket = None
        if self.args.l:
            self.listen_mode()
        elif self.args.c:
            self.client_mode()

    def _init_args_parser(self):
        self.parser.add_argument('-l', help='listen mode', required=False, action='store_true')
        self.parser.add_argument('-e', help='execute command', required=False, action='store_true')
        self.parser.add_argument('-a', help='address', required=False, default='127.0.0.1')
        self.parser.add_argument('-p', type=int, help='port', required=False)
        self.parser.add_argument('-u', help='upload file', required=False)
        self.parser.add_argument('-c', help='client mode', required=False, action='store_true')
        self.parser.add_argument('-f', help='select file upload', required=False)

    def run_command(self, command):
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            return output
        except Exception as err:
            error_message = traceback.format_exc()
            return error_message.encode('utf-8')

    def listen_mode(self):
        address = self.args.a
        port = self.args.p
        if not port or not address:
            print('not port or address')
        else:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((address, port))

            server_socket.listen(10)

            while True:
                client_socket, addr = server_socket.accept()
                self.client_socket = client_socket
                self.server_handler()

    def client_mode(self):
        address = self.args.a
        port = self.args.p
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((address, port))
        except Exception as err:
            print(err)
            return 0
        self.server_socket = server_socket
        self.client_handler()

    def client_handler(self):
        if self.args.f:
            file_name = self.args.f
            file_buffer = ''
            with open(file_name, 'r') as f:
                for line in f:
                    file_buffer += line
                file_buffer.encode('utf-8')
                f.close()
            self.server_socket.send(file_buffer.encode('utf-8'))
        elif self.args.e:
            while True:
                cmd = input()
                self.server_socket.send(cmd.encode('utf-8'))
                data = self.server_socket.recv(1024)
                print(data.decode('utf-8'))

    def server_handler(self):
        if self.client_socket:
            if self.args.e:
                while True:
                    cmd_buffer = self.get_client_input_buffer()
                    response = self.run_command(cmd_buffer)
                    self.client_socket.send(response)
            elif self.args.u:
                while True:
                    try:
                        file_buffer = self.get_client_input_buffer()
                        file_buffer = file_buffer.decode('utf-8')
                        dest = self.args.u
                        with open(dest, 'a') as f:
                            f.write(file_buffer)
                            f.close()
                    except Exception as err:
                        err_message = traceback.format_exc()
                        err_message.encode('utf-8')
                        self.client_socket.send(err_message)

    def get_client_input_buffer(self):
        client_input_buffer = b""
        client_input_buffer += self.client_socket.recv(1024)
        return client_input_buffer


test = netcat()