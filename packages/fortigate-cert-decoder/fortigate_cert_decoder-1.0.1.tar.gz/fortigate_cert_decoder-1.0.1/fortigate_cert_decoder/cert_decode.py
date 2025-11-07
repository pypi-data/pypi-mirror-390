import requests
import json
import argparse
import warnings
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.utils import CryptographyDeprecationWarning
from datetime import datetime, timezone
import urllib3

# Disable all warnings for cleaner output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)

console = Console()

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
        console.print("[red]✗ Login failed. Please check credentials.[/red]")
        return

    console.print(f"[green]✓ Logged in successfully to {host}[/green]\n")

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
        console.print(f"[red]✗ Certificate '{cert_name}' not found.[/red]")
        return

    # Extract cert_pem based on cert_type
    if cert_type == "ca":
        cert_pem = cert_data["result"][0]["data"]["ca"][0]
    else:  # local
        cert_pem = cert_data["result"][0]["data"]["local"][0]["certificate"]

    # Decode the certificate
    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())

    # Check if certificate is still valid
    now = datetime.now(timezone.utc)
    
    # Handle both old and new cryptography library attribute names
    try:
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
    except AttributeError:
        # Older versions use not_valid_before/not_valid_after without _utc suffix
        not_before = cert.not_valid_before.replace(tzinfo=timezone.utc) if cert.not_valid_before.tzinfo is None else cert.not_valid_before
        not_after = cert.not_valid_after.replace(tzinfo=timezone.utc) if cert.not_valid_after.tzinfo is None else cert.not_valid_after
    
    is_valid = not_before <= now <= not_after
    status = "[green]✓ Valid[/green]" if is_valid else "[red]✗ Expired/Not Yet Valid[/red]"

    # Parse subject and issuer into readable format
    subject_parts = []
    for attr in cert.subject:
        subject_parts.append(f"{attr.oid._name}: {attr.value}")
    
    issuer_parts = []
    for attr in cert.issuer:
        issuer_parts.append(f"{attr.oid._name}: {attr.value}")

    # Create main info table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan bold", width=20)
    table.add_column("Value", style="white")
    
    table.add_row("Certificate Type", cert_type.upper())
    table.add_row("Certificate Name", cert_name)
    table.add_row("Status", status)
    table.add_row("Serial Number", str(cert.serial_number))
    table.add_row("Valid From", not_before.strftime("%Y-%m-%d %H:%M:%S UTC"))
    table.add_row("Valid Until", not_after.strftime("%Y-%m-%d %H:%M:%S UTC"))
    table.add_row("Signature Algorithm", cert.signature_algorithm_oid._name)

    # Get SANs
    san_list = []
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san_list = [str(name) for name in san.value]
    except x509.ExtensionNotFound:
        san_list = ["None"]

    # Get Key Usage
    key_usage_list = []
    try:
        key_usage = cert.extensions.get_extension_for_class(x509.KeyUsage)
        if key_usage.value.digital_signature:
            key_usage_list.append("Digital Signature")
        if key_usage.value.key_encipherment:
            key_usage_list.append("Key Encipherment")
        if key_usage.value.key_cert_sign:
            key_usage_list.append("Certificate Signing")
        if key_usage.value.crl_sign:
            key_usage_list.append("CRL Signing")
        if key_usage.value.key_agreement:
            key_usage_list.append("Key Agreement")
    except x509.ExtensionNotFound:
        key_usage_list = ["None"]

    # Print certificate details in a panel
    console.print(Panel(table, title=f"[bold white]Certificate Details[/bold white]", border_style="cyan"))
    
    # Subject details
    console.print("\n[bold cyan]Subject:[/bold cyan]")
    for part in subject_parts:
        console.print(f"  • {part}")
    
    # Issuer details
    console.print("\n[bold cyan]Issuer:[/bold cyan]")
    for part in issuer_parts:
        console.print(f"  • {part}")
    
    # SANs
    console.print("\n[bold cyan]Subject Alternative Names:[/bold cyan]")
    for san_item in san_list:
        console.print(f"  • {san_item}")
    
    # Key Usage
    console.print("\n[bold cyan]Key Usage:[/bold cyan]")
    for usage in key_usage_list:
        console.print(f"  • {usage}")
    
    console.print()  # Empty line at end


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