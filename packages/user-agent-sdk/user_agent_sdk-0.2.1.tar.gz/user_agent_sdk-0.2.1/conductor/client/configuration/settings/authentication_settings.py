class AuthenticationSettings:
    def __init__(self, key_id: str, key_secret: str, auth_url: str):
        self.key_id = key_id
        self.key_secret = key_secret
        self.auth_url = auth_url
