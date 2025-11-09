import hvac


class VaultClient():
    client = None
    VAULT_ROLE_ID = None
    VAULT_SECRET_ID = None

    def __init__(self, env, readFromEnviroment):
        print("Setting up vault")
        VAULT_URL = readFromEnviroment(
            env=env,
            envVarName="APIAPP_VAULT_URL",
            defaultValue=None,
            acceptableValues=None,
            nullValueAllowed=False
        )
        print(" VAULT_URL:", VAULT_URL)
        self.VAULT_ROLE_ID = readFromEnviroment(
            env=env,
            envVarName="APIAPP_VAULT_ROLE_ID",
            defaultValue=None,
            acceptableValues=None,
            nullValueAllowed=False
        )
        self.VAULT_SECRET_ID = readFromEnviroment(
            env=env,
            envVarName="APIAPP_VAULT_SECRET_ID",
            defaultValue=None,
            acceptableValues=None,
            nullValueAllowed=False
        )

        self.client = None
        if VAULT_URL != "MOCK":
            self.client = hvac.Client(url=VAULT_URL)
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Vault using the AppRole credentials."""
        if self.client is None:
            raise Exception('Vault client is not initialized - is this a mock instance?')
        auth_response = self.client.auth.approle.login(
            role_id=self.VAULT_ROLE_ID,
            secret_id=self.VAULT_SECRET_ID
        )
        if not self.client.is_authenticated():
            raise Exception("Failed to authenticate with Vault")
        print(" ✅ Authenticated with Vault")

    def _ensure_authenticated(self):
        if not self.client.is_authenticated():
            print("Token expired, re-authenticating...")
            self._authenticate()  # re-login via role_id + secret_id

    def get_secret(self, ref) -> str:
        if self.client is None:
            # If we don't have a client it is a mock instance so just return the full secret ref
            return ref
        try:
            path, field = ref.rsplit(":", 1)
        except ValueError:
            raise ValueError("Invalid secret reference. Expected format: '<path>:<field>'")
        self._ensure_authenticated()

        try:
            result = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point="kv"
            )
            data = result["data"]["data"]
            return data[field]
        except hvac.exceptions.InvalidPath:
            raise KeyError(f"Secret not found at path: {path}")
        except KeyError:
            raise KeyError(f"Field '{field}' not found in secret at {path}")
        except hvac.exceptions.Forbidden:
            raise KeyError(f"no access to secret: {path}:{field}")
