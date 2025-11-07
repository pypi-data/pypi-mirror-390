import requests
import json
import argparse
from rich import print
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timezone
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def decode_certificate(host, cert_name, username, password, cert_type):
    """Decode a certificate from a FortiGate device."""
    url = f"https://{host}/jsonrpc"
    
    # Login
    payload = {
        "id": 1,
        "method": "exec",
        "params": [
            {
                "data": [
                    {
                        "passwd": password,
                        "user": username
                    }
                ],
                "url": "sys/login/user"
            }
        ],
        "session": None
    }

    response = requests.post(url, json=payload, verify=False)
    session_id = response.json().get('session', None)

    if session_id is None:
        print("[red]Login failed. Please check credentials.[/red]")
        return

    print(f"[green]✓ Logged in successfully[/green]")

    # Get certificate based on type
    get_cert_payload = {
        "method": "get",
        "params": [
            {
                "url": f"/cli/global/system/certificate/{cert_type}/{cert_name}"
            }
        ],
        "session": session_id,
        "id": 1
    }

    cert_response = requests.post(url, json=get_cert_payload, verify=False)
    cert_data = cert_response.json()

    if "result" not in cert_data or not cert_data["result"]:
        print(f"[red]Certificate '{cert_name}' not found.[/red]")
        return

    # Extract cert_pem based on cert_type
    if cert_type == "ca":
        cert_pem = cert_data["result"][0]["data"]["ca"][0]
    else:  # local
        cert_pem = cert_data["result"][0]["data"]["local"][0]["certificate"]

    # Decode the certificate
    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())

    print(f"\n[bold cyan]Certificate Details ({cert_type.upper()}):[/bold cyan]")
    print(f"[yellow]Subject:[/yellow] {cert.subject.rfc4514_string()}")
    print(f"[yellow]Issuer:[/yellow] {cert.issuer.rfc4514_string()}")
    print(f"[yellow]Serial Number:[/yellow] {cert.serial_number}")
    print(f"[yellow]Not Valid Before:[/yellow] {cert.not_valid_before_utc}")
    print(f"[yellow]Not Valid After:[/yellow] {cert.not_valid_after_utc}")
    print(f"[yellow]Signature Algorithm:[/yellow] {cert.signature_algorithm_oid._name}")

    # Check if certificate is still valid
    now = datetime.now(timezone.utc)
    if cert.not_valid_before_utc <= now <= cert.not_valid_after_utc:
        print(f"[green]Status: Valid ✓[/green]")
    else:
        print(f"[red]Status: Expired or Not Yet Valid ✗[/red]")

    print(f"\n[yellow]Subject Alternative Names:[/yellow]")
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        for name in san.value:
            print(f"  - {name}")
    except x509.ExtensionNotFound:
        print("  None")

    print(f"\n[yellow]Key Usage:[/yellow]")
    try:
        key_usage = cert.extensions.get_extension_for_class(x509.KeyUsage)
        print(f"  {key_usage.value}")
    except x509.ExtensionNotFound:
        print("  None")


def main():
    parser = argparse.ArgumentParser(description='Decode certificates from FortiGate devices')
    parser.add_argument('host', help='FortiGate host IP or hostname')
    parser.add_argument('cert_name', help='Name of the certificate to decode')
    parser.add_argument('-u', '--username', default='jsonadmin', help='Username (default: jsonadmin)')
    parser.add_argument('-p', '--password', required=True, help='Password')
    parser.add_argument('-t', '--type', dest='cert_type', choices=['ca', 'local'], default='ca',
                        help='Certificate type: ca or local (default: ca)')
    
    args = parser.parse_args()
    
    decode_certificate(args.host, args.cert_name, args.username, args.password, args.cert_type)


if __name__ == "__main__":
    main()