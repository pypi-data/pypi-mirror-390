"""FortiGate Certificate Decoder - A tool for retrieving and decoding certificates from FortiGate devices."""

__version__ = "1.0.0"
__author__ = "Todd Albiston"
__email__ = "foxtrot711@gmail.com"

from fortigate_cert_decoder.cert_decode import decode_certificate, main

__all__ = ["decode_certificate", "main"]
