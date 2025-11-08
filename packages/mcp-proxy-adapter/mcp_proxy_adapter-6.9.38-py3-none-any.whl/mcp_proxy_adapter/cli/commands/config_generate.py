"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

CLI command: config generate (Simple configuration generator)
"""

from __future__ import annotations

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


