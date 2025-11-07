import os


def kubernetes() -> bool:
    # 1) service‐account token (default mount in every Pod)
    if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
        return True
    # 2) built‐in K8s env var
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return True
    return False
