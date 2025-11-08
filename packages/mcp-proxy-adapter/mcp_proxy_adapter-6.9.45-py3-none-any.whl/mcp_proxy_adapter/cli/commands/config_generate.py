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
        server_host=getattr(args, "server_host", None),
        server_port=getattr(args, "server_port", None),
        server_cert_file=getattr(args, "server_cert_file", None),
        server_key_file=getattr(args, "server_key_file", None),
        server_ca_cert_file=getattr(args, "server_ca_cert_file", None),
        proxy_host=getattr(args, "proxy_host", None),
        proxy_port=getattr(args, "proxy_port", None),
        proxy_cert_file=getattr(args, "proxy_cert_file", None),
        proxy_key_file=getattr(args, "proxy_key_file", None),
        proxy_ca_cert_file=getattr(args, "proxy_ca_cert_file", None),
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
        help='Include proxy_client section'
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
    
    # Proxy parameters
    parser.add_argument('--proxy-host', help='Proxy host (default: localhost)')
    parser.add_argument('--proxy-port', type=int, help='Proxy port (default: 3005)')
    parser.add_argument('--proxy-cert-file', help='Proxy client certificate file path')
    parser.add_argument('--proxy-key-file', help='Proxy client key file path')
    parser.add_argument('--proxy-ca-cert-file', help='Proxy CA certificate file path')
    
    args = parser.parse_args()
    return config_generate_command(args)


if __name__ == "__main__":
    sys.exit(main())


