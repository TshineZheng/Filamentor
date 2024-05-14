class MQTTConfig:
    def __init__(self, server: str = None, port: int = 1883, client_id: str = 'Filamentor-MQTT', username: str = '', password: str = ''):
        self.server = server
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password

    @classmethod
    def from_dict(cls, json_data: dict):
        return cls(
                server=json_data['server'],
                port=json_data['port'],
                client_id=json_data['client_id'],
                username=json_data['username'],
                password=json_data['password']
            )
    

    def to_dict(self) -> dict:
        return {
            'server': self.server,
            'port': self.port,
            'client_id': self.client_id,
            'username': self.username,
            'password': self.password
        }
