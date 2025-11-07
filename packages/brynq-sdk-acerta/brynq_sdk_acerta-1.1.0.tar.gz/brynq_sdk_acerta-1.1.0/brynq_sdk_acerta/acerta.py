from typing_extensions import List
from typing import Literal, Optional, Union
import time

from .salaries import Salaries
from .cost_centers import CostCenters
from brynq_sdk_brynq import BrynQ
from .code_lists import CodeLists
from .agreements import Agreements
from .inservice import InService
from .company_cars import CompanyCars
from .employees import Employees
from .employer import Employer
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class Acerta(BrynQ):
    """
    Base class for interacting with the Acerta API.
    """

    # Default timeout in seconds for all requests
    TIMEOUT = 30

    def __init__(self, employers: Union[str, List], system_type: Optional[Literal['source', 'target']] = None, test_environment: bool = True, debug: bool = False):
        """
        Initialize the Acerta API client.

        Args:
            system_type (str): System type ('source' or 'target')
            debug (bool): Debug flag - if True uses test environment, if False uses production
        """
        super().__init__()

        # Compute environment-specific prefix once and reuse
        env_prefix = "a-" if test_environment else ""
        self.base_url = f"https://{env_prefix}api.acerta.be"

        # Extract credentials and configure OAuth2 session with automatic token renewal
        credentials = self.interfaces.credentials.get(
            system="acerta-acceptance",
            system_type=system_type,
        )
        data = credentials.get("data", {})
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")

        # Token endpoint (match test/prod like base_url)
        token_url = f"https://{env_prefix}signin.acerta.be/am/oauth2/access_token"

        # Store client credentials for reuse
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url

        # Create OAuth2 session using client credentials (Backend Application flow)
        client = BackendApplicationClient(client_id=self._client_id)
        oauth_session = OAuth2Session(client=client)

        # Fetch initial token
        token = oauth_session.fetch_token(
            token_url=self._token_url,
            client_id=self._client_id,
            client_secret=self._client_secret,
            include_client_id=True,
        )

        # Keep access_token attribute for backward compatibility
        self.access_token = token.get("access_token")

        # Attach default headers; Authorization is managed by OAuth2Session
        oauth_session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

        # Ensure token is valid before each request (client_credentials has no refresh_token)
        self._orig_request = oauth_session.request
        oauth_session.request = self._request_with_pre_expiry  # type: ignore[assignment]

        # Use the OAuth2 session for all requests
        self.session = oauth_session
        self.session.timeout = self.TIMEOUT  # type: ignore[attr-defined]
        self._employer_ids = employers if isinstance(employers, List) else [employers]
        self._employee_ids = set()
        self._agreement_ids = set()

        # Set debug mode
        self.debug = debug

        # Initialize resource classes
        self.agreements = Agreements(self)
        self.inservice = InService(self)
        self.cost_centers = CostCenters(self)
        self.code_lists = CodeLists(self)
        self.employees = Employees(self)
        self.employers = Employer(self)
        self.salaries = Salaries(self)
        self.company_cars = CompanyCars(self)

    def _ensure_valid_token(self):
        """Ensure the OAuth token exists and is not about to expire."""
        tok = getattr(self.session, "token", {}) or {}
        expires_at = tok.get("expires_at")
        # Refresh if missing or expiring within 30 seconds
        if not expires_at or (expires_at - time.time()) < 30:
            new_token = self.session.fetch_token(
                token_url=self._token_url,
                client_id=self._client_id,
                client_secret=self._client_secret,
                include_client_id=True,
            )
            self.access_token = new_token.get("access_token")

    def _request_with_pre_expiry(self, method, url, **kwargs):
        self._ensure_valid_token()
        return self._orig_request(method, url, **kwargs)
