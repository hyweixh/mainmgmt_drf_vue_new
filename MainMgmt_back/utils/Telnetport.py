import telnetlib


class TelnetClient:
    def __init__(self, host, port, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection = None

    def connect(self):
        try:
           self.connection = telnetlib.Telnet(self.host, self.port, self.timeout)
           return True
        except Exception as e:
           self.connection = None
           return False
    def send_command(self, command):
        if self.connection is not None:
            try:
                self.connection.write(command.encode('ascii') + b'\n')
                result = self.connection.read_until(b"command# ", self.timeout)
                return result.decode('ascii').strip()
            except Exception as e:
                print(f"Error sending command {command}: {e}")
                return None
        else:
            print("Not connected to Telnet server.")
            return None

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        # else:
        #     print("Not connected to Telnet server.")
# --------------- 调用该类 ----------------------------------------------
# client = TelnetClient('localhost', 3050)  # 替换为你的Telnet服务器的主机名和端口号
# res = client.connect()
# if res:
#     print('telnet成功')
# else:
#     print('telnet失败---')
# result = client.send_command('your command here')  # 替换为你要发送的命令
# print(result)
# client.disconnect()