# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT

"""
External sample MCP describe how to flash boards with uuu-based flashing operations.
"""


import os
import shlex
import stat
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, Optional

from fc_mcp.mcp_base import MCPPlugin


class Plugin(MCPPlugin):
    def register_tools(self):
        @self.mcp.tool()
        def boot_mode_switch(
            resource_id: str, boot_mode: str, verbose: int = 0
        ) -> Dict[str, Any]:
            """
            Switch boot mode for a resource using fc-client command.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                boot_mode: Boot mode to switch to ('usb', 'sd', 'emmc', or ...)
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with operation result and status information
            """

            # Build verbose flags for fc-client commands
            verbose_flags = ("-v " * verbose).strip() if verbose > 0 else ""

            # Get current timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create environment setup script
            env_setup_script = """
if [ -f "/opt/fc_env/env.sh" ]; then
    source /opt/fc_env/env.sh
elif [ -f "$HOME/.fc_env/env.sh" ]; then
    source ~/.fc_env/env.sh
else
    echo "ERROR: Neither /opt/fc_env/env.sh nor ~/.fc_env/env.sh found!"
    exit 1
fi
"""

            # Build the fc-client command with proper spacing
            if verbose_flags:
                fc_command = f"fc-client -p {resource_id} -c $BOARDS_CONFIG/{resource_id}_remote.yaml boot_sw {boot_mode} {verbose_flags}"
            else:
                fc_command = f"fc-client -p {resource_id} -c $BOARDS_CONFIG/{resource_id}_remote.yaml boot_sw {boot_mode}"

            # Combine environment setup and fc-client command
            full_command = env_setup_script + "\n" + fc_command

            try:
                # Record start time
                start_time = time.time()

                # Execute the command using bash
                result = subprocess.run(
                    ["bash", "-c", full_command],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )

                # Calculate execution time
                end_time = time.time()
                execution_time = end_time - start_time
                if result.returncode == 0:
                    return {
                        "resource_id": resource_id,
                        "operation": "boot_mode_switch",  # FIXED: consistent operation name
                        "success": True,
                        "boot_mode": boot_mode,
                        "executed_at": current_time,
                        "message": f"Successfully switched {resource_id} to {boot_mode} boot mode",
                        "command_executed": fc_command,
                        "stdout": result.stdout.strip() if result.stdout else "",
                        "execution_time": f"{execution_time:.2f} seconds",
                    }

                return {
                    "resource_id": resource_id,
                    "operation": "boot_mode_switch",  # FIXED: consistent operation name
                    "success": False,
                    "boot_mode": boot_mode,
                    "error": f"Command failed with return code {result.returncode}",
                    "command_executed": fc_command,
                    "stderr": result.stderr.strip() if result.stderr else "",
                    "stdout": result.stdout.strip() if result.stdout else "",
                    "troubleshooting": [
                        f"• Ensure resource {resource_id} is locked and accessible",
                        "• Check that FC environment is properly configured",
                        "• Verify the resource configuration file exists",
                        "• Check network connectivity to the resource",
                    ],
                }
            except subprocess.TimeoutExpired:
                return {
                    "resource_id": resource_id,
                    "operation": "boot_mode_switch",
                    "success": False,
                    "boot_mode": boot_mode,
                    "error": "Command timed out after 120 seconds",
                    "command_executed": fc_command,
                    "troubleshooting": [
                        "• Check network connectivity to the resource",
                        "• Verify the resource is responsive",
                        "• Try again with increased verbosity for more details",
                    ],
                }
            except Exception as exce:
                return {
                    "resource_id": resource_id,
                    "operation": "boot_mode_switch",
                    "success": False,
                    "boot_mode": boot_mode,
                    "error": f"Unexpected error: {str(exce)}",
                    "command_executed": fc_command,
                    "fallback_manual_command": [
                        "If automatic execution fails, run these commands manually:",
                        "source /opt/fc_env/env.sh || source ~/.fc_env/env.sh",
                        fc_command,
                    ],
                }

        @self.mcp.tool()
        def flash_usb_boot_nexus(
            resource_id: str,
            release_build_plan: str,
            build_number: str,
            verbose: int = 0,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Flash/burn/deploy image using USB Boot with Nexus plan.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                release_build_plan: Release build plan (e.g., 'Linux_Factory')
                build_number: Build number for the release (e.g., '668')
                verbose: Verbosity level (0-3)
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with script generation result and execution instructions
            """
            return self._generate_flash_script(
                resource_id=resource_id,
                flash_type="usb_boot_nexus",
                verbose=verbose,
                script_name=script_name,
                release_build_plan=release_build_plan,
                build_number=build_number,
            )

        @self.mcp.tool()
        def flash_usb_boot_urls(
            resource_id: str,
            uboot_url: str,
            dtb_url: str,
            kernel_url: str,
            rootfs_url: Optional[str] = None,
            verbose: int = 0,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Flash/burn/deploy image using USB Boot with URL addresses.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                uboot_url: URL for u-boot image
                dtb_url: URL for device tree blob
                kernel_url: URL for kernel image
                rootfs_url: URL for root filesystem (OPTIONAL - can be None/omitted)
                verbose: Verbosity level (0-3)
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with script generation result and execution instructions

            Note:
                The rootfs_url parameter is optional. If not provided, only u-boot, DTB,
                and kernel will be flashed. This is useful for minimal boot scenarios or
                when the rootfs will be provided through other means (NFS, etc.).
            """
            return self._generate_flash_script(
                resource_id=resource_id,
                flash_type="usb_boot_urls",
                verbose=verbose,
                script_name=script_name,
                uboot_url=uboot_url,
                dtb_url=dtb_url,
                kernel_url=kernel_url,
                rootfs_url=rootfs_url,
            )

        @self.mcp.tool()
        def flash_usb_boot_local(
            resource_id: str,
            uboot_path: str,
            dtb_path: str,
            kernel_path: str,
            rootfs_path: Optional[str] = None,
            verbose: int = 0,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Flash/burn/deploy image using USB Boot with local files.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                uboot_path: Local path to u-boot image
                dtb_path: Local path to device tree blob
                kernel_path: Local path to kernel image
                rootfs_path: Local path to root filesystem (OPTIONAL - can be None/omitted)
                verbose: Verbosity level (0-3)
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with script generation result and execution instructions

            Note:
                The rootfs_path parameter is optional. If not provided, only u-boot, DTB,
                and kernel will be flashed. This is useful for minimal boot scenarios or
                when the rootfs will be provided through other means (NFS, etc.).
            """
            return self._generate_flash_script(
                resource_id=resource_id,
                flash_type="usb_boot_local",
                verbose=verbose,
                script_name=script_name,
                uboot_path=uboot_path,
                dtb_path=dtb_path,
                kernel_path=kernel_path,
                rootfs_path=rootfs_path,
            )

        @self.mcp.tool()
        def flash_non_usb_boot_urls(
            resource_id: str,
            uboot_url: Optional[str] = None,
            rootfs_url: Optional[str] = None,
            boot_target: str = "sd",
            verbose: int = 0,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Flash/burn/deploy image using Non-USB Boot with URL addresses.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                uboot_url: URL for u-boot image (OPTIONAL - can be None/omitted)
                rootfs_url: URL for root filesystem (.wic.zst format) (OPTIONAL - can be None/omitted)
                boot_target: Boot target ('sd' or 'emmc')
                verbose: Verbosity level (0-3)
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with script generation result and execution instructions

            Note:
                At least one of uboot_url or rootfs_url must be provided. If both are provided,
                both u-boot and rootfs will be flashed. If only one is provided, only that
                component will be flashed.
            """
            return self._generate_flash_script(
                resource_id=resource_id,
                flash_type="non_usb_boot_urls",
                verbose=verbose,
                script_name=script_name,
                uboot_url=uboot_url,
                rootfs_url=rootfs_url,
                boot_target=boot_target,
            )

        @self.mcp.tool()
        def flash_non_usb_boot_local(
            resource_id: str,
            uboot_path: Optional[str] = None,
            dtb_path: Optional[str] = None,
            kernel_path: Optional[str] = None,
            rootfs_path: Optional[str] = None,
            boot_target: str = "sd",
            verbose: int = 0,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Flash/burn/deploy image using Non-USB Boot with local files.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                uboot_path: Local path to u-boot image (OPTIONAL - will use dummy if not provided)
                dtb_path: Local path to device tree blob (OPTIONAL - will use dummy if not provided)
                kernel_path: Local path to kernel image (OPTIONAL - will use dummy if not provided)
                rootfs_path: Local path to root filesystem (.wic.zst format) (OPTIONAL - can be None/omitted)
                boot_target: Boot target ('sd' or 'emmc')
                verbose: Verbosity level (0-3)
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with script generation result and execution instructions

            Note:
                If uboot_path, dtb_path, or kernel_path are not provided, dummy files will be used
                in the download_custom_image.sh command. The rootfs_path parameter is optional.
            """
            return self._generate_flash_script(
                resource_id=resource_id,
                flash_type="non_usb_boot_local",
                verbose=verbose,
                script_name=script_name,
                uboot_path=uboot_path,
                dtb_path=dtb_path,
                kernel_path=kernel_path,
                rootfs_path=rootfs_path,
                boot_target=boot_target,
            )

    def _generate_flash_script(
        self,
        resource_id: str,
        flash_type: str,
        verbose: int = 0,
        script_name: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Internal method to generate flash scripts for different scenarios.
        """
        # Validate required parameters based on flash type
        validation_error = self._validate_flash_parameters(flash_type, **kwargs)
        if validation_error:
            return {
                "resource_id": resource_id,
                "operation": f"flash_{flash_type}",
                "success": False,
                "error": validation_error,
            }

        # Generate script filename
        if script_name is None:
            script_name = f"flash_{flash_type}_{resource_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sh"
        elif not script_name.endswith(".sh"):
            script_name += ".sh"

        # Build verbose flags - FIXED: proper handling of empty flags
        verbose_flags = ("-v " * verbose).strip() if verbose > 0 else ""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Check for missing rootfs and prepare warnings
        warnings = []
        if flash_type in [
            "usb_boot_urls",
            "usb_boot_local",
            "non_usb_boot_urls",
            "non_usb_boot_local",
        ]:
            rootfs_param = "rootfs_url" if "urls" in flash_type else "rootfs_path"
            if not kwargs.get(rootfs_param):
                if flash_type.startswith("usb_boot"):
                    warnings.append(
                        "No rootfs specified - will use previous rootfs deployed in NFS server"
                    )
                else:
                    warnings.append(
                        "The rootfs may not be available - only u-boot, DTB, and kernel will be flashed"
                    )
        # Generate script content based on flash type
        script_content = self._get_script_content(
            resource_id, flash_type, verbose_flags, current_time, **kwargs
        )

        try:
            # Write and make executable
            with open(script_name, "w", encoding="utf-8") as f_script:
                f_script.write(script_content)

            current_permissions = os.stat(script_name).st_mode
            os.chmod(script_name, current_permissions | stat.S_IEXEC)

            script_path = os.path.abspath(script_name)

            result = {
                "resource_id": resource_id,
                "operation": f"flash_{flash_type}",
                "success": True,
                "script_generated": True,
                "script_path": script_path,
                "script_name": script_name,
                "generated_at": current_time,
                "flash_type": flash_type,
                "message": f"Flash script generated successfully: {script_name}",
                "execution_instructions": [
                    "1. Open a new terminal session",
                    f"2. Navigate to the script location: cd {os.path.dirname(script_path)}",
                    f"3. Execute the script: ./{script_name}",
                    "",
                    "The script will handle the complete flashing workflow automatically.",
                ],
            }

            # Add warnings if any
            if warnings:
                result["warnings"] = warnings

            return result

        except PermissionError:
            return {
                "resource_id": resource_id,
                "operation": f"flash_{flash_type}",
                "success": False,
                "error": f"Permission denied: Cannot create script file {script_name}",
                "suggestion": "Try running from a directory where you have write permissions, or specify a different script_name",
            }
        except Exception as exce:
            return {
                "resource_id": resource_id,
                "operation": f"flash_{flash_type}",
                "success": False,
                "error": f"Failed to create script: {str(exce)}",
            }

    def _validate_flash_parameters(self, flash_type: str, **kwargs) -> Optional[str]:
        """
        Validate required parameters for each flash type.
        """
        if flash_type == "usb_boot_nexus":
            required = ["release_build_plan", "build_number"]
        elif flash_type == "usb_boot_urls":
            required = ["uboot_url", "dtb_url", "kernel_url"]  # rootfs_url is optional
        elif flash_type == "usb_boot_local":
            required = [
                "uboot_path",
                "dtb_path",
                "kernel_path",
            ]  # rootfs_path is optional
        elif flash_type == "non_usb_boot_urls":
            # At least one of uboot_url or rootfs_url must be provided
            if not kwargs.get("uboot_url") and not kwargs.get("rootfs_url"):
                return "At least one of uboot_url or rootfs_url must be provided"
            return None  # No other validation needed
        elif flash_type == "non_usb_boot_local":
            # All parameters are optional - dummy files will be used if not provided
            return None  # No validation needed
        else:
            return f"Unknown flash type: {flash_type}"

        missing = [param for param in required if not kwargs.get(param)]
        if missing:
            return f"Missing required parameters: {', '.join(missing)}"

        return None

    def _escape_bash_arg(self, arg: str) -> str:
        """
        Safely escape arguments for bash commands.
        """
        return shlex.quote(str(arg))

    def _format_fc_command(self, base_command: str, verbose_flags: str) -> str:
        """
        Helper to format fc-client commands with proper verbose flag placement.
        """
        if verbose_flags:
            return f"{base_command} {verbose_flags}"
        return base_command

    def _get_script_content(
        self,
        resource_id: str,
        flash_type: str,
        verbose_flags: str,
        current_time: str,
        **kwargs,
    ) -> str:
        """
        Generate script content based on flash type and parameters.
        """
        base_header = f"""#!/bin/bash
# Auto-generated flash script
# Resource: {resource_id}
# Flash Type: {flash_type}
# Generated on: {current_time}

set -e  # Exit on any error

echo "=========================================="
echo "Flash/Burn/Deploy Image Workflow"
echo "Resource: {resource_id}"
echo "Type: {flash_type}"
echo "=========================================="

# Environment setup
echo "Setting up environment..."
if [ -f "/opt/fc_env/env.sh" ]; then
    source /opt/fc_env/env.sh
elif [ -f "$HOME/.fc_env/env.sh" ]; then
    source ~/.fc_env/env.sh
else
    echo "ERROR: FC environment not found!"
    exit 1
fi

"""

        if flash_type == "usb_boot_nexus":
            boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw usb',
                verbose_flags,
            )
            bootstrap_cmd = self._format_fc_command(
                f"fc-client -p {resource_id} bootstrap {resource_id}_cmd.txt",
                verbose_flags,
            )

            return (
                base_header
                + f"""# USB Boot - Nexus Plan
echo "Step 1: Downloading yocto image from nexus..."
download_yocto_image.sh {resource_id} {self._escape_bash_arg(kwargs['release_build_plan'])} {self._escape_bash_arg(kwargs['build_number'])} nexus

echo "Step 2: Switch to USB boot..."
{boot_cmd}

echo "Step 3: Bootstrapping device..."
{bootstrap_cmd}

echo "SUCCESS: USB Boot Nexus flash completed!"
"""
            )

        if flash_type == "usb_boot_urls":
            boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw usb',
                verbose_flags,
            )
            bootstrap_cmd = self._format_fc_command(
                f"fc-client -p {resource_id} bootstrap {resource_id}_cmd.txt",
                verbose_flags,
            )

            # Build download command with optional rootfs
            download_cmd = f"""download_custom_image.sh -p {resource_id} \\
    --uboot-url {self._escape_bash_arg(kwargs['uboot_url'])} \\
    --dtb-url {self._escape_bash_arg(kwargs['dtb_url'])} \\
    --kernel-url {self._escape_bash_arg(kwargs['kernel_url'])}"""

            if kwargs.get("rootfs_url"):
                download_cmd += f" \\\n    --rootfs-url {self._escape_bash_arg(kwargs['rootfs_url'])}"

            return (
                base_header
                + f"""# USB Boot - URL Addresses
echo "Step 1: Downloading custom images from URLs..."
{download_cmd}

echo "Step 2: Switch to USB boot..."
{boot_cmd}

echo "Step 3: Bootstrapping device..."
{bootstrap_cmd}

echo "SUCCESS: USB Boot URLs flash completed!"
"""
            )

        if flash_type == "usb_boot_local":
            boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw usb',
                verbose_flags,
            )
            bootstrap_cmd = self._format_fc_command(
                f"fc-client -p {resource_id} bootstrap {resource_id}_cmd.txt",
                verbose_flags,
            )

            # Build download command with optional rootfs
            download_cmd = f"""download_custom_image.sh -p {resource_id} \\
    --uboot {self._escape_bash_arg(kwargs['uboot_path'])} \\
    --dtb {self._escape_bash_arg(kwargs['dtb_path'])} \\
    --kernel {self._escape_bash_arg(kwargs['kernel_path'])}"""

            if kwargs.get("rootfs_path"):
                download_cmd += (
                    f" \\\n    --rootfs {self._escape_bash_arg(kwargs['rootfs_path'])}"
                )

            return (
                base_header
                + f"""# USB Boot - Local Files
echo "Step 1: Setting up custom images from local files..."
{download_cmd}

echo "Step 2: Switch to USB boot..."
{boot_cmd}

echo "Step 3: Bootstrapping device..."
{bootstrap_cmd}

echo "SUCCESS: USB Boot Local flash completed!"
"""
            )
        if flash_type == "non_usb_boot_urls":
            boot_target = kwargs.get("boot_target", "sd")
            usb_boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw usb',
                verbose_flags,
            )
            target_boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw {boot_target}',
                verbose_flags,
            )

            # Determine bootstrap command based on what URLs are provided
            uboot_url = kwargs.get("uboot_url")
            rootfs_url = kwargs.get("rootfs_url")

            if uboot_url and rootfs_url:
                # Both URLs provided - use sd_all with both URLs
                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target}_all {self._escape_bash_arg(uboot_url)} {self._escape_bash_arg(rootfs_url)}"',
                    verbose_flags,
                )
                step2_desc = f"Bootstrapping u-boot and rootfs to {boot_target}_all"
            elif uboot_url:
                # Only uboot URL provided - use sd with uboot URL
                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target} {self._escape_bash_arg(uboot_url)}"',
                    verbose_flags,
                )
                step2_desc = f"Bootstrapping u-boot to {boot_target}"
            elif rootfs_url:
                # Only rootfs URL provided - use sd_all with rootfs URL
                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target}_all {self._escape_bash_arg(rootfs_url)}"',
                    verbose_flags,
                )
                step2_desc = f"Bootstrapping rootfs to {boot_target}_all"
            else:
                # This shouldn't happen due to validation, but just in case
                return base_header + "echo 'ERROR: No URLs provided'"

            return (
                base_header
                + f"""# Non-USB Boot - URL Addresses
echo "Step 1: Initial USB boot..."
{usb_boot_cmd}

echo "Step 2: {step2_desc}..."
{bootstrap_cmd}

echo "Step 3: Switching to {boot_target} boot..."
{target_boot_cmd}

echo "SUCCESS: Non-USB Boot URLs flash completed!"
"""
            )
        if flash_type == "non_usb_boot_local":
            boot_target = kwargs.get("boot_target", "sd")
            usb_boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw usb',
                verbose_flags,
            )
            target_boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw {boot_target}',
                verbose_flags,
            )

            # Get the provided file paths or use dummy files
            uboot_path = kwargs.get("uboot_path") or "/dev/null"
            dtb_path = kwargs.get("dtb_path") or "/dev/null"
            kernel_path = kwargs.get("kernel_path") or "/dev/null"
            rootfs_path = kwargs.get("rootfs_path")

            # Build download command - always include uboot, dtb, kernel (with dummy if needed)
            download_cmd = f"""download_custom_image.sh -p {resource_id} \\
    --uboot {self._escape_bash_arg(uboot_path)} \\
    --dtb {self._escape_bash_arg(dtb_path)} \\
    --kernel {self._escape_bash_arg(kernel_path)}"""

            if rootfs_path:
                download_cmd += (
                    f" \\\n    --rootfs {self._escape_bash_arg(rootfs_path)}"
                )

            script_content = (
                base_header
                + f"""# Non-USB Boot - Local Files
echo "Step 1: Setting up custom images from local files..."
{download_cmd}

echo "Step 2: Initial USB boot..."
{usb_boot_cmd}

"""
            )
            # Determine the bootstrap scenario based on provided files
            actual_uboot_path = kwargs.get("uboot_path")
            actual_rootfs_path = kwargs.get("rootfs_path")

            if actual_uboot_path and not actual_rootfs_path:
                # Scenario 1: Only u-boot provided - use "sd" with u-boot file in /tftpboot/work/
                uboot_filename = f"/tftpboot/work/{resource_id}_{os.path.basename(actual_uboot_path)}"
                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target} {uboot_filename}"',
                    verbose_flags,
                )
                script_content += f"""echo "Step 3: Bootstrapping u-boot to {boot_target}..."
{bootstrap_cmd}

echo "Step 4: Switching to {boot_target} boot..."
{target_boot_cmd}
"""

            elif actual_rootfs_path and not actual_uboot_path:
                # Scenario 2: Only rootfs provided - use "sd_all" with rootfs file in /tftpboot/
                rootfs_filename = (
                    f"/tftpboot/{resource_id}_{os.path.basename(actual_rootfs_path)}"
                )
                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target}_all {rootfs_filename}"',
                    verbose_flags,
                )
                script_content += f"""echo "Step 3: Bootstrapping rootfs to {boot_target}_all..."
{bootstrap_cmd}

echo "Step 4: Switching to {boot_target} boot..."
{target_boot_cmd}
"""

            elif actual_uboot_path and actual_rootfs_path:
                # Scenario 3: Both u-boot and rootfs provided - use "sd_all" with both files
                uboot_filename = f"/tftpboot/work/{resource_id}_{os.path.basename(actual_uboot_path)}"
                rootfs_filename = (
                    f"/tftpboot/{resource_id}_{os.path.basename(actual_rootfs_path)}"
                )
                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target}_all {uboot_filename} {rootfs_filename}"',
                    verbose_flags,
                )
                script_content += f"""echo "Step 3: Bootstrapping u-boot and rootfs to {boot_target}_all..."
{bootstrap_cmd}

echo "Step 4: Switching to {boot_target} boot..."
{target_boot_cmd}
"""

            else:
                # No u-boot or rootfs provided - just switch boot mode
                script_content += f"""echo "Step 3: No files to bootstrap, switching to {boot_target} boot..."
{target_boot_cmd}
"""

            script_content += """
echo "SUCCESS: Non-USB Boot Local flash completed!"
"""
            return script_content

        return base_header + "echo 'Unknown flash type'"
