from abstract_utilities.file_utils import *
from abstract_utilities.file_utils import run_pruned_func as run_pruned_funcs
import os, re, base64

# --------------------------------------------------------------------
# Safe command wrapper for debug visibility
# --------------------------------------------------------------------
def run_pruned_func(*args, **kwargs):
    cmd = kwargs.get("cmd")
    if kwargs.get("password"):
        cmd = f"sudo {cmd}"
    print(f"🟢 running: {cmd}")
    return run_pruned_funcs(*args, **kwargs)

# --------------------------------------------------------------------
# Safe remote write (preserves $host, ;, >, etc.)
# --------------------------------------------------------------------
def safe_write_remote(file_path, contents, **kwargs):
    """Safely write content to remote file via SSH using base64 encoding."""
    encoded = base64.b64encode(contents.encode()).decode()
    kwargs["cmd"] = f"echo {encoded} | base64 -d | sudo tee {file_path} > /dev/null"
    print(f"🟢 writing safely to {file_path}")
    return run_pruned_func(run_cmd, **kwargs)

# --------------------------------------------------------------------
# Global setup
# --------------------------------------------------------------------
user_kwargs = {
    "user_at_host": "solcatcher",
    "password": "ANy1Kan@!23"
}

init_dir = "/etc/nginx/sites-available/"
enabled_dir = "/etc/nginx/sites-enabled/"

texts = """
abstractgpt
comicguybook
croasis
frebase
googlegrey
ireadsolidity
itsaclownworld
joejamail
thecomicguybook
theoasis
vivint-adolfo
""".strip()

# --------------------------------------------------------------------
# Nginx config builders
# --------------------------------------------------------------------
def replace_301(text: str) -> str:
    """Ensure every 'return 301 https://' includes $host$request_uri;"""
    text = re.sub(
        r'return\s+301\s+https://[^;{]*;?',
        'return 301 https://$host$request_uri;',
        text,
        flags=re.IGNORECASE | re.MULTILINE
    )
    text = text.replace('&*', '}').replace('*&', '{')
    return text


def get_80(domain: str, ext: str) -> str:
    """Generate HTTP → HTTPS redirect server block."""
    text = f"""# HTTP redirect to HTTPS
server *&
    listen 80;
    listen [::]:80;
    server_name {domain}.{ext} www.{domain}.{ext};
    return 301 https://;
&*"""
    return replace_301(text)


def get_443(domain: str, ext: str) -> str:
    """Generate HTTPS server block."""
    text = f"""# HTTPS server
server *&
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {domain}.{ext} www.{domain}.{ext};

    root /var/www/sites/{domain}.{ext}/html;
    index index.html index.htm;

    ssl_certificate /etc/letsencrypt/live/{domain}.{ext}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}.{ext}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
&*"""
    return replace_301(text)

# --------------------------------------------------------------------
# Main loop: iterate through domain groups
# --------------------------------------------------------------------
for nu_domain in texts.splitlines():
    dir_path = os.path.join(init_dir, nu_domain)
    dirs = collect_globs(dir_path, file_type="d", **user_kwargs)
    if isinstance(dirs, str):
        dirs = [d for d in dirs.splitlines() if d.strip()]
    dirs = [d for d in dirs if "old" not in d]

    for ext_dir in dirs:
        ext = os.path.basename(ext_dir)
        domain = f"{nu_domain}.{ext}"
        if nu_domain !=ext:
            conf_file = os.path.join(ext_dir, "index.conf")
            tmp_conf = conf_file.replace("index.conf", "index_http.conf")
            ln_file = os.path.join(enabled_dir, f"{domain}.conf")

            # Generate content
            cont_80 = get_80(nu_domain, ext)
            cont_443 = get_443(nu_domain, ext)
            contents = f"{cont_80}\n\n{cont_443}"

            # Remove any old links
            run_pruned_func(run_cmd, cmd=f"rm -f {ln_file}", **user_kwargs)

            # 1️⃣ Write HTTP-only config for certbot
            safe_write_remote(tmp_conf, cont_80, **user_kwargs)
            run_pruned_func(run_cmd, cmd=f"ln -s {tmp_conf} {ln_file}", **user_kwargs)

            # 2️⃣ Run certbot to issue SSL cert
            run_pruned_func(run_cmd, cmd=f"certbot --nginx -d {domain} -d www.{domain}", **user_kwargs)

            # 3️⃣ Replace with full HTTP+HTTPS config
            safe_write_remote(conf_file, contents, **user_kwargs)
            run_pruned_func(run_cmd, cmd=f"ln -sf {conf_file} {ln_file}", **user_kwargs)

            # 4️⃣ Validate and reload nginx
            run_pruned_func(run_cmd, cmd="sudo nginx -t && sudo systemctl reload nginx", **user_kwargs)

