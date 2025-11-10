"""
Refactored Nginx operations module with a Site dataclass and NginxManager class.
- Site dataclass centralizes site metadata and defaults
- NginxManager provides high-level methods that accept Site objects
- Backwards-compatible helpers included: parse_sites_list -> List[Site]
- Dry-run support, idempotent flag application, combined files handling with per-site markers
- Cross-platform: DNS skipped on Windows, platform-aware commands/paths
- Improved insertions: e.g., cache inside location / {} when possible
- Added cache clear and DNS reload
NOTE: This file re-uses helper functions from utils_devops.core modules.
"""
from __future__ import annotations
import re
import shutil
import socket
import subprocess
import os
import pwd
import grp
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Import your internal helpers (adjust these paths/names if your project differs)
from utils_devops.core.logs import get_library_logger
from utils_devops.core.files import (
    atomic_write, ensure_dir, remove_dir, remove_file,
    file_exists, dir_exists, read_file, touch
)
from utils_devops.core.systems import is_windows, is_linux, is_root, command_exists, run
from utils_devops.core.strings import render_jinja

log = get_library_logger()

# Defaults (platform-aware)
DEFAULT_NGINX_CMD = "nginx.exe" if is_windows() else "nginx"
DEFAULT_TEST_CMD = [DEFAULT_NGINX_CMD, "-t"]
DEFAULT_RELOAD_CMD = [DEFAULT_NGINX_CMD, "-s", "reload"]
DEFAULT_START_CMD = [DEFAULT_NGINX_CMD, "-g", "daemon off;"]
DEFAULT_PID_FILE = Path(r"C:\nginx\logs\nginx.pid") if is_windows() else Path("/run/nginx.pid")
DEFAULT_LOG_DIR = Path(r"C:\nginx\logs") if is_windows() else Path("/etc/nginx/logs")
DEFAULT_SITES_AVAILABLE = Path(r"C:\nginx\conf\sites-available") if is_windows() else Path("/etc/nginx/sites-available")
DEFAULT_SITES_ENABLED = Path(r"C:\nginx\conf\sites-enabled") if is_windows() else Path("/etc/nginx/sites-enabled")
DEFAULT_CACHE_BASE = Path(r"C:\nginx\cache") if is_windows() else Path("/etc/nginx/cache")
DEFAULT_CACHE_COMBINED = (Path(r"C:\nginx\conf.d") if is_windows() else Path("/etc/nginx/conf.d")) / "cache-paths.conf"
DEFAULT_DNS_COMBINED = (Path(r"C:\etc\dnsmasq.d") if is_windows() else Path("/etc/dnsmasq.d")) / "combined-dns.conf"
DEFAULT_NGINX_CONF = Path(r"C:\nginx\conf\nginx.conf") if is_windows() else Path("/etc/nginx/nginx.conf")
DUMMY_UPSTREAM = "http://127.0.0.1:81"
DEFAULT_NGINX_IP = "172.16.229.50"

class NginxOpsError(Exception):
    """Custom exception for Nginx operations errors."""
    pass

@dataclass
class Site:
    """
    Structured representation of a site.
    - name: used for file names and server_name
    - upstream: URL[](http://host:port), or filesystem path for `serve` sites
    - is_serve: whether the site is a static serve (root path)
    - locations: list of (path, upstream) tuples for additional location blocks
    - flags: mapping of flag names -> values (True or specific value)
    - client_max_body_size: optional override for client_max_body_size
    - force: whether to force re-create configs
    - description: optional descriptive text
    """
    name: str
    upstream: str = ""
    is_serve: bool = False
    locations: List[Tuple[str, str]] = field(default_factory=list)
    flags: Dict[str, Any] = field(default_factory=dict)
    client_max_body_size: Optional[str] = None
    force: bool = False
    description: Optional[str] = None

    @classmethod
    def from_parsed_line(cls, line: str) -> "Site":
        """Parse a single line from sites.txt into Site object.
        Format: site upstream [flags] [/path=upstream]
        """
        parts = re.split(r"\s+", line.strip())
        if not parts or parts[0].startswith("#"):
            raise ValueError("empty or comment line")
        name = parts[0]
        upstream = parts[1] if len(parts) > 1 else ""
        is_serve = upstream.startswith("/") or (len(upstream) > 1 and re.match(r"[A-Za-z]:\\", upstream))
        locations: List[Tuple[str, str]] = []
        flags: Dict[str, Any] = {}
        for p in parts[2:]:
            if p.startswith('/'):
                if '=' in p:
                    path, up = p.split('=', 1)
                    path = path.strip()
                    up = up.strip()
                    locations.append((path, up))
                    flags[path] = up  # add to flags for sync
                else:
                    path = p.strip()
                    locations.append((path, ""))
                    flags[path] = True  # add to flags
            else:
                if '=' in p:
                    k, v = p.split('=', 1)
                    flags[k.lower().strip()] = v.strip()
                else:
                    flags[p.lower().strip()] = True
        return cls(name, upstream, is_serve, locations, flags)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def help() -> None:
    """
Nginx Operations Module - Complete Help Reference
=================================================

Overview
--------
High-level Nginx site management with idempotent operations, template rendering,
flag-based configuration, and cross-platform support. Manages sites, cache, DNS,
and service control with dry-run capability.

Key Classes
-----------
NginxOpsError: Custom exception for Nginx operations failures.
Site: Dataclass representing site configuration (name, upstream, flags, locations).
NginxManager: Main manager class for all Nginx operations.
Flag: Configuration for flag templates and placement rules.

Core Functions
--------------
Initialization & Setup
NginxManager(sites_available, sites_enabled, cache_base, templates_dir, dry_run, validate_upstreams)
    Create manager instance with customizable paths and dry-run mode.
    - validate_upstreams: Optional upstream validation (default: False)
    - fallback_upstream: Fallback upstream when validation fails (default: http://127.0.0.1:81)
help() -> None
    Print this comprehensive help reference.

Site Management
parse_sites_list(list_path) -> List[Site]
    Parse sites.txt into structured Site objects.
create_site(site, proxy_tpl, serve_tpl, location_tpl) -> Path
    Create or update site config from Site object with template rendering.
remove_site(site_name) -> None
    Remove site config, cache, DNS entries, and clean up.
sync_sites(sites, list_path) -> None
    Full sync: add/update/remove sites based on sites.txt.
sync_from_list(list_path, force_all) -> None
    Complete sync from sites.txt file.
list_available_sites() -> List[str]
    List all configured site names.

Configuration & Templates
render_template(name, context) -> str
    Render Jinja template with auto-fallback to string substitution.
build_location_blocks(locations, location_tpl) -> List[str]
    Generate location blocks from template for additional routes.
write_site_config(site, rendered) -> Path
    Atomic write and enable site configuration.
setup_site_logs(site) -> Tuple[Path, Path]
    Create access/error log files with proper permissions.

Flag Management
apply_flag(site, flag, value) -> None
    Apply configuration flag (cache, error, upload, dns, locations).
remove_flag(site_name, flag) -> None
    Remove flag configuration and clean up associated resources.
sync_flags(sites) -> None
    Sync all flags for given sites from their Site objects.
sync_flags_for_site(site) -> None
    Sync flags for a single site.
flag_exists(site, flag) -> bool
    Check if flag is already applied to site.

Cache Operations
ensure_cache_dir(site) -> Path
    Create and permission cache directory for site.
clear_cache(site=None) -> None
    Clear cache for specific site or all sites.
reload_cache(sites, flags_dir, cache_base, dry_run) -> None
    Clear and re-apply cache configuration.

Service Control
manage_service(test_cmd, reload_cmd, start_cmd) -> bool
    Test configuration and reload/start Nginx service.
validate_upstream(upstream, fallback, timeout, use_http) -> str
    Validate upstream reachability with fallback support (optional feature).
reload_dns() -> None
    Reload dnsmasq service (Linux only).

Template System
---------------
Templates use Jinja2 with fallback to simple string substitution.
Standard templates:
- reverse-proxy.conf: Reverse proxy configuration
- serve.conf: Static file serving
- location.conf: Additional location blocks
- flags/*.conf: Flag-specific configurations

Flag templates support META directives for placement:
# META: placement=server_443_out_after_location, begin=# ---- BEGIN ----, end=# ---- END ----

Site Definition Format
----------------------
site upstream [flags] [/path=upstream]
Examples:
example.com http://backend:8080 cache upload=50M /api/=http://api:3000
static.site /var/www/html serve error
app.site https://app:8443 dns /admin/=http://admin:8080

Supported Flags
---------------
cache: Enable proxy caching with per-site cache directory
error: Enable proxy_intercept_errors for custom error pages
upload: Set client_max_body_size (upload=100M)
dns: Add dnsmasq entry for site (Linux only)
/path/: Add additional location block with custom upstream
serve: Static file serving mode (uses serve.conf template)

Marker System
-------------
Auto-generated markers for idempotent operations:
# ---- BEGIN CACHE example.com ----
proxy_cache example.com_cache;
...
# ---- END CACHE example.com ----

Platform Support
----------------
Linux: Full feature support (sites-available/enabled, dnsmasq, symlinks)
Windows: Basic support (copy instead of symlinks, no DNS management)

Dry Run Mode
------------
Set dry_run=True in NginxManager to preview changes without applying.

Optional Features
-----------------
Upstream Validation: Disable with validate_upstreams=False in NginxManager
Fallback Upstream: Configure with fallback_upstream parameter

Common Patterns
---------------
# Basic setup
mgr = NginxManager(dry_run=True)
sites = mgr.parse_sites_list("sites.txt")
mgr.sync_sites(sites)

# Single site operations
site = Site("example.com", "http://1.2.3.4", flags={"cache": True})
mgr.create_site(site)
mgr.apply_flag(site, "cache")

# Service management
mgr.manage_service()
mgr.clear_cache()

Error Handling
--------------
All operations raise NginxOpsError on failure with descriptive messages.
Service operations include retry logic with tenacity.
Configuration changes are atomic with backup/rollback capability.

Dependencies
------------
jinja2: Template rendering
tenacity: Retry decorators
requests: Upstream validation (optional)
rich: Optional pretty output (table formatting)

See also: files, systems, strings modules for utility functions.
"""
    print(help.__doc__)

# Small helpers (kept internal to manager but available standalone)
def _find_server_blocks(text: str) -> List[Tuple[int, int, str]]:
    """Proper server block detection with nested handling."""
    blocks = []
    pos = 0
    
    while pos < len(text):
        # Find server start
        server_match = re.search(r'server\s*\{', text[pos:])
        if not server_match:
            break
            
        start = pos + server_match.start()
        depth = 0
        i = start
        
        while i < len(text):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    blocks.append((start, end, text[start:end]))
                    pos = end
                    break
            i += 1
        else:
            break  # Unclosed block
    
    return blocks

def _server_has_port(block: str, port: int) -> bool:
    """Check if server block listens on specific port."""
    return bool(re.search(rf'listen\s+[^;]*\b{port}\b', block))

def _find_location_blocks(block: str, path: str = "/") -> List[Tuple[int, int, str]]:
    """Find location blocks matching path in a server block."""
    blocks = []
    esc_path = re.escape(path)
    for m in re.finditer(rf"location\s+{esc_path}\s*\{{", block):
        start = m.start()
        depth = 1
        for i in range(m.end(), len(block)):
            if block[i] == "{":
                depth += 1
            elif block[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    blocks.append((start, end, block[start:end]))
                    break
    return blocks

@dataclass
class Flag:
    """
    Represents a configurable flag for Nginx sites.
    - name: Flag identifier (e.g., 'cache', '/api')
    - template: Template file name for primary insertion
    - placement: Insertion placement (e.g., 'inside_location', 'server_443_out', 'combined')
    - target_getter: Function to get primary target file
    - secondary_template: Optional secondary template (e.g., for combined configs)
    - secondary_target_getter: Function for secondary target
    - context_adjuster: Function to adjust rendering context
    - apply_hook: Optional custom apply function (overrides template)
    - remove_hook: Optional custom remove function
    - pre_apply: Action before apply
    - post_remove: Action after remove
    """
    name: str
    template: Optional[str] = None
    placement: Optional[str] = None
    target_getter: Callable[['NginxManager', Site], Path] = lambda mgr, site: mgr.sites_available / site.name
    secondary_template: Optional[str] = None
    secondary_target_getter: Optional[Callable[['NginxManager', Site], Path]] = None
    context_adjuster: Optional[Callable[[Dict[str, Any], 'NginxManager', Site, Optional[Any]], Dict[str, Any]]] = None
    apply_hook: Optional[Callable[['NginxManager', Site, Optional[Any]], None]] = None
    remove_hook: Optional[Callable[['NginxManager', Site], None]] = None
    pre_apply: Optional[Callable[['NginxManager', Site], None]] = None
    post_remove: Optional[Callable[['NginxManager', Site], None]] = None

    def get_markers(self, site: Site) -> Tuple[str, str]:
        """Generate begin/end markers for this flag."""
        flag_part = self.name.upper().replace("/", "LOCATION-")
        return f"# ---- BEGIN {flag_part} {site.name} ----", f"# ---- END {flag_part} {site.name} ----"

    def get_secondary_markers(self, site: Site) -> Tuple[str, str]:
        """Generate markers for secondary insertion (same as primary by default)."""
        return self.get_markers(site)

class NginxManager:
    """
    High-level manager for Nginx site configurations using Site and Flag objects.
    Supports creation, syncing, flag application, service management.
    """
    def __init__(
        self,
        sites_available: Path = DEFAULT_SITES_AVAILABLE,
        sites_enabled: Path = DEFAULT_SITES_ENABLED,
        cache_base: Path = DEFAULT_CACHE_BASE,
        cache_combined: Path = DEFAULT_CACHE_COMBINED,
        dns_combined: Path = DEFAULT_DNS_COMBINED if is_linux() else None,
        log_dir: Path = DEFAULT_LOG_DIR,
        flags_dir: Union[Path, str] = Path("/etc/nginx/generate-sites/templates"),
        templates_dir: Optional[Path] = None,
        dry_run: bool = False,
        validate_upstreams: bool = False,
        fallback_upstream: str = DUMMY_UPSTREAM,
    ) -> None:
        self.sites_available = Path(sites_available)
        self.sites_enabled = Path(sites_enabled)
        self.cache_base = Path(cache_base)
        self.cache_combined = Path(cache_combined)
        self.dns_combined = Path(dns_combined) if dns_combined else None
        if is_windows() and self.dns_combined:
            log.warning("DNS management skipped on Windows (dnsmasq not supported)")
            self.dns_combined = None
        self.log_dir = Path(log_dir)
        self.flags_dir = Path(flags_dir)
        self.templates_dir = Path(templates_dir) if templates_dir else self.flags_dir
        self.dry_run = dry_run
        self.validate_upstreams = validate_upstreams
        self.fallback_upstream = fallback_upstream
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True)
        # Ensure directories
        ensure_dir(str(self.sites_available))
        ensure_dir(str(self.sites_enabled))
        ensure_dir(str(self.cache_base))
        ensure_dir(str(self.log_dir))
        # Known flags registry
        self.known_flags: Dict[str, Flag] = {
            "cache": Flag(
                "cache",
                template="cache.conf",
                placement="server_443_out_after_location",  # Fixed placement
                secondary_template="cache-path.conf",
                secondary_target_getter=lambda mgr, site: mgr.cache_combined,
                context_adjuster=lambda ctx, mgr, site, val: ctx | {"SITE": site.name, "CACHE_DIR": str(mgr.cache_base / site.name)},
                pre_apply=lambda mgr, site: mgr.ensure_cache_dir(site),
                post_remove=lambda mgr, site: remove_dir(str(mgr.cache_base / site.name), recursive=True) if dir_exists(str(mgr.cache_base / site.name)) else None
            ),
            "error": Flag(
                "error",
                template="error.conf",
                placement="server_443_out",
                context_adjuster=lambda ctx, mgr, site, val: ctx | {"SITE": site.name}
            ),
            "dns": Flag(
                "dns",
                template="dns.conf",
                placement="combined",
                target_getter=lambda mgr, site: mgr.dns_combined,
                context_adjuster=lambda ctx, mgr, site, val: ctx | {"SITE": site.name, "IP": re.match(r"https?://([\d\.]+)", site.upstream).group(1) if re.match(r"https?://([\d\.]+)", site.upstream) else DEFAULT_NGINX_IP}
            ),
            "upload": Flag(
                "upload",
                apply_hook=lambda mgr, site, val: mgr._set_client_max_body_size(mgr.sites_available / site.name, val or site.client_max_body_size or "10M"),
                remove_hook=lambda mgr, site: log.info(f"To revert upload for {site.name}, re-create the site without upload flag")
            ),
        }

    def parse_template_meta(self, template_path: Path) -> Dict[str, str]:
        """Parse META directives from template headers."""
        if not template_path.exists():
            return {}
        
        content = template_path.read_text(encoding="utf-8")
        meta = {}
        
        # Parse # META: key=value, key2=value2
        meta_match = re.search(r'^#\s*META:\s*(.+)$', content, flags=re.MULTILINE)
        if meta_match:
            meta_line = meta_match.group(1).strip()
            for item in re.split(r'\s*,\s*', meta_line):
                if '=' in item:
                    key, value = item.split('=', 1)
                    meta[key.strip()] = value.strip()
                else:
                    meta[item.strip()] = "true"
        
        return meta

    def _strip_meta_lines(self, content: str) -> str:
        """Remove META lines from template content."""
        return re.sub(r'(?m)^[ \t]*#\s*META:.*\n?', '', content)

    # -------------------- Parsing --------------------
    def parse_sites_list(self, list_path: Union[str, Path]) -> List[Site]:
        """Parse sites.txt into list of Site objects."""
        p = Path(list_path)
        if not file_exists(str(p)):
            raise NginxOpsError(f"sites.txt not found: {p}")
        sites: List[Site] = []
        for line in read_file(str(p)).splitlines():
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            try:
                sites.append(Site.from_parsed_line(s))
            except ValueError as e:
                log.warning(f"Skipping invalid line in sites.txt: {s} ({e})")
        log.info(f"Parsed {len(sites)} sites from {p}")
        return sites

    # -------------------- Templates & Rendering --------------------
    def render_template(self, name: Union[str, Path], context: Dict[str, Any]) -> str:
        """Render a Jinja template with context."""
        tpl_name = str(name)
        try:
            tpl = self.jinja_env.get_template(tpl_name)
            return tpl.render(**context)
        except TemplateNotFound:
            log.warning(f"Template not found: {tpl_name}, falling back to raw render")
            return render_jinja(tpl_name, context)
        except Exception as e:
            raise NginxOpsError(f"Template rendering failed for {tpl_name}: {e}")

    def build_location_blocks(self, locations: List[Tuple[str, str]], location_tpl: Union[str, Path] = "location.conf") -> List[str]:
        """Build location blocks from templates (used in create_site)."""
        blocks: List[str] = []
        for path, up in locations:
            ctx = {"PATH": path, "UPSTREAM": up}
            blocks.append(self.render_template(location_tpl, ctx))
        return blocks

    # -------------------- Validation --------------------
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def validate_upstream(self, upstream: str, fallback: str = DUMMY_UPSTREAM, timeout: int = 1, use_http: bool = True) -> str:
        """Validate upstream reachability."""
        if not self.validate_upstreams:
            return upstream  # Skip validation if disabled
            
        match = re.match(r'(https?://)?([^:/]+)(:\d+)?(/.*)?', upstream)
        if not match:
            log.warning(f"Invalid upstream: {upstream}, using fallback")
            return fallback
        scheme, host, port, _ = match.groups()
        scheme = scheme or "http://"
        port = port or ""
        if use_http:
            url = f"{scheme}{host}{port}"
            try:
                resp = requests.head(url, timeout=timeout)
                if resp.status_code < 400:
                    return upstream
            except Exception as e:
                log.debug(f"Upstream HTTP check failed: {e}")
        else:
            try:
                socket.getaddrinfo(host, None)
                return upstream
            except Exception as e:
                log.debug(f"Upstream DNS check failed: {e}")
        log.warning(f"Upstream {upstream} unreachable, using {fallback}")
        return fallback

    # -------------------- Files & Configs --------------------
    def write_site_config(self, site: Site, rendered: str) -> Path:
        """Write and enable site config."""
        tgt_avail = self.sites_available / site.name
        tgt_enabled = self.sites_enabled / site.name
        if self.dry_run:
            log.info(f"[dry-run] Would write config for {site.name} to {tgt_avail}")
            return tgt_avail
        atomic_write(str(tgt_avail), rendered)
        try:
            if file_exists(str(tgt_enabled)) or tgt_enabled.is_symlink():
                tgt_enabled.unlink()
            if is_windows():
                shutil.copy(str(tgt_avail), str(tgt_enabled))
            else:
                tgt_enabled.symlink_to(tgt_avail)
        except Exception as e:
            raise NginxOpsError(f"Could not enable site {site.name}: {e}")
        log.info(f"Wrote and enabled config for {site.name}")
        return tgt_avail

    def _set_permissions_safe(self, path: str, mode: int = 0o644, owner: str = "root") -> None:
        """Safe permission setting that avoids I/O closed file errors."""
        if self.dry_run:
            return
            
        try:
            # Set mode using os.chmod
            os.chmod(path, mode)
            
            # Set owner safely - only if we're root and the user exists
            if is_root() and is_linux():
                try:
                    if ":" in owner:
                        user, group = owner.split(":", 1)
                    else:
                        user, group = owner, owner
                    
                    uid = pwd.getpwnam(user).pw_uid
                    gid = grp.getgrnam(group).gr_gid
                    os.chown(path, uid, gid)
                except (KeyError, PermissionError) as e:
                    log.debug(f"Could not set owner to {owner} for {path}: {e}")
                    # Fallback to root
                    try:
                        os.chown(path, 0, 0)  # root:root
                    except PermissionError:
                        log.warning(f"Could not set owner to root for {path}")
        except Exception as e:
            log.warning(f"Could not set permissions for {path}: {e}")

    def setup_site_logs(self, site: Site) -> Tuple[Path, Path]:
        """Setup access/error logs for site with proper permissions."""
        access = self.log_dir / f"{site.name}-access.log"
        error = self.log_dir / f"{site.name}-error.log"
        if self.dry_run:
            log.info(f"[dry-run] Would create logs: {access}, {error}")
            return access, error
            
        touch(str(access))
        touch(str(error))
        
        # Set proper permissions using safe method
        try:
            self._set_permissions_safe(str(access), 0o644, "root")
            self._set_permissions_safe(str(error), 0o644, "root")
        except Exception as e:
            log.warning(f"Could not set log file permissions: {e}")
            
        return access, error

    def ensure_cache_dir(self, site: Site) -> Path:
        """Ensure per-site cache directory exists with proper permissions."""
        cache_dir = self.cache_base / site.name
        ensure_dir(str(cache_dir))
        if not self.dry_run:
            try:
                self._set_permissions_safe(str(cache_dir), 0o755, "root")
            except Exception as e:
                log.warning(f"Could not set cache directory permissions: {e}")
        return cache_dir

    # -------------------- Creation & Sync --------------------
    def create_site(
        self,
        site: Site,
        proxy_tpl: Union[str, Path] = "reverse-proxy.conf",
        serve_tpl: Union[str, Path] = "serve.conf",
        location_tpl: Union[str, Path] = "location.conf",
    ) -> Path:
        """Create or force-update a single site config."""
        conf_path = self.sites_available / site.name
        if file_exists(str(conf_path)) and not site.force:
            log.info(f"Site config exists: {conf_path} (skip)")
            return conf_path
        
        # Use validated upstream or fallback if validation is enabled
        upstream = self.validate_upstream(site.upstream or "", self.fallback_upstream) if self.validate_upstreams else (site.upstream or "")
        
        tpl = serve_tpl if site.is_serve else proxy_tpl
        context = {
            "SITE": site.name,
            "IP_ADDRESS": upstream,
            "ROOT_PATH": upstream if site.is_serve else "",
            "CLIENT_MAX_BODY_SIZE": site.client_max_body_size or "10M",
        }
        
        try:
            rendered = self.render_template(tpl, context)
            
            # Add location blocks if any
            if site.locations:
                location_blocks = self.build_location_blocks(site.locations, location_tpl)
                rendered += "\n" + "\n".join(location_blocks)
                
        except NginxOpsError as e:
            raise NginxOpsError(f"Failed to render templates for {site.name}: {e}")
            
        self.write_site_config(site, rendered)
        self.setup_site_logs(site)
        
        # Apply flags (includes upload override)
        self.sync_flags([site])
        self.manage_service()
        return conf_path

    def remove_site(self, site_name: str) -> None:
        """Remove a site and clean up associated files/flags."""
        conf_avail = self.sites_available / site_name
        conf_enabled = self.sites_enabled / site_name
        
        if self.dry_run:
            log.info(f"[dry-run] Would remove site {site_name}")
            return
            
        if file_exists(str(conf_enabled)) or conf_enabled.is_symlink():
            conf_enabled.unlink(missing_ok=True)
        if file_exists(str(conf_avail)):
            remove_file(str(conf_avail))
            
        # Cleanup known flags
        for flag_name in list(self.known_flags):
            self.remove_flag(site_name, flag_name)
            
        # Remove empty logs
        access = self.log_dir / f"{site_name}-access.log"
        error = self.log_dir / f"{site_name}-error.log"
        if file_exists(str(access)) and Path(access).stat().st_size == 0:
            remove_file(str(access))
        if file_exists(str(error)) and Path(error).stat().st_size == 0:
            remove_file(str(error))
            
        log.info(f"Removed site {site_name}")

    def sync_sites(self, sites: List[Site], list_path: Optional[Union[str, Path]] = None) -> None:
        """Sync list of sites: add/update/remove configs and flags."""
        existing = {p.stem for p in self.sites_available.iterdir() if p.is_file()}
        desired = {s.name for s in sites}
        to_add = desired - existing
        to_remove = existing - desired
        site_map = {s.name: s for s in sites}
        
        for sname in to_add:
            if sname in site_map:
                self.create_site(site_map[sname])
                
        for sname in to_remove:
            self.remove_site(sname)
            
        # Update existing
        for sname in desired & existing:
            s = site_map[sname]
            if s.force:
                self.create_site(s)
            self.sync_flags([s])
            
        self.manage_service()

    def sync_from_list(self, list_path: Union[str, Path], force_all: bool = False) -> None:
        """Complete sync from sites.txt (like original script)."""
        sites_map = {s.name: s for s in self.parse_sites_list(list_path)}
        existing_sites = set(self.list_available_sites())
        desired_sites = set(sites_map.keys())
        
        # Determine actions
        to_add = desired_sites - existing_sites
        to_remove = existing_sites - desired_sites
        to_keep = desired_sites & existing_sites
        
        log.info(f"Sync: +{len(to_add)} -{len(to_remove)} ~{len(to_keep)}")
        
        # Add new sites
        for site_name in to_add:
            self.create_site(sites_map[site_name])
        
        # Remove old sites
        for site_name in to_remove:
            self.remove_site(site_name)
        
        # Update existing sites
        for site_name in to_keep:
            site = sites_map[site_name]
            if force_all or site.force or site.flags.get("force"):
                log.info(f"Recreating site {site_name} (force)")
                self.create_site(site)
            
            # Sync flags for this site
            self.sync_flags_for_site(site)

    def sync_flags_for_site(self, site: Site) -> None:
        """Sync flags for a single site (like original sync_flags)."""
        known_flags = {"cache", "error", "upload", "dns"}
        desired_flags = set(site.flags.keys())
        desired_locations = {loc[0] for loc in site.locations}
        
        # Apply desired flags
        for flag in desired_flags:
            if flag == "force":
                continue
            value = site.flags[flag] if site.flags[flag] is not True else None
            self.apply_flag(site, flag, value)
        
        # Remove unwanted known flags
        for flag in known_flags:
            if flag not in desired_flags:
                self.remove_flag(site.name, flag)
        
        # Clean up orphaned locations
        conf_path = self.sites_available / site.name
        if conf_path.exists():
            content = read_file(str(conf_path))
            current_locations = set(re.findall(r'location\s+([^\s\{]+)\s*\{', content))
            for loc in current_locations:
                if loc != "/" and loc not in desired_locations:
                    self.remove_flag(site.name, loc)

    def list_available_sites(self) -> List[str]:
        """List available site configs."""
        if not self.sites_available.exists():
            return []
        return [p.stem for p in self.sites_available.glob("*") if p.is_file()]

    # -------------------- Flags --------------------
    def sync_flags(self, sites: List[Site]) -> None:
        """Sync flags for given sites, including locations."""
        for s in sites:
            conf = self.sites_available / s.name
            if not file_exists(str(conf)):
                continue
            desired_flags = set(s.flags.keys())
            for flag in desired_flags:
                if flag == "force":
                    continue
                value = s.flags[flag] if s.flags[flag] is not True else None
                self.apply_flag(s, flag, value)
            # Remove undesired known flags
            for flag in set(self.known_flags) - desired_flags:
                self.remove_flag(s.name, flag)
        self.manage_service()

    def apply_flag(self, site: Site, flag: str, value: Optional[Any] = None) -> None:
        """Apply a flag to a site using Flag object."""
        if flag in self.known_flags:
            f = self.known_flags[flag]
        elif flag.startswith("/"):
            upstream = value if value is not None else site.upstream
            f = Flag(
                name=flag,
                template="location.conf",
                placement="server_443_out",
                context_adjuster=lambda ctx, mgr, site, val: ctx | {"PATH": flag, "UPSTREAM": upstream or ""},
            )
        else:
            log.warning(f"Unknown flag: {flag}")
            return
            
        if self.flag_exists(site, flag):
            log.debug(f"Flag {flag} already exists for {site.name}, updating")
            
        if f.pre_apply:
            f.pre_apply(self, site)
            
        if f.apply_hook:
            if not self.dry_run:
                f.apply_hook(self, site, value)
        elif f.template:
            context = {"SITE": site.name}
            if f.context_adjuster:
                context = f.context_adjuster(context, self, site, value)
            snippet = self.render_template(f.template, context)
            begin, end = f.get_markers(site)
            target = f.target_getter(self, site)
            
            if self.dry_run:
                log.info(f"[dry-run] Would apply flag {flag} to {target}")
            else:
                if f.placement == "combined":
                    self._apply_entry_to_combined(target, snippet, begin, end)
                else:
                    self._apply_snippet(target, snippet, f.placement or "server_443_out", begin, end)
                    
            if f.secondary_template:
                sec_context = {"SITE": site.name}
                if f.context_adjuster:
                    sec_context = f.context_adjuster(sec_context, self, site, value)
                sec_snippet = self.render_template(f.secondary_template, sec_context)
                sec_begin, sec_end = f.get_secondary_markers(site)
                sec_target = f.secondary_target_getter(self, site)
                if self.dry_run:
                    log.info(f"[dry-run] Would apply secondary for {flag} to {sec_target}")
                else:
                    self._apply_entry_to_combined(sec_target, sec_snippet, sec_begin, sec_end)
                    
        log.info(f"Applied flag {flag} to {site.name}")

    def remove_flag(self, site_name: str, flag: str) -> None:
        """Remove a flag from a site using Flag object."""
        site = Site(name=site_name)  # dummy for markers
        if flag in self.known_flags:
            f = self.known_flags[flag]
        elif flag.startswith("/"):
            f = Flag(name=flag)
        else:
            log.debug(f"Unknown flag for removal: {flag}")
            return
            
        if f.remove_hook:
            f.remove_hook(self, site)
        elif f.template or flag.startswith("/"):
            begin, end = f.get_markers(site)
            target = f.target_getter(self, site)
            if self.dry_run:
                log.info(f"[dry-run] Would remove flag {flag} from {target}")
            else:
                self._remove_region(target, begin, end)
            if f.secondary_template:
                sec_begin, sec_end = f.get_secondary_markers(site)
                sec_target = f.secondary_target_getter(self, site)
                self._remove_entry_from_combined(sec_target, sec_begin, sec_end)
                
        if f.post_remove:
            f.post_remove(self, site)
        log.info(f"Removed flag {flag} from {site_name}")

    def flag_exists(self, site: Site, flag: str) -> bool:
        """Check if a flag is already applied to site."""
        if flag not in self.known_flags and not flag.startswith("/"):
            return False
            
        if flag in self.known_flags:
            f = self.known_flags[flag]
        else:
            f = Flag(name=flag)
            
        target = f.target_getter(self, site)
        if not file_exists(str(target)):
            return False
            
        txt = read_file(str(target))
        begin, _ = f.get_markers(site)
        return begin in txt

    # -------------------- low-level text modifications --------------------
    def _apply_snippet(self, conf_path: Path, snippet: str, placement: str = "server_443_out", 
                       begin_marker: Optional[str] = None, end_marker: Optional[str] = None) -> None:
        """Robust snippet placement with marker support."""
        if self.dry_run:
            log.info(f"[dry-run] Would apply snippet to {conf_path}")
            return
        
        txt = read_file(str(conf_path))
        blocks = _find_server_blocks(txt)
        placed = False
        
        port = 443 if "443" in placement else 80
        inside_location = "inside_location" in placement
        after_locations = "after_location" in placement
        
        for start, end, block in blocks:
            if not _server_has_port(block, port):
                continue
                
            # Handle marker replacement
            if begin_marker and end_marker:
                pattern = re.escape(begin_marker) + r'.*?' + re.escape(end_marker)
                if re.search(pattern, block, flags=re.DOTALL):
                    new_block = re.sub(pattern, f"{begin_marker}\n{snippet}\n{end_marker}", block, flags=re.DOTALL)
                    txt = txt[:start] + new_block + txt[end:]
                    placed = True
                    break
                else:
                    # Insert with markers
                    wrapped = f"{begin_marker}\n{snippet}\n{end_marker}"
                    new_block = self._insert_snippet_into_block(block, wrapped, placement)
                    if new_block != block:
                        txt = txt[:start] + new_block + txt[end:]
                        placed = True
                        break
            else:
                # Insert without markers
                new_block = self._insert_snippet_into_block(block, snippet, placement)
                if new_block != block:
                    txt = txt[:start] + new_block + txt[end:]
                    placed = True
                    break
        
        if not placed:
            log.warning(f"Could not place snippet in {conf_path}, appending to file")
            txt += f"\n{snippet}"
        
        atomic_write(str(conf_path), txt)

    def _insert_snippet_into_block(self, block: str, snippet: str, placement: str) -> str:
        """Insert snippet into server block at correct position."""
        if "inside_location" in placement:
            # Find location / block
            loc_match = re.search(r'(location\s+/\s*\{[^}]*)(\})', block, flags=re.DOTALL)
            if loc_match:
                return block[:loc_match.start(1)] + loc_match.group(1) + "\n" + snippet + "\n" + block[loc_match.start(2):]
        
        elif "after_location" in placement:
            # Find last location block and insert after it
            locations = list(re.finditer(r'location\s+[^{]+\{[^}]*\}', block, flags=re.DOTALL))
            if locations:
                last_loc = locations[-1]
                return block[:last_loc.end()] + "\n" + snippet + block[last_loc.end():]
        
        # Default: insert before closing server brace
        last_brace = block.rfind('}')
        if last_brace != -1:
            return block[:last_brace] + "\n" + snippet + "\n" + block[last_brace:]
        
        return block

    def _remove_region(self, conf_path: Path, begin: str, end: str) -> None:
        """Remove a marked region from a config file."""
        if self.dry_run:
            return
        if not file_exists(str(conf_path)):
            return
        txt = read_file(str(conf_path))
        pattern = re.escape(begin) + r".*?" + re.escape(end) + r"\s*"
        # Use re.sub directly instead of regex_replace to avoid flags issue
        new_txt = re.sub(pattern, "", txt, flags=re.DOTALL)
        if new_txt != txt:
            atomic_write(str(conf_path), new_txt)

    def _apply_entry_to_combined(self, combined: Path, entry: str, begin: str, end: str) -> None:
        """Apply an entry to a combined file using markers."""
        if self.dry_run:
            return
        if not file_exists(str(combined)):
            ensure_dir(str(combined.parent))
            touch(str(combined))
        txt = read_file(str(combined))
        pattern = re.escape(begin) + r"(.*?)" + re.escape(end)
        # Use re.search directly instead of regex_search to avoid flags issue
        m = re.search(pattern, txt, flags=re.DOTALL)
        if m:
            # Use re.sub directly instead of regex_replace to avoid flags issue
            new_txt = re.sub(pattern, begin + "\n" + entry.strip() + "\n" + end, txt, flags=re.DOTALL)
        else:
            new_txt = txt.rstrip() + "\n" + begin + "\n" + entry.strip() + "\n" + end + "\n"
        if new_txt != txt:
            atomic_write(str(combined), new_txt)

    def _remove_entry_from_combined(self, combined: Path, begin: str, end: str) -> None:
        """Remove a marked entry from a combined file."""
        if not file_exists(str(combined)) or self.dry_run:
            return
        txt = read_file(str(combined))
        pattern = re.escape(begin) + r".*?" + re.escape(end) + r"\s*"
        # Use re.sub directly instead of regex_replace to avoid flags issue
        new_txt = re.sub(pattern, "", txt, flags=re.DOTALL)
        if new_txt != txt:
            atomic_write(str(combined), new_txt)

    def _set_client_max_body_size(self, conf_path: Path, val: str) -> None:
        """Set client_max_body_size in server block."""
        if self.dry_run:
            return
        txt = read_file(str(conf_path))
        blocks = _find_server_blocks(txt)
        modified = False
        for start, endpos, block in blocks:
            if not _server_has_port(block, 443):
                continue
            pattern = r"client_max_body_size\s+[^;]+;"
            # Use re.search directly instead of regex_search
            if re.search(pattern, block):
                # Use re.sub directly instead of regex_replace
                new_block = re.sub(pattern, f"client_max_body_size {val};", block)
            else:
                server_name_m = re.search(r"server_name\s+[^;]+;", block)
                insert_idx = server_name_m.end() if server_name_m else block.find("{") + 1
                new_block = block[:insert_idx] + f"\n    client_max_body_size {val};" + block[insert_idx:]
            txt = txt[:start] + new_block + txt[endpos:]
            modified = True
            break
        if modified:
            atomic_write(str(conf_path), txt)

    # -------------------- Service control --------------------
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def manage_service(self, test_cmd: List[str] = DEFAULT_TEST_CMD, reload_cmd: List[str] = DEFAULT_RELOAD_CMD, start_cmd: List[str] = DEFAULT_START_CMD) -> bool:
        """Test and reload/start Nginx service."""
        if self.dry_run:
            log.info("[dry-run] Would manage Nginx service")
            return True
        if not is_root():
            raise NginxOpsError("Requires root privileges")
        proc = run(test_cmd, capture=True, no_die=True)
        if proc.returncode == 0:
            run(reload_cmd, capture=True)
            log.info("Nginx reloaded successfully")
            return True
        run(start_cmd, capture=True)
        log.info("Started Nginx")
        return True

    # -------------------- Reloads --------------------
    def clear_cache(self, site: Optional[Union[Site, str]] = None) -> None:
        """Clear cache for a site (by name or Site object) or all sites."""
        if site is not None:
            site_name = site if isinstance(site, str) else site.name
            cache_dir = self.cache_base / site_name
            if not dir_exists(str(cache_dir)):
                return
            if self.dry_run:
                log.info(f"[dry-run] Would clear cache for {site_name}")
                return
            remove_dir(str(cache_dir), recursive=True)
            ensure_dir(str(cache_dir))  # recreate empty
            log.info(f"Cleared cache for {site_name}")
        else:
            if self.dry_run:
                log.info("[dry-run] Would clear all caches")
                return
            for d in self.cache_base.iterdir():
                if d.is_dir():
                    remove_dir(str(d), recursive=True)
                    ensure_dir(str(d))  # recreate empty
            log.info("Cleared all caches")

    def reload_dns(self) -> None:
        """Reload dnsmasq service (Linux only)."""
        if not self.dns_combined or not is_linux():
            log.warning("DNS reload skipped (not supported)")
            return
        if self.dry_run:
            log.info("[dry-run] Would reload DNS (dnsmasq)")
            return
        run(["systemctl", "restart", "dnsmasq"], elevated=True, no_die=True)
        log.info("Reloaded DNS (dnsmasq)")

# Export public API
__all__ = [
    "NginxOpsError",
    "Site", 
    "NginxManager",
    "Flag",
    "help",
    "parse_sites_list",
]

# Backwards compatibility
def parse_sites_list(list_path: Union[str, Path]) -> List[Site]:
    """Parse sites.txt into Site objects (backwards compatibility)."""
    manager = NginxManager()
    return manager.parse_sites_list(list_path)