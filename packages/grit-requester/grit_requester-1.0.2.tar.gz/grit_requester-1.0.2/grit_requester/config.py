class GritConfig:
    def __init__(
      self,
      base_url: str,
      auth_url: str,
      token: str,
      secret: str,
      context: str,
      token_header: str = "x-token",
      token_expiration_header: str = "x-expires"
    ):
        self.base_url = base_url
        self.auth_url = auth_url
        self.token = token
        self.secret = secret
        self.context = context
        self.token_header = token_header
        self.token_expiration_header = token_expiration_header

    def __repr__(self):
        return f"<GritConfig base_url={self.base_url!r} context={self.context!r}>"
