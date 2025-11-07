import os
import socket

import requests

DEFAULT_CLUSTER_NAME = "UNKNOWN"

# ─── 1. ConfigMap (optional) ─────────────────────────────────


def get_from_config_map(path: str = "/etc/cluster-info/cluster-name"):
    """If you’ve mounted a ConfigMap at this path, read it."""
    try:
        with open(path, "r") as f:
            name = f.read().strip()
            if name:
                return name
    except IOError:
        pass


# ─── 2. Cloud Metadata ────────────────────────────────────────


def get_gke_cluster_name(timeout: float = 1.0):
    """GKE nodes automatically get a 'cluster-name' instance attribute."""
    try:
        resp = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/attributes/cluster-name",
            headers={"Metadata-Flavor": "Google"},
            timeout=timeout,
        )
        if resp.ok and resp.text:
            return resp.text
    except requests.RequestException:
        pass


def get_eks_cluster_name(timeout: float = 1.0):
    """EKS-backed EC2 instances are tagged 'eks:cluster-name'."""
    try:
        # 1) fetch IMDSv2 token
        token = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=timeout,
        ).text
        # 2) read the eks:cluster-name tag
        resp = requests.get(
            "http://169.254.169.254/latest/meta-data/tags/instance/eks:cluster-name",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=timeout,
        )
        if resp.ok and resp.text:
            return resp.text
    except requests.RequestException:
        pass


def get_aks_cluster_name(timeout: float = 1.0):
    """AKS nodes live in a VM RG named MC_<resourceGroup>_<clusterName>_<zone>."""
    try:
        resp = requests.get(
            "http://169.254.169.254/metadata/instance",
            params={"api-version": "2021-02-01", "format": "json"},
            headers={"Metadata": "true"},
            timeout=timeout,
        )
        if resp.ok:
            compute = resp.json().get("compute", {})
            rg = compute.get("resourceGroupName", "")
            parts = rg.split("_")
            if len(parts) >= 3:
                return parts[2]
    except requests.RequestException:
        pass


# ─── 3. Kubernetes API fallback ────────────────────────────────


def get_via_k8s_api(timeout: float = 1.0):
    """
    If you’re running in K8s and have in‑cluster RBAC, try:
      A) ClusterProperty CRD (KEP‑2149)
      B) Node labels on your own Pod’s node
    """
    try:
        from kubernetes import client, config
    except ImportError:
        return

    try:
        # load service account creds
        config.load_incluster_config()

        # A) ClusterProperty CRD
        co = client.CustomObjectsApi()
        props = co.list_cluster_custom_object(
            group="multicluster.k8s.io",
            version="v1alpha6",
            plural="clusterproperties",
        ).get("items", [])
        if props:
            name = props[0].get("spec", {}).get("clusterName")
            if name:
                return name

        # B) read this Pod → its Node → cluster label
        v1 = client.CoreV1Api()
        # Pod name = hostname in K8s
        pod_name = socket.gethostname()
        ns = (
            open("/var/run/secrets/kubernetes.io/serviceaccount/namespace")
            .read()
            .strip()
        )
        pod = v1.read_namespaced_pod(
            name=pod_name, namespace=ns, _request_timeout=timeout
        )
        node = v1.read_node(pod.spec.node_name, _request_timeout=timeout)
        labels = node.metadata.labels or {}
        for key in ("cluster.x-k8s.io/cluster-name", "topology.kubernetes.io/cluster"):
            if labels.get(key):
                return labels[key]
    except Exception:
        pass


# ─── 4. Aggregator ────────────────────────────────────────────


def get_cluster_name():
    for fn in (
        get_from_config_map,
        get_gke_cluster_name,
        get_eks_cluster_name,
        get_aks_cluster_name,
        get_via_k8s_api,
    ):
        try:
            name = fn()
            if name:
                return name
        except Exception:
            continue
    return DEFAULT_CLUSTER_NAME
