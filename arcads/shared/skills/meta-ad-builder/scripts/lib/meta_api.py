"""
Shared Meta Marketing API helpers for the meta-ad-builder skill.

Distilled from the Ad Builder Agent deploy scripts: image/video upload,
video-processing polling, and ad creation with transient-error retry/backoff.

Credentials come from environment (load a .env first with python-dotenv):
  META_ACCESS_TOKEN   (required) — long-lived user/system token, ads_management scope
  META_AD_ACCOUNT_ID  (required) — with or without the act_ prefix
  META_API_VERSION    (optional) — Graph API version, default v23.0
"""

import base64
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlsplit

import requests

GRAPH_HOST = "graph.facebook.com"
_API_VERSION_RE = re.compile(r"v\d{1,3}\.\d{1,3}")
_AD_ACCOUNT_RE = re.compile(r"(act_)?\d{1,32}")
_NUMERIC_ID_RE = re.compile(r"\d{1,32}")
# Graph path segments: numeric IDs, act_ IDs, page usernames (letters, digits, dots,
# underscores) and edge names. Rejects "/", "?", "#", "%" and dot-only segments.
_SEGMENT_RE = re.compile(r"(?!\.+$)[A-Za-z0-9_.]{1,100}")
DEFAULT_TIMEOUT = 60


def _api_version():
    version = os.getenv("META_API_VERSION", "v23.0")
    if not _API_VERSION_RE.fullmatch(version):
        raise RuntimeError(f"META_API_VERSION must look like v23.0, got {version!r}")
    return version


API_VERSION = _api_version()
BASE_URL = f"https://{GRAPH_HOST}/{API_VERSION}"


def graph_url(*segments):
    """Build a Graph API URL, refusing segments that could change the path or host."""
    for seg in segments:
        if not _SEGMENT_RE.fullmatch(str(seg)):
            raise ValueError(f"Invalid Graph API path segment: {str(seg)[:60]!r}")
    return "/".join([BASE_URL, *map(str, segments)])


def is_graph_url(url):
    """True only for https URLs on graph.facebook.com (e.g. API paging links)."""
    try:
        parts = urlsplit(str(url))
        port = parts.port
    except ValueError:
        return False
    return parts.scheme == "https" and parts.hostname == GRAPH_HOST and port in (None, 443)


def numeric_id(value, label="ID"):
    value = str(value).strip()
    if not _NUMERIC_ID_RE.fullmatch(value):
        raise ValueError(f"{label} must be numeric, got {value[:60]!r}")
    return value


def get_access_token():
    token = os.getenv("META_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN not set — see check-meta-env.sh")
    return token


def auth_headers(token=None):
    """Send the token in the Authorization header, never in URLs (which get logged)."""
    return {"Authorization": f"Bearer {token or get_access_token()}"}


def normalize_ad_account(acct):
    acct = str(acct).strip()
    if not _AD_ACCOUNT_RE.fullmatch(acct):
        raise ValueError(f"Ad account ID must be digits or act_<digits>, got {acct[:60]!r}")
    return acct if acct.startswith("act_") else f"act_{acct}"


def get_ad_account_id():
    acct = os.getenv("META_AD_ACCOUNT_ID")
    if not acct:
        raise RuntimeError("META_AD_ACCOUNT_ID not set — see check-meta-env.sh")
    return normalize_ad_account(acct)


def resolve_output_dir(run_slug):
    """Resolve a per-run output directory.

    Honors OUTPUT_BASE (set by the gen-ai-core workspace); otherwise writes
    under ./outputs/meta-ads/ — both are gitignored, so account-specific ad
    IDs and pulled performance data never land in version control.
    """
    base = os.getenv("OUTPUT_BASE")
    root = Path(base) if base else Path("outputs/meta-ads")
    run_dir = root / run_slug
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def upload_image(path, name=None):
    """Upload an image to /adimages (base64). Returns the image hash."""
    path = Path(path)
    if not path.exists():
        print(f"  ERROR: image not found: {path}")
        return None
    with open(path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    url = graph_url(get_ad_account_id(), "adimages")
    resp = requests.post(
        url,
        headers=auth_headers(),
        data={
            "bytes": img_b64,
            "name": (name or path.stem)[:90],
        },
        timeout=120,
    )
    data = resp.json()
    if "images" in data:
        h = list(data["images"].values())[0].get("hash")
        print(f"  Uploaded image. hash={h}")
        return h
    print(f"  Upload error: {json.dumps(data, indent=2)[:500]}")
    return None


def upload_video(path):
    """Upload a video to /advideos (multipart). Returns the video_id."""
    path = Path(path)
    if not path.exists():
        print(f"  ERROR: video not found: {path}")
        return None
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  Uploading {path.name} ({size_mb:.1f} MB)...")
    url = graph_url(get_ad_account_id(), "advideos")
    with open(path, "rb") as f:
        files = {"source": (path.name, f, "video/mp4")}
        data = {"name": path.name}
        resp = requests.post(url, headers=auth_headers(), data=data, files=files, timeout=900)
    if resp.status_code != 200:
        print(f"  ERROR HTTP {resp.status_code}: {resp.text[:500]}")
        return None
    result = resp.json()
    if "error" in result:
        print(f"  ERROR uploading: {json.dumps(result['error'], indent=2)}")
        return None
    vid = result.get("id")
    print(f"  Video uploaded: {vid}")
    return vid


def wait_for_video_processing(video_id, max_wait=360):
    """Poll a video until processing completes. Returns a thumbnail URL.

    Meta rejects video-ad creation until the video is fully processed; the
    returned thumbnail is required by video_data.image_url.
    """
    print("  Waiting for video processing...")
    url = graph_url(numeric_id(video_id, "video_id"))
    for attempt in range(max_wait // 10):
        time.sleep(10)
        resp = requests.get(url, headers=auth_headers(), params={
            "fields": "status,picture,thumbnails{uri,is_preferred}",
        }, timeout=DEFAULT_TIMEOUT)
        data = resp.json()
        if "error" in data:
            print(f"    Poll error: {data['error'].get('message', '?')}")
            continue
        status = data.get("status", {})
        phase = status.get("processing_phase", {}).get("status", "unknown")
        video_status = status.get("video_status", "unknown")
        elapsed = (attempt + 1) * 10
        print(f"    {elapsed}s: phase={phase}, video_status={video_status}")
        if phase == "complete" and video_status == "ready":
            thumbs = data.get("thumbnails", {}).get("data", [])
            preferred = next((t for t in thumbs if t.get("is_preferred")), None)
            return (preferred or {}).get("uri") or data.get("picture")
    print("  WARNING: processing timed out. Falling back to picture.")
    resp = requests.get(url, headers=auth_headers(), params={"fields": "picture"},
                        timeout=DEFAULT_TIMEOUT)
    return resp.json().get("picture")


def create_ad(adset_id, ad_name, creative, status="PAUSED", pixel_id=None):
    """Create an ad in an ad set. Retries transient OAuthException errors.

    status defaults to PAUSED — the skill never launches spending ads
    automatically. The user reviews and un-pauses in Ads Manager.
    """
    url = graph_url(get_ad_account_id(), "ads")
    payload = {
        "adset_id": numeric_id(adset_id, "adset_id"),
        "name": ad_name,
        "status": status,
        "creative": json.dumps(creative),
    }
    if pixel_id:
        payload["tracking_specs"] = json.dumps([{
            "action.type": ["offsite_conversion"],
            "fb_pixel": [pixel_id],
        }])

    for attempt in range(1, 5):
        resp = requests.post(url, headers=auth_headers(), data=payload, timeout=DEFAULT_TIMEOUT)
        data = resp.json()
        if "error" not in data:
            ad_id = data["id"]
            print(f"  Created ad: {ad_id} ({ad_name}) [status={status}]")
            return ad_id
        err = data["error"]
        if err.get("is_transient") and attempt < 4:
            backoff = min(60, 5 * (2 ** (attempt - 1)))
            print(f"  Transient error (code {err.get('code')}). Retry {attempt}/4 in {backoff}s.")
            time.sleep(backoff)
            continue
        print(f"  ERROR creating ad: {json.dumps(err, indent=2)}")
        return None
    return None
