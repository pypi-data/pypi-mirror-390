import os
from typing import List, Optional

from ...request_interceptor import get_domains_to_not_propagate_headers_to
from .utils import init_fast_network_tracking
from .requests import patch_requests
from .aiohttp import patch_aiohttp
from .httpx import patch_httpx
from .httpcore import patch_httpcore
from .http_client import patch_http_client
from .urllib_request import patch_urllib_request
from .httplib2 import patch_httplib2
from .pycurl import patch_pycurl
from .niquests import patch_niquests
from .curl_cffi import patch_curl_cffi
from .tornado import patch_tornado
from .treq import patch_treq

# from .aioh2            import patch_aioh2           # Asynchronous HTTP/2 client, no clear extension hooks
# from .http_prompt      import patch_http_prompt     # CLI HTTP client, minimal public API
# from .mureq            import patch_mureq           # Specialized crawler client, little documentation
# from .reqboost         import patch_reqboost        # High-performance batch client, docs scarce
# from .impit            import (patch_impit)         # Used by Crawlee's ImpitHttpClient
# from .h11              import patch_h11             # Low-level HTTP/1.1 protocol library
# from .aioquic          import patch_aioquic         # QUIC/HTTP-3 client, no standard headers API
# from .qh3              import patch_qh3             # Experimental HTTP/3 client, no docs found


def patch_all_http_clients(
    domains_to_not_propagate_headers_to: Optional[List[str]] = None,
):
    # Enable Python-level header injection (ULTRA-FAST: <100ns)
    # This disables C-level header injection (291µs overhead) and lets Python patches handle it
    os.environ["SF_PYTHON_HEADER_INJECTION"] = "0"

    # Initialize fast C-based network tracking
    # NOTE: When LD_PRELOAD is active (_sfteepreload), this only initializes the Python senders
    # The actual socket capture is done by _sfteepreload automatically
    init_fast_network_tracking()

    # Send domains mutation ONCE before patching (not from within each patch function)
    if domains_to_not_propagate_headers_to:
        domains_to_not_propagate_headers_to = get_domains_to_not_propagate_headers_to(
            domains_to_not_propagate_headers_to
        )

    # ULTRA-FAST Python-level header injection (<100ns)
    # Enable core libraries that cover 95% of use cases:

    # requests covers: requests → urllib3 → http.client (entire stack!)
    patch_requests(domains_to_not_propagate_headers_to)

    # aiohttp for async HTTP (standalone stack)
    patch_aiohttp(domains_to_not_propagate_headers_to)

    # Additional libraries (enable if needed):
    patch_http_client(domains_to_not_propagate_headers_to)  # Covered by requests
    patch_urllib_request(domains_to_not_propagate_headers_to)  # Covered by requests
    patch_httplib2(domains_to_not_propagate_headers_to)
    patch_httpx(domains_to_not_propagate_headers_to)
    patch_httpcore(domains_to_not_propagate_headers_to)
    patch_pycurl(domains_to_not_propagate_headers_to)
    patch_treq(domains_to_not_propagate_headers_to)
    patch_tornado(domains_to_not_propagate_headers_to)
    patch_curl_cffi(domains_to_not_propagate_headers_to)
    patch_niquests(domains_to_not_propagate_headers_to)

    # # Lesser-used libraries
    # patch_impit(domains_to_not_propagate_headers_to)
    # patch_aioh2(domains_to_not_propagate_headers_to)
    # patch_http_prompt(domains_to_not_propagate_headers_to)
    # patch_mureq(domains_to_not_propagate_headers_to)
    # patch_reqboost(domains_to_not_propagate_headers_to)
    # patch_h11(domains_to_not_propagate_headers_to)
    # patch_aioquic(domains_to_not_propagate_headers_to)
    # patch_qh3(domains_to_not_propagate_headers_to)
