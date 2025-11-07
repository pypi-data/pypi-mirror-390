from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings


class Credentials(AuthenticationSettings):
    def __init__(self, client_id: str, client_secret: str, auth_url: str):
        super().__init__(client_id, client_secret)
        self.auth_url = auth_url
