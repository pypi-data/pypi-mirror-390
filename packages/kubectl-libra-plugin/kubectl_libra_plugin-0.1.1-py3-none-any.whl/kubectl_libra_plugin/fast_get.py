from __future__ import annotations

import sys
import httpx
import argparse
import subprocess
from tabulate import tabulate
from datetime import datetime, UTC

now = datetime.now(UTC)


def format_age(since: str) -> str:
    since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
    if since_date.year < 1980:
        return ""  # old, probably not exist fallback epoch
    td = now - since_date
    total_seconds = int(td.total_seconds())
    
    # Just seconds
    if total_seconds < 60:
        return f"{total_seconds}s"
    
    # Just minutes
    if total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes}m"
        
    # Hours and minutes
    if total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if minutes == 0:
            return f"{hours}h"
        return f"{hours}h{minutes}m"
        
    # Days and hours
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    if hours == 0:
        return f"{days}d"
    return f"{days}d{hours}h"


def error(message: str, exitcode: int = 1):
    print(message, file=sys.stderr)
    raise SystemExit(exitcode)


def parse_resource_name(resource: str, name_filter: str):
    if (("/" in resource) and name_filter) or ("/" in name_filter):
        error("error: there is no need to specify a resource type as a separate argument when passing arguments in resource/name form (e.g. 'kubectl get resource/<resource_name>' instead of 'kubectl get resource resource/<resource_name>'")
    # either resource name_filter or resource/name_filter
    if "/" in resource:
        split = resource.split("/")
        if len(split) != 2:
            error("error: arguments in resource/name form may not have more than one slash")
        resource, name_filter = split
    return resource, name_filter


def kubectl_fet():
    argp = argparse.ArgumentParser()
    argp.add_argument("resource")
    argp.add_argument("name_filter", nargs='?', default='')
    argp.add_argument("-o", "--output", default="")
    argp.add_argument("-l", "--selector", default="")
    argp.add_argument("-n", "--namespace", default="default")
    argp.add_argument("-a", "--accurate", action="store_true", help="By default, fet greps in name instead of accurately matching. Add -a to match kubectl behavior or accurately finding the name.")
    argp.add_argument("--sort-by", default="")
    argp.add_argument("--show-kind", action="store_true")
    argp.add_argument("--show-labels", action="store_true")
    argp.add_argument("--ignore-not-found", action="store_true")
    args, extra = argp.parse_known_intermixed_args()
    namespace: str = args.namespace
    resource: str = args.resource
    selector: str = args.selector
    name_filter: str = args.name_filter
    resource, name_filter = parse_resource_name(resource, name_filter)
    if resource not in ("pod", "pods"):
        raise ValueError("Fast get only supports pod/pods, got %s" % resource)
    params = {"namespace": namespace}
    if name_filter:
        params["name_filter"] = name_filter
    if selector:
        params["label_selector"] = selector
    sorter = args.sort_by
    sorters = {
        "": (lambda pod: pod["name"]),
        ".metadata.name": (lambda pod: pod["name"]),
        "{.metadata.name}": (lambda pod: pod["name"]),
        ".metadata.creationTimestamp": (lambda pod: datetime.fromisoformat(pod["creation_timestamp"].replace('Z', '+00:00'))),
        "{.metadata.creationTimestamp}": (lambda pod: datetime.fromisoformat(pod["creation_timestamp"].replace('Z', '+00:00'))),
        ".spec.nodeName": (lambda pod: pod["node_name"]),
        "{.spec.nodeName}": (lambda pod: pod["node_name"]),
    }
    if sorter not in sorters:
        raise ValueError("Unsupported sorter for fast get", sorter)
    if args.output not in ["", "wide"]:
        raise ValueError("Unsupported output format for fast get, expected none or wide", args.output)
    with subprocess.Popen(["kubectl", *extra, "proxy", "--port", "0"], stdout=subprocess.PIPE) as proxy:
        try:
            with httpx.Client(timeout=10.0) as client:
                serve = proxy.stdout.readline().decode().split()[-1]
                resp = client.get(
                    f"http://{serve}/api/v1/namespaces/{namespace}/services/kubecon-socat:80/proxy/api/kubecon/pods",
                    params=params
                )
                code = resp.status_code
                result: dict = resp.json()
        finally:
            proxy.terminate()
    if code != 200:
        if result.get("kind") == "Status":
            error(f'Error from server ({result["reason"]}): {result["message"]}')
        else:
            error(f"Error from server: HTTP {code}")
    if args.accurate:
        pods = [pod for pod in result["pods"] if pod['name'] == name_filter]
    else:
        pods = result["pods"]
    if not args.ignore_not_found and not len(result):
        error(f'Error from server (NotFound): pods "{name_filter}" not found')
    pods = sorted(pods, key=sorters[sorter])
    table = []
    header = ["NAME", "READY", "STATUS", "RESTARTS", "AGE"]
    wide: bool = args.output == "wide"
    show_labels: bool = args.show_labels
    if wide:
        header.extend(["IP", "NODE"])
    if show_labels:
        header.append("LABELS")
    table.append(header)
    show_kind = args.show_kind
    for pod in pods:
        restime = format_age(pod["last_restart_timestamp"])
        row = [
            f"pod/{pod['name']}" if show_kind else pod['name'],
            f"{pod['num_ready_containers']}/{pod['num_total_containers']}",
            pod["status_phrase"],
            str(pod["num_restarts"]) + ((" (%s ago)" % restime) if restime else ""),
            format_age(pod["creation_timestamp"])
        ]
        if wide:
            row.extend((
                pod["pod_ip"],
                pod["node_name"]
            ))
        if show_labels:
            row.append(','.join(f"{k}={v}" for k, v in pod["labels"].items()))
        table.append(row)
    print(tabulate(table, tablefmt="plain"))
