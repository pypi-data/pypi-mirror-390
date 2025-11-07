NONSESSION_APPLOGS = "nonsession-applogs"
SAILFISH_DEFAULT_GRAPHQL_ENDPOINT = "https://api-service.sailfishqa.com/graphql/"
SAILFISH_TRACING_HEADER = "X-Sf3-Rid"
FUNCSPAN_OVERRIDE_HEADER = "X-Sf3-FunctionSpanCaptureOverride"
PARENT_SESSION_ID_HEADER = "X-Sf4-Prid"  # Parent Recording ID (stripped from outbound, internal only)

# Byte-string constants for fast header matching (avoid decode/dict overhead)
SAILFISH_TRACING_HEADER_BYTES = SAILFISH_TRACING_HEADER.encode("ascii").lower()  # b"x-sf3-rid"
FUNCSPAN_OVERRIDE_HEADER_BYTES = FUNCSPAN_OVERRIDE_HEADER.encode("ascii").lower()  # b"x-sf3-functionspancaptureoverride"
PARENT_SESSION_ID_HEADER_BYTES = PARENT_SESSION_ID_HEADER.encode("ascii").lower()  # b"x-sf4-prid"
