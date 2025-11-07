#!/usr/bin/env python3
import json
import io
import os
import sys
import zipfile
from typing import Dict, Any, Tuple, List, Optional

import requests
import xml.etree.ElementTree as ET

# Project-local imports:
# Ensure your sys.path points to the folder where these modules live, similar to your tests.
# For example, uncomment and adapt if needed:
# current_file = os.path.abspath(__file__)
# current_dir = os.path.dirname(current_file)
# project_root = os.path.dirname(current_dir)
# sys.path.append(os.path.join(project_root, "src", "Encorsa_e_Factura"))

try:
    from sincronizare import XMLProcessor  # requires the upgraded class with compile_template()
except:
    from .sincronizare import XMLProcessor
    
try:
    from XMLFromTemplateBuilder import XMLFromTemplateBuilder
except:
    from .XMLFromTemplateBuilder import XMLFromTemplateBuilder
    
try:
    from AnafUtils import get_token_with_refresh
except:
    from .AnafUtils import get_token_with_refresh

def _bool_str(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip().upper()
    return "DA" if s == "DA" else None


def _build_upload_url(env: str, params: Dict[str, Any]) -> str:
    """
    Build the ANAF upload URL with required and optional query parameters.
    env: "test" or "prod"
    params: must include "standard" and "cif"; may include "extern", "autofactura", "executare".
    """
    base = f"https://api.anaf.ro/{'test' if env.lower() == 'test' else 'prod'}/FCTEL/rest/upload"
    # Required
    q = [("standard", params["standard"]), ("cif", params["cif"])]
    # Optional flags (only accept "DA")
    for key in ("extern", "autofactura", "executare"):
        val = _bool_str(params.get(key))
        if val:
            q.append((key, val))
    # Assemble
    from urllib.parse import urlencode
    return f"{base}?{urlencode(q)}"


def _ensure_bytes(data, encoding="utf-8") -> bytes:
    if data is None:
        return b""
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    return str(data).encode(encoding or "utf-8", errors="replace")


def _zip_bytes(filename: str, content: bytes) -> bytes:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, content)
    return mem.getvalue()


def send_invoice_anaf(
    data_json_str: str,
    template_xml_path: str,
    extras_json_str: str,
) -> Tuple[int, Dict[str, Any]]:
    """
    Build XML from template + data_by_guid and POST it to ANAF using OAuth2.
    Returns (status_code, response_json_or_text_as_dict).

    Parameters:
      - data_json_str: JSON string with scalars and list rows keyed by GUIDs and list_id, respectively.
      - template_xml_path: file path to template used to compile scalars/item_lists_dict.
      - extras_json_str: JSON string containing:
          {
            "env": "test" | "prod",                         # default: "test"
            "namespaces": {...},                            # prefix -> URI
            "standard": "UBL|CN|CII|RASP",                  # required
            "cif": "########",                              # required numeric string
            "extern": "DA", "autofactura": "DA", "executare": "DA",  # optional flags
            "oauth": {"client_id": "...", "client_secret": "...", "refresh_token": "...", "parameters": {...}},
            "serialization": {"root_hint": "/ubl:Invoice", "xml_declaration": true, "encoding": "utf-8"},
            "upload": {"as_multipart": false, "multipart_field_name": "file", "zip": false, "zip_entry_name": "invoice.xml", "timeout_seconds": 60}
          }
    """
    # 1) Parse inputs
    try:
        data_by_guid: Dict[str, Any] = json.loads(data_json_str)
    except Exception as exc:
        raise ValueError(f"Invalid data_json_str: {exc}")

    try:
        extras: Dict[str, Any] = json.loads(extras_json_str)
    except Exception as exc:
        raise ValueError(f"Invalid extras_json_str: {exc}")

    env = (extras.get("env") or "test").lower()
    namespaces = extras.get("namespaces") or {}
    # Required ANAF query params
    standard = extras.get("standard")
    cif = extras.get("cif")
    if not standard or not cif:
        raise ValueError("extras_json_str must include 'standard' and 'cif'")

    # 2) Compile template to scalars + item_lists_dict
    xp = XMLProcessor(template_xml_path, namespaces=namespaces)
    scalars_map, item_lists_dict, _ = xp.compile_template()  # requires your upgraded XMLProcessor

    # 3) Build XML using your builder
    serialization = extras.get("serialization") or {}
    root_hint = serialization.get("root_hint")
    xml_decl = bool(serialization.get("xml_declaration", True))
    encoding = serialization.get("encoding") or "utf-8"

    builder = XMLFromTemplateBuilder(namespaces)
    xml_str = builder.build_document(
        scalars=scalars_map,
        item_lists_dict=item_lists_dict,
        data_by_guid=data_by_guid,
        root_hint=root_hint,
        xml_declaration=xml_decl,
        encoding=encoding,
        as_string=True,
    )
    xml_bytes = _ensure_bytes(xml_str, encoding=encoding)

    # 4) OAuth2: obtain access token using provided refresh token
    oauth = extras.get("oauth") or {}
    client_id = oauth.get("client_id")
    client_secret = oauth.get("client_secret")
    refresh_token = oauth.get("refresh_token")
    token_params = oauth.get("parameters") or {}

    if not (client_id and client_secret and refresh_token):
        raise ValueError("extras_json_str.oauth must include client_id, client_secret, and refresh_token")

    token_info = get_token_with_refresh(refresh_token, client_id, client_secret, token_params)
    # token_info is expected to have 'access_token' (adapt if your util returns a different structure)
    access_token = token_info.get("access_token") if isinstance(token_info, dict) else None
    if not access_token:
        raise RuntimeError("Could not obtain access_token from get_token_with_refresh")

    # 5) Build endpoint URL and headers
    upload_params = {
        "standard": standard,
        "cif": str(cif).strip(),
        "extern": extras.get("extern"),
        "autofactura": extras.get("autofactura"),
        "executare": extras.get("executare"),
    }
    url = _build_upload_url(env, upload_params)

    headers = {
        "Authorization": f"Bearer {access_token}",
        # Content-Type may be set by 'requests' when using 'files' for multipart
        # For raw XML body, explicitly set application/xml
    }

    upload_cfg = extras.get("upload") or {}
    as_multipart = bool(upload_cfg.get("as_multipart", False))
    multipart_field_name = upload_cfg.get("multipart_field_name") or "file"
    do_zip = bool(upload_cfg.get("zip", False))
    zip_entry_name = upload_cfg.get("zip_entry_name") or "invoice.xml"
    timeout_seconds = int(upload_cfg.get("timeout_seconds", 60))

    payload_bytes = xml_bytes
    if do_zip:
        payload_bytes = _zip_bytes(zip_entry_name, xml_bytes)

    # 6) Send request
    try:
        if as_multipart:
            # Multipart form-data (field name configurable)
            files = {
                multipart_field_name: (
                    zip_entry_name + (".zip" if do_zip else ""),
                    payload_bytes,
                    "application/zip" if do_zip else "application/xml",
                )
            }
            resp = requests.post(url, headers=headers, files=files, timeout=timeout_seconds)
        else:
            # Raw body (default to application/xml or application/zip)
            headers = {**headers}
            headers["Content-Type"] = "application/zip" if do_zip else "application/xml"
            resp = requests.post(url, headers=headers, data=payload_bytes, timeout=timeout_seconds)

        # Try parse JSON, else return text
        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, {"text": resp.text}

    except requests.RequestException as exc:
        return 0, {"error": str(exc), "url": url}


# Optional CLI wrapper for quick manual runs
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Send UBL/CN XML to ANAF using OAuth2")
    ap.add_argument("--data-json", required=True, help="JSON string or @path/to/file.json with GUID-keyed data")
    ap.add_argument("--template", required=True, help="Path to XML template")
    ap.add_argument("--extras-json", required=True, help="JSON string or @path/to/file.json with namespaces, env, oauth, and upload options")
    args = ap.parse_args()

    def _load_arg_json(s: str) -> str:
        if s.startswith("@"):
            with open(s[1:], "r", encoding="utf-8") as f:
                return f.read()
        return s

    data_json_str = _load_arg_json(args.data_json)
    extras_json_str = _load_arg_json(args.extras_json)

    code, body = send_invoice_anaf(data_json_str, args.template, extras_json_str)
    print(f"HTTP {code}")
    print(json.dumps(body, indent=2, ensure_ascii=False))
