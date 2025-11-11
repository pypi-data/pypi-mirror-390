#!/usr/bin/env python3
"""Release and download monitoring utility for Riveter.

This script provides utilities for monitoring binary downloads, installation
success rates, and alerting on failed binary builds or formula updates.

Usage:
    python scripts/monitor_releases.py download-stats --version 1.2.3
    python scripts/monitor_releases.py check-builds --days 7
    python scripts/monitor_releases.py alert-failures --webhook-url https://hooks.slack.com/...
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ReleaseMonitor:
    """Monitors Riveter releases, downloads, and build status."""

    GITHUB_REPO = "riveter/riveter"
    HOMEBREW_TAP_REPO = "ScottRyanHoward/homebrew-riveter"
    SUPPORTED_PLATFORMS = ["macos-intel", "macos-arm64", "linux-x86_64"]

    def __init__(self, github_token: Optional[str] = None, debug: bool = False):
        """Initialize the release monitor.

        Args:
            github_token: GitHub token for API access (optional, increases rate limits)
            debug: Enable debug mode for verbose output
        """
        self.github_token = github_token
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)

        # Create monitoring data directory
        self.data_dir = Path("monitoring")
        self.data_dir.mkdir(exist_ok=True)

        self.stats_file = self.data_dir / "download_stats.json"
        self.build_log_file = self.data_dir / "build_status.json"

        # Setup API headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Riveter-Release-Monitor/1.0",
        }

        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

    def get_release_info(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Get release information from GitHub API.

        Args:
            version: Specific version to get info for, or None for latest

        Returns:
            Release information dictionary

        Raises:
            RuntimeError: If API request fails
        """
        if version:
            # Get specific release
            if not version.startswith("v"):
                version = f"v{version}"
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/tags/{version}"
        else:
            # Get latest release
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"

        logger.debug(f"Fetching release info from: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch release info: {e}") from e

    def get_download_stats(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Get download statistics for a release.

        Args:
            version: Version to get stats for, or None for latest

        Returns:
            Download statistics dictionary
        """
        logger.info(f"Fetching download stats for version: {version or 'latest'}")

        try:
            release_info = self.get_release_info(version)

            stats = {
                "version": release_info["tag_name"],
                "published_at": release_info["published_at"],
                "total_downloads": 0,
                "assets": {},
                "platforms": {},
            }

            # Process each asset
            for asset in release_info.get("assets", []):
                asset_name = asset["name"]
                download_count = asset["download_count"]

                stats["assets"][asset_name] = {
                    "download_count": download_count,
                    "size": asset["size"],
                    "created_at": asset["created_at"],
                    "updated_at": asset["updated_at"],
                }

                stats["total_downloads"] += download_count

                # Categorize by platform
                for platform in self.SUPPORTED_PLATFORMS:
                    if platform in asset_name:
                        if platform not in stats["platforms"]:
                            stats["platforms"][platform] = {"total_downloads": 0, "assets": []}

                        stats["platforms"][platform]["total_downloads"] += download_count
                        stats["platforms"][platform]["assets"].append(
                            {"name": asset_name, "downloads": download_count, "size": asset["size"]}
                        )
                        break

            logger.debug(f"Download stats: {json.dumps(stats, indent=2)}")
            return stats

        except Exception as e:
            logger.error(f"Failed to get download stats: {e}")
            return {}

    def save_download_stats(self, stats: Dict[str, Any]) -> None:
        """Save download statistics to file.

        Args:
            stats: Download statistics to save
        """
        try:
            # Load existing stats
            existing_stats = []
            if self.stats_file.exists():
                with open(self.stats_file, "r") as f:
                    existing_stats = json.load(f)

            # Add timestamp
            stats["collected_at"] = datetime.now(timezone.utc).isoformat()

            # Append new stats
            existing_stats.append(stats)

            # Keep only last 100 entries
            if len(existing_stats) > 100:
                existing_stats = existing_stats[-100:]

            # Save updated stats
            with open(self.stats_file, "w") as f:
                json.dump(existing_stats, f, indent=2)

            logger.debug(f"Saved download stats to {self.stats_file}")

        except Exception as e:
            logger.error(f"Failed to save download stats: {e}")

    def get_workflow_runs(self, workflow_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent workflow runs for monitoring.

        Args:
            workflow_name: Name of the workflow file (e.g., "release-binaries.yml")
            days: Number of days to look back

        Returns:
            List of workflow run information
        """
        since_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        url = f"https://api.github.com/repos/{self.GITHUB_REPO}/actions/workflows/{workflow_name}/runs"
        params = {"per_page": 50, "created": f">={since_date}"}

        logger.debug(f"Fetching workflow runs from: {url}")

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data.get("workflow_runs", [])

        except requests.RequestException as e:
            logger.error(f"Failed to fetch workflow runs: {e}")
            return []

    def check_build_status(self, days: int = 7) -> Dict[str, Any]:
        """Check the status of recent binary builds.

        Args:
            days: Number of days to check

        Returns:
            Build status summary
        """
        logger.info(f"Checking build status for last {days} days")

        # Get workflow runs for binary builds
        binary_runs = self.get_workflow_runs("release-binaries.yml", days)
        release_runs = self.get_workflow_runs("release.yml", days)

        status = {
            "period_days": days,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "binary_builds": {
                "total": len(binary_runs),
                "successful": 0,
                "failed": 0,
                "in_progress": 0,
                "cancelled": 0,
                "failures": [],
            },
            "releases": {
                "total": len(release_runs),
                "successful": 0,
                "failed": 0,
                "in_progress": 0,
                "cancelled": 0,
                "failures": [],
            },
        }

        # Analyze binary build runs
        for run in binary_runs:
            conclusion = run.get("conclusion")
            status_val = run.get("status")

            if status_val == "completed":
                if conclusion == "success":
                    status["binary_builds"]["successful"] += 1
                elif conclusion == "failure":
                    status["binary_builds"]["failed"] += 1
                    status["binary_builds"]["failures"].append(
                        {
                            "run_id": run["id"],
                            "created_at": run["created_at"],
                            "head_sha": run["head_sha"],
                            "html_url": run["html_url"],
                        }
                    )
                elif conclusion == "cancelled":
                    status["binary_builds"]["cancelled"] += 1
            else:
                status["binary_builds"]["in_progress"] += 1

        # Analyze release runs
        for run in release_runs:
            conclusion = run.get("conclusion")
            status_val = run.get("status")

            if status_val == "completed":
                if conclusion == "success":
                    status["releases"]["successful"] += 1
                elif conclusion == "failure":
                    status["releases"]["failed"] += 1
                    status["releases"]["failures"].append(
                        {
                            "run_id": run["id"],
                            "created_at": run["created_at"],
                            "head_sha": run["head_sha"],
                            "html_url": run["html_url"],
                        }
                    )
                elif conclusion == "cancelled":
                    status["releases"]["cancelled"] += 1
            else:
                status["releases"]["in_progress"] += 1

        return status

    def save_build_status(self, status: Dict[str, Any]) -> None:
        """Save build status to file.

        Args:
            status: Build status to save
        """
        try:
            # Load existing status logs
            existing_logs = []
            if self.build_log_file.exists():
                with open(self.build_log_file, "r") as f:
                    existing_logs = json.load(f)

            # Append new status
            existing_logs.append(status)

            # Keep only last 50 entries
            if len(existing_logs) > 50:
                existing_logs = existing_logs[-50:]

            # Save updated logs
            with open(self.build_log_file, "w") as f:
                json.dump(existing_logs, f, indent=2)

            logger.debug(f"Saved build status to {self.build_log_file}")

        except Exception as e:
            logger.error(f"Failed to save build status: {e}")

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate dashboard data combining stats and build status.

        Returns:
            Dashboard data dictionary
        """
        dashboard = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "download_stats": {},
            "build_status": {},
            "alerts": [],
        }

        try:
            # Get latest download stats
            if self.stats_file.exists():
                with open(self.stats_file, "r") as f:
                    stats_history = json.load(f)
                    if stats_history:
                        dashboard["download_stats"] = stats_history[-1]

            # Get latest build status
            if self.build_log_file.exists():
                with open(self.build_log_file, "r") as f:
                    build_history = json.load(f)
                    if build_history:
                        dashboard["build_status"] = build_history[-1]

            # Generate alerts
            build_status = dashboard.get("build_status", {})

            # Alert on failed builds
            binary_failures = build_status.get("binary_builds", {}).get("failed", 0)
            if binary_failures > 0:
                dashboard["alerts"].append(
                    {
                        "type": "build_failure",
                        "severity": "high",
                        "message": (
                            f"{binary_failures} binary build(s) failed in the last "
                            f"{build_status.get('period_days', 7)} days"
                        ),
                        "details": build_status.get("binary_builds", {}).get("failures", []),
                    }
                )

            release_failures = build_status.get("releases", {}).get("failed", 0)
            if release_failures > 0:
                dashboard["alerts"].append(
                    {
                        "type": "release_failure",
                        "severity": "high",
                        "message": (
                            f"{release_failures} release(s) failed in the last "
                            f"{build_status.get('period_days', 7)} days"
                        ),
                        "details": build_status.get("releases", {}).get("failures", []),
                    }
                )

            # Alert on low download counts (if we have historical data)
            download_stats = dashboard.get("download_stats", {})
            total_downloads = download_stats.get("total_downloads", 0)
            if total_downloads == 0 and download_stats:
                dashboard["alerts"].append(
                    {
                        "type": "no_downloads",
                        "severity": "medium",
                        "message": (
                            f"No downloads recorded for version "
                            f"{download_stats.get('version', 'unknown')}"
                        ),
                        "details": {},
                    }
                )

        except Exception as e:
            logger.error(f"Failed to generate dashboard data: {e}")
            dashboard["alerts"].append(
                {
                    "type": "dashboard_error",
                    "severity": "medium",
                    "message": f"Error generating dashboard: {e}",
                    "details": {},
                }
            )

        return dashboard

    def send_alert(self, webhook_url: str, alert_data: Dict[str, Any]) -> bool:
        """Send alert to webhook (Slack, Discord, etc.).

        Args:
            webhook_url: Webhook URL to send alert to
            alert_data: Alert data to send

        Returns:
            True if alert sent successfully, False otherwise
        """
        try:
            # Format alert message
            alerts = alert_data.get("alerts", [])
            if not alerts:
                logger.info("No alerts to send")
                return True

            # Create message
            message_parts = ["🚨 Riveter Release Monitoring Alert"]

            for alert in alerts:
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    alert["severity"], "ℹ️"
                )

                message_parts.append(f"{severity_emoji} {alert['message']}")

                # Add details for failures
                if alert["type"] in ["build_failure", "release_failure"] and alert["details"]:
                    for failure in alert["details"][:3]:  # Limit to first 3 failures
                        message_parts.append(
                            f"  • Run ID: {failure['run_id']} - {failure['html_url']}"
                        )

            message = "\n".join(message_parts)

            # Send to webhook
            payload = {"text": message}

            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()

            logger.info("Alert sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False


def main() -> None:
    """Main entry point for the release monitoring script."""
    parser = argparse.ArgumentParser(
        description="Monitor Riveter releases and downloads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get download stats for latest release
  python scripts/monitor_releases.py download-stats

  # Get stats for specific version
  python scripts/monitor_releases.py download-stats --version 1.2.3

  # Check build status for last 7 days
  python scripts/monitor_releases.py check-builds --days 7

  # Generate dashboard data
  python scripts/monitor_releases.py dashboard

  # Send alerts to Slack webhook
  python scripts/monitor_releases.py alert-failures --webhook-url https://hooks.slack.com/...

Environment Variables:
  GITHUB_TOKEN - GitHub token for API access (optional, increases rate limits)
        """,
    )

    parser.add_argument(
        "command",
        choices=["download-stats", "check-builds", "dashboard", "alert-failures"],
        help="Command to execute",
    )

    parser.add_argument("--version", help="Specific version to get stats for (default: latest)")

    parser.add_argument("--days", type=int, default=7, help="Number of days to check (default: 7)")

    parser.add_argument("--webhook-url", help="Webhook URL for sending alerts")

    parser.add_argument("--save", action="store_true", help="Save results to monitoring files")

    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with verbose output"
    )

    args = parser.parse_args()

    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")

    try:
        monitor = ReleaseMonitor(github_token=github_token, debug=args.debug)

        if args.command == "download-stats":
            stats = monitor.get_download_stats(args.version)

            if not stats:
                print("❌ Failed to get download stats")
                sys.exit(1)

            print(f"📊 Download Statistics for {stats['version']}")
            print("=" * 50)
            print(f"Total Downloads: {stats['total_downloads']:,}")
            print(f"Published: {stats['published_at']}")
            print()

            print("Platform Breakdown:")
            for platform, data in stats["platforms"].items():
                print(f"  {platform}: {data['total_downloads']:,} downloads")
                for asset in data["assets"]:
                    size_mb = asset["size"] / (1024 * 1024)
                    print(
                        f"    • {asset['name']}: {asset['downloads']:,} downloads "
                        f"({size_mb:.1f} MB)"
                    )

            if args.save:
                monitor.save_download_stats(stats)
                print(f"\n✅ Stats saved to {monitor.stats_file}")

        elif args.command == "check-builds":
            status = monitor.check_build_status(args.days)

            print(f"🔨 Build Status (Last {args.days} days)")
            print("=" * 40)

            print("Binary Builds:")
            binary = status["binary_builds"]
            print(f"  Total: {binary['total']}")
            print(f"  ✅ Successful: {binary['successful']}")
            print(f"  ❌ Failed: {binary['failed']}")
            print(f"  🔄 In Progress: {binary['in_progress']}")
            print(f"  ⏹️ Cancelled: {binary['cancelled']}")

            print("\nReleases:")
            releases = status["releases"]
            print(f"  Total: {releases['total']}")
            print(f"  ✅ Successful: {releases['successful']}")
            print(f"  ❌ Failed: {releases['failed']}")
            print(f"  🔄 In Progress: {releases['in_progress']}")
            print(f"  ⏹️ Cancelled: {releases['cancelled']}")

            # Show recent failures
            if binary["failures"]:
                print("\nRecent Binary Build Failures:")
                for failure in binary["failures"][:3]:
                    print(f"  • {failure['created_at'][:10]} - Run {failure['run_id']}")
                    print(f"    {failure['html_url']}")

            if releases["failures"]:
                print("\nRecent Release Failures:")
                for failure in releases["failures"][:3]:
                    print(f"  • {failure['created_at'][:10]} - Run {failure['run_id']}")
                    print(f"    {failure['html_url']}")

            if args.save:
                monitor.save_build_status(status)
                print(f"\n✅ Status saved to {monitor.build_log_file}")

        elif args.command == "dashboard":
            dashboard = monitor.generate_dashboard_data()

            print("📈 Riveter Release Dashboard")
            print("=" * 30)
            print(f"Generated: {dashboard['generated_at'][:19]}Z")
            print()

            # Download stats summary
            download_stats = dashboard.get("download_stats", {})
            if download_stats:
                print(f"Latest Release: {download_stats.get('version', 'Unknown')}")
                print(f"Total Downloads: {download_stats.get('total_downloads', 0):,}")
                print()

            # Build status summary
            build_status = dashboard.get("build_status", {})
            if build_status:
                binary = build_status.get("binary_builds", {})
                releases = build_status.get("releases", {})

                print(f"Build Status ({build_status.get('period_days', 7)} days):")
                print(
                    f"  Binary Builds: {binary.get('successful', 0)}✅ {binary.get('failed', 0)}❌"
                )
                print(
                    f"  Releases: {releases.get('successful', 0)}✅ {releases.get('failed', 0)}❌"
                )
                print()

            # Alerts
            alerts = dashboard.get("alerts", [])
            if alerts:
                print("🚨 Active Alerts:")
                for alert in alerts:
                    severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                        alert["severity"], "ℹ️"
                    )
                    print(f"  {severity_emoji} {alert['message']}")
            else:
                print("✅ No active alerts")

            # Save dashboard data
            dashboard_file = monitor.data_dir / "dashboard.json"
            with open(dashboard_file, "w") as f:
                json.dump(dashboard, f, indent=2)
            print(f"\n📄 Dashboard data saved to {dashboard_file}")

        elif args.command == "alert-failures":
            if not args.webhook_url:
                parser.error("--webhook-url is required for alert-failures command")

            dashboard = monitor.generate_dashboard_data()

            if monitor.send_alert(args.webhook_url, dashboard):
                print("✅ Alert sent successfully")
            else:
                print("❌ Failed to send alert")
                sys.exit(1)

    except Exception as e:
        logger.error(f"Command failed: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
