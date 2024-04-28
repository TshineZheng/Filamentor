class MQTTConfig:
    def __init__(self, server, port, client_id, username, password):
        self.server = server
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password