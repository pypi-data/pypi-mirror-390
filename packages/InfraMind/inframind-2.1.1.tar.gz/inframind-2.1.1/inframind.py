#!/usr/bin/env python3
"""
InfraMind CLI - Easy integration with CI/CD pipelines

Usage:
    inframind optimize --repo myorg/myrepo --branch main
    inframind report --duration 180 --status success
    inframind config --url http://inframind:8081
"""

import argparse
import json
import os
import sys
from typing import Optional
import requests


class InfraMindClient:
    """Client for interacting with InfraMind API"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or os.getenv("INFRAMIND_URL", "http://localhost:8081")
        self.api_key = api_key or os.getenv("INFRAMIND_API_KEY")
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})

    def optimize(
        self,
        repo: str,
        branch: str = "main",
        build_type: str = "release",
        previous_duration: Optional[int] = None,
    ) -> dict:
        """Get optimization suggestions from InfraMind"""

        payload = {
            "repo": repo,
            "branch": branch,
            "build_type": build_type,
        }

        if previous_duration:
            payload["previous_duration"] = previous_duration

        try:
            response = self.session.post(
                f"{self.base_url}/optimize",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with InfraMind API: {e}", file=sys.stderr)
            sys.exit(1)

    def report(
        self,
        repo: str,
        branch: str,
        duration: int,
        status: str,
        cpu: Optional[int] = None,
        memory: Optional[int] = None,
        **kwargs,
    ) -> dict:
        """Report build results to InfraMind"""

        payload = {
            "repo": repo,
            "branch": branch,
            "duration": duration,
            "status": status,
        }

        if cpu:
            payload["cpu"] = cpu
        if memory:
            payload["memory"] = memory

        # Add any additional fields
        payload.update(kwargs)

        try:
            response = self.session.post(
                f"{self.base_url}/builds/complete",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error reporting to InfraMind API: {e}", file=sys.stderr)
            sys.exit(1)

    def health(self) -> dict:
        """Check InfraMind API health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking InfraMind health: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_optimize(args):
    """Handle optimize command"""
    client = InfraMindClient(args.url, args.api_key)

    result = client.optimize(
        repo=args.repo,
        branch=args.branch,
        build_type=args.build_type,
        previous_duration=args.previous_duration,
    )

    if args.format == "json":
        print(json.dumps(result, indent=2))
    elif args.format == "env":
        # Output as environment variables
        print(f"export INFRAMIND_CPU={result.get('cpu', '')}")
        print(f"export INFRAMIND_MEMORY={result.get('memory', '')}")
        print(f"export INFRAMIND_CONCURRENCY={result.get('concurrency', '')}")
        print(f"export INFRAMIND_CACHE_ENABLED={result.get('cache_enabled', '')}")
        print(
            f"export INFRAMIND_ESTIMATED_DURATION={result.get('estimated_duration', '')}"
        )
    elif args.format == "shell":
        # Output for direct shell evaluation
        print(f"INFRAMIND_CPU={result.get('cpu', '')}")
        print(f"INFRAMIND_MEMORY={result.get('memory', '')}")
        print(f"INFRAMIND_CONCURRENCY={result.get('concurrency', '')}")
        print(f"INFRAMIND_CACHE_ENABLED={result.get('cache_enabled', '')}")
        print(f"INFRAMIND_ESTIMATED_DURATION={result.get('estimated_duration', '')}")
    else:  # human-readable
        print(f"\n🚀 InfraMind Optimization Suggestions for {args.repo}@{args.branch}")
        print("=" * 70)
        print(f"  CPU:              {result.get('cpu', 'N/A')}")
        print(f"  Memory:           {result.get('memory', 'N/A')} MB")
        print(f"  Concurrency:      {result.get('concurrency', 'N/A')}")
        print(f"  Cache Enabled:    {result.get('cache_enabled', 'N/A')}")
        print(f"  Estimated Time:   {result.get('estimated_duration', 'N/A')}s")
        print(f"  Confidence:       {result.get('confidence', 'N/A'):.2%}")
        print(f"\n💡 Rationale: {result.get('rationale', 'N/A')}")
        print()


def cmd_report(args):
    """Handle report command"""
    client = InfraMindClient(args.url, args.api_key)

    result = client.report(
        repo=args.repo,
        branch=args.branch,
        duration=args.duration,
        status=args.status,
        cpu=args.cpu,
        memory=args.memory,
    )

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✅ Build results reported successfully!")
        print(f"   Repo:     {args.repo}@{args.branch}")
        print(f"   Duration: {args.duration}s")
        print(f"   Status:   {args.status}")
        print()


def cmd_health(args):
    """Handle health command"""
    client = InfraMindClient(args.url, args.api_key)

    result = client.health()

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        status = result.get("status", "unknown")
        if status == "healthy":
            print(f"✅ InfraMind API is healthy")
            print(f"   URL: {client.base_url}")
        else:
            print(f"⚠️  InfraMind API status: {status}")
            print(f"   URL: {client.base_url}")


def cmd_config(args):
    """Handle config command"""
    config_file = os.path.expanduser("~/.inframind/config")
    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)

    if args.url:
        config["url"] = args.url
    if args.api_key:
        config["api_key"] = args.api_key

    if args.url or args.api_key:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuration saved to {config_file}")
    else:
        print(f"📋 Current configuration:")
        print(f"   URL:     {config.get('url', 'Not set (using default)')}")
        print(f"   API Key: {'***' + config.get('api_key', '')[-8:] if config.get('api_key') else 'Not set'}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="InfraMind CLI - Intelligent CI/CD Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get optimization suggestions
  inframind optimize --repo myorg/myrepo --branch main

  # Report build results
  inframind report --repo myorg/myrepo --branch main --duration 180 --status success

  # Check API health
  inframind health

  # Configure CLI
  inframind config --url http://inframind.example.com --api-key YOUR_KEY

Environment Variables:
  INFRAMIND_URL       API base URL (default: http://localhost:8081)
  INFRAMIND_API_KEY   API authentication key
        """,
    )

    parser.add_argument(
        "--url",
        help="InfraMind API URL (overrides INFRAMIND_URL env var)",
    )
    parser.add_argument(
        "--api-key",
        help="API authentication key (overrides INFRAMIND_API_KEY env var)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Optimize command
    optimize_parser = subparsers.add_parser(
        "optimize", help="Get optimization suggestions"
    )
    optimize_parser.add_argument("--repo", required=True, help="Repository name")
    optimize_parser.add_argument(
        "--branch", default="main", help="Branch name (default: main)"
    )
    optimize_parser.add_argument(
        "--build-type", default="release", help="Build type (default: release)"
    )
    optimize_parser.add_argument(
        "--previous-duration",
        type=int,
        help="Previous build duration in seconds",
    )
    optimize_parser.add_argument(
        "--format",
        choices=["human", "json", "env", "shell"],
        default="human",
        help="Output format",
    )
    optimize_parser.set_defaults(func=cmd_optimize)

    # Report command
    report_parser = subparsers.add_parser("report", help="Report build results")
    report_parser.add_argument("--repo", required=True, help="Repository name")
    report_parser.add_argument(
        "--branch", default="main", help="Branch name (default: main)"
    )
    report_parser.add_argument(
        "--duration", type=int, required=True, help="Build duration in seconds"
    )
    report_parser.add_argument(
        "--status", required=True, choices=["success", "failure"], help="Build status"
    )
    report_parser.add_argument("--cpu", type=int, help="CPU cores used")
    report_parser.add_argument("--memory", type=int, help="Memory used in MB")
    report_parser.add_argument(
        "--format", choices=["human", "json"], default="human", help="Output format"
    )
    report_parser.set_defaults(func=cmd_report)

    # Health command
    health_parser = subparsers.add_parser("health", help="Check API health")
    health_parser.add_argument(
        "--format", choices=["human", "json"], default="human", help="Output format"
    )
    health_parser.set_defaults(func=cmd_health)

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage CLI configuration")
    config_parser.add_argument("--url", help="Set API URL")
    config_parser.add_argument("--api-key", help="Set API key")
    config_parser.set_defaults(func=cmd_config)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
