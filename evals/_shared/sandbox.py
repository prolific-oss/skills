"""
Shared sandbox utilities for Prolific automation skill evals.

Provides two public functions:

    ensure_prolific_binary() -> Path
        Downloads and caches the latest Prolific CLI release binary from
        GitHub. Safe to call at the top of any eval runner — it is a no-op
        when the current version is already cached.

    build_agent_env(item_cwd, prolific_binary) -> dict
        Builds the environment dict to pass to ClaudeAgentOptions.env for
        a single eval item. Symlinks the cached binary into item_cwd/bin/,
        prepends that to PATH, and injects PROLIFIC_TOKEN. Also blanks
        Langfuse credentials so the agent subprocess does not emit its own
        competing traces.

Typical usage in an automation skill's run_evals.py
----------------------------------------------------
    import sys
    sys.path.insert(0, str(Path(__file__).parents[1]))  # evals/ root
    from _shared.sandbox import ensure_prolific_binary, build_agent_env

    # Once at startup, before the experiment loop:
    prolific_bin = ensure_prolific_binary()

    # Per eval item, after tempfile.mkdtemp():
    env = build_agent_env(item_cwd, prolific_bin)
    options = ClaudeAgentOptions(..., env=env)

The install-prolific-cli eval does NOT use this module — that skill tests
pre-installation states and intentionally controls whether the binary is
present using mock executables.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import urllib.request
from pathlib import Path

GITHUB_RELEASES_API = "https://api.github.com/repos/prolific-oss/cli/releases/latest"

# Binaries are cached here, keyed by version tag.  Gitignored.
CACHE_DIR = Path(__file__).parent.parent / "_cache"

# Asset names on GitHub match sys.platform and platform.machine() via these maps.
# Verified against https://github.com/prolific-oss/cli/releases/latest (v1.0.1).
_OS_MAP: dict[str, str] = {
    "darwin": "darwin",
    "linux": "linux",
    "win32": "windows",
    "freebsd": "freebsd",
}
_ARCH_MAP: dict[str, str] = {
    "x86_64": "amd64",
    "amd64": "amd64",
    "arm64": "arm64",
    "aarch64": "arm64",
    "armv7l": "arm",
    "i386": "386",
    "i686": "386",
}


def _asset_name() -> str:
    os_key = _OS_MAP.get(sys.platform)
    if not os_key:
        raise RuntimeError(
            f"Unsupported platform for Prolific CLI binary: {sys.platform!r}\n"
            f"Supported: {list(_OS_MAP)}"
        )
    arch_key = _ARCH_MAP.get(platform.machine().lower())
    if not arch_key:
        raise RuntimeError(
            f"Unsupported architecture for Prolific CLI binary: {platform.machine()!r}\n"
            f"Supported: {list(_ARCH_MAP)}"
        )
    return f"prolific-{os_key}-{arch_key}"


def _fetch_latest_release() -> dict:
    req = urllib.request.Request(
        GITHUB_RELEASES_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "prolific-skills-evals",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def ensure_prolific_binary() -> Path:
    """
    Return a path to the latest Prolific CLI binary, downloading if needed.

    Cache strategy
    --------------
    The cache lives at skills/evals/_cache/ and uses the release version tag
    as the filename suffix (e.g. prolific-darwin-arm64-v1.0.1).  On each
    call, the GitHub API is queried for the latest tag.  If the tag matches
    a cached file that is already executable, no download occurs.  A new
    release triggers one download; old cached binaries are left in place.

    Checksum verification
    ---------------------
    Each release publishes a .sha256 file alongside the binary.  The download
    is verified against this before the binary is made executable, to catch
    corrupt or tampered files before they are run with bypassPermissions.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    release = _fetch_latest_release()
    version = release["tag_name"]
    asset_name = _asset_name()

    binary_path = CACHE_DIR / f"{asset_name}-{version}"
    if binary_path.is_file() and os.access(binary_path, os.X_OK):
        print(f"  Prolific CLI {version} already cached ({asset_name})")
        return binary_path

    assets = {a["name"]: a["browser_download_url"] for a in release["assets"]}

    binary_url = assets.get(asset_name)
    sha256_url = assets.get(f"{asset_name}.sha256")
    if not binary_url:
        available = sorted(
            a["name"] for a in release["assets"]
            if not a["name"].endswith((".md5", ".sha256"))
        )
        raise RuntimeError(
            f"No release asset '{asset_name}' found in {version}.\n"
            f"Available binaries: {available}"
        )

    print(f"  Downloading Prolific CLI {version} ({asset_name})...")
    tmp_path = binary_path.with_suffix(".tmp")
    urllib.request.urlretrieve(binary_url, tmp_path)

    if sha256_url:
        with urllib.request.urlopen(sha256_url) as resp:
            expected_sha256 = resp.read().decode().split()[0]
        actual_sha256 = hashlib.sha256(tmp_path.read_bytes()).hexdigest()
        if actual_sha256 != expected_sha256:
            tmp_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"SHA256 mismatch for {asset_name} — download may be corrupt.\n"
                f"  expected: {expected_sha256}\n"
                f"  actual:   {actual_sha256}"
            )
        print(f"  SHA256 verified.")
    else:
        print(f"  Warning: no .sha256 file found for {asset_name} in {version}, skipping verification.")

    tmp_path.chmod(0o755)
    tmp_path.replace(binary_path)
    print(f"  Cached at {binary_path}")
    return binary_path


def build_agent_env(item_cwd: str, prolific_binary: Path) -> dict[str, str]:
    """
    Build the env dict for a Claude Code agent subprocess running an
    automation skill eval.

    Symlinks the cached binary
    --------------------------
    Rather than copying the binary into each item's temp dir (slow, disk
    intensive), a symlink is created at item_cwd/bin/prolific pointing at
    the cached binary.  This is safe because the binary is read-only after
    download and shared across concurrent eval items.

    PATH prepending
    ---------------
    item_cwd/bin/ is prepended to the inherited system PATH so the agent
    finds our binary first, regardless of whether prolific is also installed
    system-wide.

    Token precedence
    ----------------
    PROLIFIC_TEST_TOKEN takes priority over PROLIFIC_TOKEN.  This allows
    a dedicated eval/test Prolific account to be used for evals without
    touching the developer's personal token.  Additional Prolific-prefixed
    config such as PROLIFIC_TEST_WORKSPACE_ID is also passed through so
    prompts can reference it.

    Langfuse credentials
    --------------------
    Blanked out in the subprocess env.  The agent's OTel spans reach
    Langfuse through LangSmith's integration, parented to the dataset run
    span via propagate_attributes() — direct Langfuse access from the
    subprocess would create orphaned duplicate traces.
    """
    bin_dir = os.path.join(item_cwd, "bin")
    os.makedirs(bin_dir, exist_ok=True)

    link_path = os.path.join(bin_dir, "prolific")
    if not os.path.exists(link_path):
        os.symlink(prolific_binary, link_path)

    token = os.environ.get("PROLIFIC_TEST_TOKEN") or os.environ.get("PROLIFIC_TOKEN", "")
    if not token:
        print("  Warning: neither PROLIFIC_TEST_TOKEN nor PROLIFIC_TOKEN is set.")

    env = {
        "PROLIFIC_TOKEN": token,
        "PATH": bin_dir + os.pathsep + os.environ.get("PATH", ""),
        "LANGFUSE_PUBLIC_KEY": "",
        "LANGFUSE_SECRET_KEY": "",
        "LANGFUSE_BASE_URL": "",
    }
    for key, value in os.environ.items():
        if key.startswith("PROLIFIC_") and key not in env:
            env[key] = value
    return env
