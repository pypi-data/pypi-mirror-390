from __future__ import annotations
import os, sys, socket, urllib.request, urllib.error

DEFAULT_TIMEOUT_S = 0.15

def _quick_http(url: str, headers: dict[str, str] | None = None, timeout: float = DEFAULT_TIMEOUT_S) -> tuple[int | None, str]:
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), "ok"
    except urllib.error.HTTPError as e:
        return e.code, "http_error"
    except Exception as e:
        return None, str(e)

def _is_cloud_instance() -> tuple[bool, str]:
    try:
        import urllib.request as _u
        tok_req = _u.Request(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"},
            method="PUT",
        )
        with _u.urlopen(tok_req, timeout=DEFAULT_TIMEOUT_S) as r:
            if r.getcode() == 200:
                return True, "aws-imdsv2"
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404, 405):
            return True, f"aws-imds({e.code})"
    except Exception:
        pass

    code, _ = _quick_http("http://169.254.169.254/latest/meta-data/")
    if code == 200:
        return True, "aws-imdsv1"

    code, _ = _quick_http(
        "http://169.254.169.254/computeMetadata/v1/instance/id",
        headers={"Metadata-Flavor": "Google"},
    )
    if code == 200:
        return True, "gcp-metadata"

    code, _ = _quick_http(
        "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
        headers={"Metadata": "true"},
    )
    if code == 200:
        return True, "azure-imds"

    return False, "no-cloud-metadata"

def _resolves_host_docker_internal() -> bool:
    try:
        socket.gethostbyname("host.docker.internal")
        return True
    except Exception:
        return False

# ---- globals to hold state ----
SF_IS_LOCAL_ENV: bool | None = None
SF_LOCAL_ENV_REASON: str | None = None


def _detect() -> tuple[bool, str]:
    """Detect environment once. Raise nothing; always return a tuple."""
    try:
        if any(os.getenv(k) for k in (
            "CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI",
            "BUILDkite", "TEAMCITY_VERSION", "JENKINS_URL", "DRONE"
        )):
            return (False, "ci-env-detected")

        on_cloud, cloud_reason = _is_cloud_instance()
        if on_cloud:
            return (False, cloud_reason)

        if sys.platform in ("darwin", "win32"):
            return (True, f"desktop-os:{sys.platform}")
        try:
            if "microsoft" in os.uname().release.lower() \
               or "microsoft" in open("/proc/version", "rt", errors="ignore").read().lower():
                return (True, "wsl-kernel")
        except OSError:
            pass

        if _resolves_host_docker_internal():
            return (True, "docker-desktop-dns")

        return (True, "no-cloud-metadata-and-no-ci")

    except Exception as e:
        # fallback: treat as local if detection fails
        return (True, f"detect-error:{type(e).__name__}")


def set_sf_is_local_flag() -> None:
    """
    Run detection once and store results in global variables.
    Call this at app startup. Never raises.
    """
    global SF_IS_LOCAL_ENV, SF_LOCAL_ENV_REASON
    try:
        SF_IS_LOCAL_ENV, SF_LOCAL_ENV_REASON = _detect()
    except Exception as e:
        # absolute fallback, so setup never fails
        SF_IS_LOCAL_ENV, SF_LOCAL_ENV_REASON = True, f"setup-error:{type(e).__name__}"


def sf_is_local_dev_environment() -> tuple[bool, str]:
    """
    Return cached values if sf_set_is_local_flag() has been called,
    otherwise run detection on the fly. Never raises.
    """
    global SF_IS_LOCAL_ENV, SF_LOCAL_ENV_REASON
    if SF_IS_LOCAL_ENV is None or SF_LOCAL_ENV_REASON is None:
        set_sf_is_local_flag()
    return SF_IS_LOCAL_ENV, SF_LOCAL_ENV_REASON
