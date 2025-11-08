"""Wayland setup and permission checker."""

import logging
import subprocess
import os
import grp
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class WaylandSetupChecker:
    """Check and guide Wayland-specific setup requirements."""

    def __init__(self):
        """Initialize Wayland setup checker."""
        self.issues: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []

    def check_all(self) -> Dict[str, any]:
        """
        Check all Wayland requirements.

        Returns:
            Dict with status and issues found
        """
        self.issues = []
        self.warnings = []

        # Check if we're on Wayland
        if not self._is_wayland():
            return {
                "is_wayland": False,
                "ready": True,
                "issues": [],
                "warnings": []
            }

        # Run checks
        self._check_ydotool()
        self._check_groups()
        self._check_udev_rules()
        self._check_uinput_module()

        return {
            "is_wayland": True,
            "ready": len(self.issues) == 0,
            "issues": self.issues,
            "warnings": self.warnings
        }

    def _is_wayland(self) -> bool:
        """Check if running on Wayland."""
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        return session_type == "wayland"

    def _check_ydotool(self):
        """Check if ydotool is installed."""
        try:
            result = subprocess.run(
                ["which", "ydotool"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode != 0:
                self.issues.append({
                    "title": "ydotool not installed",
                    "description": "ydotool is required for text injection on Wayland",
                    "solution": (
                        "Install ydotool:\n"
                        "  Debian/Ubuntu: sudo apt install ydotool\n"
                        "  Fedora: sudo dnf install ydotool\n"
                        "  Arch: sudo pacman -S ydotool"
                    )
                })
            else:
                logger.info("ydotool is installed")

        except Exception as e:
            logger.warning(f"Failed to check ydotool: {e}")
            self.warnings.append({
                "title": "Could not verify ydotool",
                "description": f"Check failed: {e}"
            })

    def _check_groups(self):
        """Check if user is in required groups."""
        try:
            username = os.getlogin()
            user_groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]

            required_groups = ["input", "uinput"]
            missing_groups = []

            for group in required_groups:
                if group not in user_groups:
                    # Check if group exists
                    try:
                        grp.getgrnam(group)
                        missing_groups.append(group)
                    except KeyError:
                        self.warnings.append({
                            "title": f"Group '{group}' does not exist",
                            "description": f"The system group '{group}' was not found. This may be normal on some distributions."
                        })

            if missing_groups:
                self.issues.append({
                    "title": f"Not in required groups: {', '.join(missing_groups)}",
                    "description": f"User must be in {', '.join(missing_groups)} groups for ydotool to work",
                    "solution": (
                        f"Add your user to the groups:\n"
                        f"  sudo usermod -aG {','.join(missing_groups)} $USER\n\n"
                        f"Then logout and login again for changes to take effect."
                    )
                })
            else:
                logger.info("User is in required groups")

        except Exception as e:
            logger.warning(f"Failed to check groups: {e}")
            self.warnings.append({
                "title": "Could not verify group membership",
                "description": f"Check failed: {e}"
            })

    def _check_udev_rules(self):
        """Check if udev rules for uinput are configured."""
        try:
            udev_rules_path = Path("/etc/udev/rules.d/80-uinput.rules")

            if not udev_rules_path.exists():
                self.warnings.append({
                    "title": "udev rules not found",
                    "description": "Recommended udev rules for uinput are not configured",
                    "solution": (
                        "Create udev rule:\n"
                        "  echo 'KERNEL==\"uinput\", MODE=\"0660\", GROUP=\"uinput\", OPTIONS+=\"static_node=uinput\"' | \\\n"
                        "    sudo tee /etc/udev/rules.d/80-uinput.rules\n\n"
                        "Then reload udev rules:\n"
                        "  sudo udevadm control --reload-rules\n"
                        "  sudo udevadm trigger"
                    )
                })
            else:
                # Check if rule is correct
                try:
                    content = udev_rules_path.read_text()
                    if "uinput" not in content.lower():
                        self.warnings.append({
                            "title": "udev rules may be incorrect",
                            "description": "The udev rules file exists but may not be configured correctly"
                        })
                    else:
                        logger.info("udev rules appear to be configured")
                except Exception as e:
                    logger.warning(f"Could not read udev rules: {e}")

        except Exception as e:
            logger.warning(f"Failed to check udev rules: {e}")

    def _check_uinput_module(self):
        """Check if uinput kernel module is loaded."""
        try:
            result = subprocess.run(
                ["lsmod"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if "uinput" not in result.stdout:
                self.warnings.append({
                    "title": "uinput module not loaded",
                    "description": "The uinput kernel module is not currently loaded",
                    "solution": (
                        "Load the module:\n"
                        "  sudo modprobe uinput\n\n"
                        "To load automatically on boot, add to /etc/modules:\n"
                        "  echo 'uinput' | sudo tee -a /etc/modules"
                    )
                })
            else:
                logger.info("uinput module is loaded")

        except Exception as e:
            logger.warning(f"Failed to check uinput module: {e}")

    def get_setup_guide(self) -> str:
        """
        Get complete setup guide for Wayland.

        Returns:
            Formatted setup guide text
        """
        guide = """
═══════════════════════════════════════════════════════════
           Talky - Wayland Setup Guide
═══════════════════════════════════════════════════════════

Talky requires additional setup on Wayland due to security restrictions.

STEP 1: Install ydotool
───────────────────────
Debian/Ubuntu:
  sudo apt install ydotool

Fedora:
  sudo dnf install ydotool

Arch Linux:
  sudo pacman -S ydotool


STEP 2: Add User to Groups
───────────────────────────
  sudo usermod -aG input,uinput $USER

IMPORTANT: You must logout and login again for this to take effect!


STEP 3: Configure udev Rules
─────────────────────────────
Create udev rule for uinput:
  echo 'KERNEL=="uinput", MODE="0660", GROUP="uinput", OPTIONS+="static_node=uinput"' | \\
    sudo tee /etc/udev/rules.d/80-uinput.rules

Reload udev rules:
  sudo udevadm control --reload-rules
  sudo udevadm trigger


STEP 4: Load uinput Module
───────────────────────────
Load now:
  sudo modprobe uinput

Load automatically on boot:
  echo 'uinput' | sudo tee -a /etc/modules


STEP 5: Start ydotoold Service (if needed)
───────────────────────────────────────────
Some distributions require starting the ydotool daemon:
  systemctl --user enable --now ydotool
  # or
  ydotoold &


STEP 6: Restart Talky
─────────────────────
After completing all steps and logging out/in, restart Talky.

═══════════════════════════════════════════════════════════

For more information, see:
  https://github.com/ChrisKalahiki/talky/blob/main/README.md

═══════════════════════════════════════════════════════════
"""
        return guide

    def print_status_report(self):
        """Print detailed status report to console."""
        result = self.check_all()

        print("\n" + "=" * 60)
        print("Wayland Setup Status")
        print("=" * 60)

        if not result["is_wayland"]:
            print("\n✓ Not running on Wayland - no setup required")
            print("=" * 60)
            return

        if result["ready"]:
            print("\n✓ All checks passed! Talky should work correctly.")
        else:
            print("\n✗ Setup incomplete - please address the issues below:")

        # Print issues
        if result["issues"]:
            print("\n" + "─" * 60)
            print("ISSUES (must fix):")
            print("─" * 60)
            for i, issue in enumerate(result["issues"], 1):
                print(f"\n{i}. {issue['title']}")
                print(f"   {issue['description']}")
                if 'solution' in issue:
                    print(f"\n   Solution:")
                    for line in issue['solution'].split('\n'):
                        print(f"   {line}")

        # Print warnings
        if result["warnings"]:
            print("\n" + "─" * 60)
            print("WARNINGS (recommended):")
            print("─" * 60)
            for i, warning in enumerate(result["warnings"], 1):
                print(f"\n{i}. {warning['title']}")
                print(f"   {warning['description']}")
                if 'solution' in warning:
                    print(f"\n   Solution:")
                    for line in warning['solution'].split('\n'):
                        print(f"   {line}")

        print("\n" + "=" * 60)

        if not result["ready"]:
            print("\nFor complete setup guide, run:")
            print("  talky --wayland-setup-guide")
            print("=" * 60)


def main():
    """Run Wayland setup checker from command line."""
    checker = WaylandSetupChecker()
    checker.print_status_report()


if __name__ == "__main__":
    main()
