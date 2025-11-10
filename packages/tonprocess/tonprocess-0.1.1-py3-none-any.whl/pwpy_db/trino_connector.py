import os
import logging
import pickle
import base64
import hashlib
import getpass
import platform
import socket
import subprocess
import sys
import requests
import psutil

# cryptography works for older python; no version-specific call here
from cryptography.fernet import Fernet

# importlib metadata compatibility
try:
    from importlib.metadata import version, PackageNotFoundError
except Exception:
    try:
        from importlib_metadata import version, PackageNotFoundError
    except Exception:
        version = None
        PackageNotFoundError = Exception

# Trino imports
try:
    from trino.dbapi import connect
    from trino.auth import BasicAuthentication
except Exception:
    raise ImportError("Trino client not installed. Run: pip install trino")

# --------------------------------------
DEFAULT_PICKLE = "token.pkl"


class MaskedCreds(dict):
    """Dictionary wrapper that masks sensitive fields on print/repr."""
    SENSITIVE_KEYS = {"TRINO_USER", "TRINO_PASSWORD"}

    def __repr__(self):
        masked = {
            k: ("***masked***" if k in self.SENSITIVE_KEYS else v)
            for k, v in self.items()
        }
        return str(masked)


# --------------------------------------
# AUTO EMAIL DETECT
# --------------------------------------
def _detect_email():
    os_name = platform.system().lower()

    # Windows
    if "windows" in os_name:
        try:
            result = subprocess.run(
                "whoami /upn",
                capture_output=True,
                text=True,
                shell=True
            )
            email = result.stdout.strip()
            if "@" in email:
                return email
        except:
            pass

    # Mac
    if "darwin" in os_name:
        try:
            out = subprocess.check_output(["defaults", "read", "MobileMeAccounts"], text=True)
            import re
            emails = re.findall(r'"AccountID"\s*=\s*"([^"]+)"', out)
            if emails:
                return emails[0]
        except:
            pass

        # fallback git
        try:
            email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
            if "@" in email:
                return email
        except:
            pass

    # Linux
    if "linux" in os_name:
        try:
            email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
            if "@" in email:
                return email
        except:
            pass

    # last fallback
    return getpass.getuser()


# --------------------------------------
# FERNET Key
# --------------------------------------
def _to_fernet_key(keys1):
    if not isinstance(keys1, str) or not keys1:
        raise ValueError("keys1 must be non-empty")
    digest = hashlib.sha256(keys1.strip().lower().encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


# --------------------------------------
def load_token(pickle_file, _key_):
    if not os.path.exists(pickle_file):
        raise FileNotFoundError(f"{pickle_file} not found")

    fernet_key = _to_fernet_key(_key_)
    fernet = Fernet(fernet_key)

    with open(pickle_file, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted = fernet.decrypt(encrypted_data)
    except Exception as e:
        raise ValueError("Unauthorized User, Please enter correct mail") from e

    creds = pickle.loads(decrypted)
    if not isinstance(creds, dict):
        raise ValueError("Failed to fetch Credentials")

    if not creds.get("JUPYTERHUB_USER"):
        raise ValueError("Unauthorized User")

    return MaskedCreds(creds)


# --------------------------------------
# Ensure Latest toprocess
# --------------------------------------
def ensure_latest_toprocess(force_update=False):
    if version is None:
        print("Version check not supported; skipping toprocess verification")
        return

    # get local version
    try:
        local_ver = version("toprocess")
    except PackageNotFoundError:
        local_ver = None

    # get latest version online
    latest_ver = None
    try:
        resp = requests.get("https://pypi.org/pypi/toprocess/json", timeout=5)
        resp.raise_for_status()
        latest_ver = resp.json()["info"]["version"]
    except Exception as e:
        logging.warning(f"Could not fetch latest version info: {e}")
        return

    if force_update or local_ver != latest_ver:
        print(f"Installing/Updating toprocess (local: {local_ver}, latest: {latest_ver}) ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "toprocess"])
        except Exception as e:
            print("Failed to update toprocess:", e)
            return

        # reload if importable
        try:
            import importlib
            if "toprocess" in sys.modules:
                importlib.reload(sys.modules["toprocess"])
        except:
            pass
    else:
        print(f"toprocess is up-to-date (version {local_ver})")


# --------------------------------------
# TRINO
# --------------------------------------
def fetch_trino_data(query, pickle_file=DEFAULT_PICKLE, entered_email=None):

    ensure_latest_toprocess()

    # auto email
    if not entered_email:
        entered_email = _detect_email()

    if not entered_email:
        print("Email not detected. Aborting.")
        return None

    # load credentials
    try:
        creds = load_token(pickle_file, entered_email)
    except Exception as e:
        logging.error(f"Failed to load credentials: {e}")
        print(f"Failed to load credentials: {e}")
        return None

    try:
        user_type = creds["USER_TYPE"]
        user_name = creds["TRINO_USER"]
        password = creds["TRINO_PASSWORD"]
        host = creds["TRINO_HOST"]
        port = int(creds.get("TRINO_PORT", 443))
        http_scheme = creds.get("TRINO_HTTP_SCHEME", "https")
        jupyter_user_email = creds["JUPYTERHUB_USER"]
    except KeyError as ke:
        print(f"Missing required Trino credential key: {ke}")
        return None

    logged_user = getpass.getuser()
    pc_name = platform.node()

    comment = (
        f"/*email:{entered_email}, jupyter_user:{jupyter_user_email}, "
        f"logged_user:{logged_user}, pc_name:{pc_name}, user_type={user_type}*/ "
    )
    modified_query = comment + query

    try:
        print(f"Connecting to Trino as {user_name} (jupyter_user={jupyter_user_email})")

        conn = connect(
            host=host,
            port=port,
            user=user_name,
            auth=BasicAuthentication(user_name, password),
            http_scheme=http_scheme,
        )
        cur = conn.cursor()
        cur.execute(modified_query)
        results = cur.fetchall()

        try:
            import pandas as pd
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            cur.close()
            conn.close()
            print("Query executed successfully.")
            return df
        except Exception:
            cur.close()
            conn.close()
            return results

    except Exception as e:
        print(f"Error executing query: {e}")
        return None
