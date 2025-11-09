"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

CLI command: config generate (Simple configuration generator)
"""

from __future__ import annotations

import argparse
import sys
from argparse import Namespace

from mcp_proxy_adapter.core.config.simple_config_generator import SimpleConfigGenerator


def config_generate_command(args: Namespace) -> int:
    generator = SimpleConfigGenerator()
    out = generator.generate(
        protocol=args.protocol,
        with_proxy=args.with_proxy,
        out_path=args.out,
        # Server parameters
        server_host=getattr(args, "server_host", None),
        server_port=getattr(args, "server_port", None),
        server_cert_file=getattr(args, "server_cert_file", None),
        server_key_file=getattr(args, "server_key_file", None),
        server_ca_cert_file=getattr(args, "server_ca_cert_file", None),
        server_crl_file=getattr(args, "server_crl_file", None),
        # Client parameters
        client_enabled=getattr(args, "client_enabled", False),
        client_protocol=getattr(args, "client_protocol", None),
        client_cert_file=getattr(args, "client_cert_file", None),
        client_key_file=getattr(args, "client_key_file", None),
        client_ca_cert_file=getattr(args, "client_ca_cert_file", None),
        client_crl_file=getattr(args, "client_crl_file", None),
        # Registration parameters
        registration_host=getattr(args, "registration_host", None),
        registration_port=getattr(args, "registration_port", None),
        registration_protocol=getattr(args, "registration_protocol", None),
        registration_cert_file=getattr(args, "registration_cert_file", None),
        registration_key_file=getattr(args, "registration_key_file", None),
        registration_ca_cert_file=getattr(args, "registration_ca_cert_file", None),
        registration_crl_file=getattr(args, "registration_crl_file", None),
    )
    print(f"✅ Configuration generated: {out}")
    return 0


def main() -> int:
    """Main entry point for adapter-cfg-gen CLI command."""
    parser = argparse.ArgumentParser(
        prog="adapter-cfg-gen",
        description="Generate simple configuration file for MCP Proxy Adapter"
    )
    parser.add_argument(
        '--protocol',
        required=True,
        choices=['http', 'https', 'mtls'],
        help='Server/proxy protocol'
    )
    parser.add_argument(
        '--with-proxy',
        action='store_true',
        help='Enable proxy registration (deprecated, use --registration-* parameters)'
    )
    parser.add_argument(
        '--out',
        default='config.json',
        help='Output config path (default: config.json)'
    )
    
    # Server parameters
    parser.add_argument('--server-host', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--server-port', type=int, help='Server port (default: 8080)')
    parser.add_argument('--server-cert-file', help='Server certificate file path')
    parser.add_argument('--server-key-file', help='Server key file path')
    parser.add_argument('--server-ca-cert-file', help='Server CA certificate file path')
    parser.add_argument('--server-crl-file', help='Server CRL file path')
    
    # Client parameters
    parser.add_argument('--client-enabled', action='store_true', help='Enable client configuration')
    parser.add_argument('--client-protocol', choices=['http', 'https', 'mtls'], help='Client protocol')
    parser.add_argument('--client-cert-file', help='Client certificate file path')
    parser.add_argument('--client-key-file', help='Client key file path')
    parser.add_argument('--client-ca-cert-file', help='Client CA certificate file path')
    parser.add_argument('--client-crl-file', help='Client CRL file path')
    
    # Registration parameters
    parser.add_argument('--registration-host', help='Registration proxy host (default: localhost)')
    parser.add_argument('--registration-port', type=int, help='Registration proxy port (default: 3005)')
    parser.add_argument('--registration-protocol', choices=['http', 'https', 'mtls'], help='Registration protocol')
    parser.add_argument('--registration-cert-file', help='Registration certificate file path')
    parser.add_argument('--registration-key-file', help='Registration key file path')
    parser.add_argument('--registration-ca-cert-file', help='Registration CA certificate file path')
    parser.add_argument('--registration-crl-file', help='Registration CRL file path')
    
    args = parser.parse_args()
    return config_generate_command(args)


if __name__ == "__main__":
    sys.exit(main())


