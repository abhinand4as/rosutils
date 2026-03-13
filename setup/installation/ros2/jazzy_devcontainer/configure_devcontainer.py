#!/usr/bin/env python3
"""
Interactive Dev Container Configuration Script for ROS 2

This script helps configure the .devcontainer files by asking relevant questions
and updating both devcontainer.json and Dockerfile accordingly.
"""

import json
import os
import sys
import re
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a styled header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}{text}{Colors.ENDC}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}! {text}{Colors.ENDC}")


def get_input(prompt, default=None, validation_fn=None):
    """
    Get user input with optional default value and validation

    Args:
        prompt: Question to ask the user
        default: Default value if user presses enter
        validation_fn: Function to validate input, returns (is_valid, error_message)

    Returns:
        User input or default value
    """
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
            if not user_input:
                print_warning("Input cannot be empty. Please try again.")
                continue

        if validation_fn:
            is_valid, error_msg = validation_fn(user_input)
            if not is_valid:
                print_warning(error_msg)
                continue

        return user_input


def validate_ros_distro(distro):
    """Validate ROS 2 distribution name"""
    valid_distros = ['humble', 'iron', 'jazzy', 'rolling']
    if distro.lower() in valid_distros:
        return True, ""
    return False, f"Invalid ROS distro. Choose from: {', '.join(valid_distros)}"


def validate_domain_id(domain_id):
    """Validate ROS Domain ID (0-101)"""
    try:
        domain = int(domain_id)
        if 0 <= domain <= 101:
            return True, ""
        return False, "Domain ID must be between 0 and 101"
    except ValueError:
        return False, "Domain ID must be a number"


def validate_uid(uid):
    """Validate user UID"""
    try:
        uid_int = int(uid)
        if uid_int > 0:
            return True, ""
        return False, "UID must be a positive number"
    except ValueError:
        return False, "UID must be a number"


def update_dockerfile(file_path, config):
    """Update Dockerfile with new configuration"""
    print_info(f"Updating {file_path}...")

    with open(file_path, 'r') as f:
        content = f.read()

    # Update ROS distribution
    content = re.sub(
        r'FROM ros:\w+',
        f'FROM ros:{config["ros_distro"]}',
        content
    )

    # Update default username
    content = re.sub(
        r'ARG USERNAME=\w+',
        f'ARG USERNAME={config["username"]}',
        content
    )

    # Update USER_UID if needed
    content = re.sub(
        r'ARG USER_UID=\d+',
        f'ARG USER_UID={config["user_uid"]}',
        content
    )

    with open(file_path, 'w') as f:
        f.write(content)

    print_success(f"Updated {file_path}")


def update_devcontainer_json(file_path, config):
    """Update devcontainer.json with new configuration"""
    print_info(f"Updating {file_path}...")

    with open(file_path, 'r') as f:
        data = json.load(f)

    # Update basic fields
    data['name'] = config['container_name']
    data['remoteUser'] = config['username']

    # Update build args
    if 'build' not in data:
        data['build'] = {}
    if 'args' not in data['build']:
        data['build']['args'] = {}
    data['build']['args']['USERNAME'] = config['username']

    # Update workspace paths
    data['workspaceFolder'] = config['workspace_folder']
    data['workspaceMount'] = (
        f"source=${{localWorkspaceFolder}},"
        f"target={config['workspace_folder']},type=bind"
    )

    # Update container environment
    if 'containerEnv' not in data:
        data['containerEnv'] = {}
    data['containerEnv']['ROS_DOMAIN_ID'] = str(config['ros_domain_id'])

    # Update postCreateCommand to use correct paths
    workspace_folder = config['workspace_folder']
    data['postCreateCommand'] = (
        f"sudo rosdep update && "
        f"sudo rosdep install --from-paths src --ignore-src -y && "
        f"sudo chown -R $(whoami) {workspace_folder}"
    )

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    print_success(f"Updated {file_path}")


def main():
    """Main configuration workflow"""
    print_header("=" * 60)
    print_header("ROS 2 Dev Container Configuration Script")
    print_header("=" * 60)

    # Determine paths
    script_dir = Path(__file__).parent
    template_devcontainer_dir = script_dir / '.devcontainer'
    template_dockerfile_path = template_devcontainer_dir / 'Dockerfile'
    template_devcontainer_json_path = template_devcontainer_dir / 'devcontainer.json'

    # Check if template files exist
    if not template_dockerfile_path.exists() or not template_devcontainer_json_path.exists():
        print_error(f"Template dev container files not found in {template_devcontainer_dir}")
        print_info("Please ensure .devcontainer/Dockerfile and .devcontainer/devcontainer.json exist")
        sys.exit(1)

    print_info("This script will configure your ROS 2 dev container setup.")
    print_info("The generated files will be saved to your workspace folder.")
    print_info("Press Enter to accept default values shown in brackets.\n")

    # Read template configuration
    with open(template_devcontainer_json_path, 'r') as f:
        current_config = json.load(f)

    with open(template_dockerfile_path, 'r') as f:
        dockerfile_content = f.read()

    # Extract default values from template files (these remain unchanged)
    default_ros_distro = re.search(r'FROM ros:(\w+)', dockerfile_content)
    default_ros_distro = default_ros_distro.group(1) if default_ros_distro else 'jazzy'

    default_username = re.search(r'ARG USERNAME=(\w+)', dockerfile_content)
    default_username = default_username.group(1) if default_username else 'USERNAME'

    default_workspace = current_config.get('workspaceFolder', '/home/USERNAME/workspace')
    default_domain_id = current_config.get('containerEnv', {}).get('ROS_DOMAIN_ID', '42')
    default_uid = re.search(r'ARG USER_UID=(\d+)', dockerfile_content)
    default_uid = default_uid.group(1) if default_uid else '1000'
    default_container_name = current_config.get('name', 'ROS 2 Development Container')

    # Gather configuration
    config = {}

    print_header("1. ROS 2 Distribution")
    print_info("Available: humble, iron, jazzy, rolling")
    print_info(f"Template default: {default_ros_distro}")
    config['ros_distro'] = get_input(
        "Enter ROS 2 distribution",
        default=default_ros_distro,
        validation_fn=validate_ros_distro
    ).lower()

    print_header("2. Container Name")
    print_info(f"Template default: {default_container_name}")
    config['container_name'] = get_input(
        "Enter container name (shown in VSCode)",
        default=f'ROS 2 {config["ros_distro"].capitalize()} Dev'
    )

    print_header("3. Username Configuration")
    print_info(f"Template default: {default_username}")
    config['username'] = get_input(
        "Enter username for the container",
        default=os.getenv('USER', 'developer')
    )

    print_header("4. User ID (UID)")
    print_info("Tip: Use the same UID as your host user for file permissions")
    print_info(f"Your current UID: {os.getuid()}")
    print_info(f"Template default: {default_uid}")
    config['user_uid'] = get_input(
        "Enter user UID",
        default=str(os.getuid()),
        validation_fn=validate_uid
    )

    print_header("5. Workspace Path")
    print_info("This is the path inside the container where your workspace will be mounted")
    print_info(f"Template default: {default_workspace}")
    suggested_workspace = f"/home/{config['username']}/workspace"
    config['workspace_folder'] = get_input(
        "Enter workspace folder path",
        default=suggested_workspace
    )

    print_header("6. ROS Domain ID")
    print_info("ROS Domain ID allows multiple ROS systems on the same network (0-101)")
    print_info(f"Template default: {default_domain_id}")
    config['ros_domain_id'] = get_input(
        "Enter ROS Domain ID",
        default=default_domain_id,
        validation_fn=validate_domain_id
    )

    # Additional packages (optional)
    print_header("7. Additional Packages (Optional)")
    print_info("Enter additional apt packages to install (space-separated)")
    print_info("Example: ros-jazzy-navigation2 ros-jazzy-slam-toolbox")
    additional_packages = input("Packages (or press Enter to skip): ").strip()
    config['additional_packages'] = additional_packages

    # Automatically determine output directory from workspace folder
    # Use the complete workspace path provided
    print_header("8. Output Location")
    print_info("The .devcontainer folder will be saved in your workspace directory")
    # Create .devcontainer in the same parent directory structure
    output_dir = Path(config['workspace_folder']) / '.devcontainer'
    config['output_dir'] = output_dir.expanduser().resolve()
    print_info(f"Output directory: {config['output_dir']}")

    # Show summary
    print_header("=" * 60)
    print_header("Configuration Summary")
    print_header("=" * 60)
    print(f"ROS 2 Distribution:    {config['ros_distro']}")
    print(f"Container Name:        {config['container_name']}")
    print(f"Username:              {config['username']}")
    print(f"User UID:              {config['user_uid']}")
    print(f"Workspace Folder:      {config['workspace_folder']}")
    print(f"ROS Domain ID:         {config['ros_domain_id']}")
    if config['additional_packages']:
        print(f"Additional Packages:   {config['additional_packages']}")
    print(f"Output Directory:      {config['output_dir']}")
    print("=" * 60)

    # Confirm
    confirm = input(f"\n{Colors.BOLD}Apply these changes? (y/n): {Colors.ENDC}").strip().lower()
    if confirm != 'y':
        print_warning("Configuration cancelled.")
        sys.exit(0)

    # Create output directory
    print_header("Creating output directory...")
    output_devcontainer_dir = config['output_dir']
    output_devcontainer_dir.mkdir(parents=True, exist_ok=True)
    print_success(f"Created directory: {output_devcontainer_dir}")

    # Create src directory in workspace folder
    workspace_dir = output_devcontainer_dir.parent
    src_dir = workspace_dir / 'src'
    src_dir.mkdir(parents=True, exist_ok=True)
    print_success(f"Created directory: {src_dir}")

    # Define output file paths
    output_dockerfile_path = output_devcontainer_dir / 'Dockerfile'
    output_devcontainer_json_path = output_devcontainer_dir / 'devcontainer.json'

    # Warn if files already exist (will be overwritten)
    if output_dockerfile_path.exists() or output_devcontainer_json_path.exists():
        print_warning("Files already exist in output directory and will be overwritten")

    # Apply changes
    print_header("Generating configuration files...")

    try:
        # Copy and update Dockerfile
        with open(template_dockerfile_path, 'r') as f:
            dockerfile_content = f.read()

        # Write to temporary path first, then update
        temp_dockerfile = output_devcontainer_dir / 'Dockerfile.tmp'
        with open(temp_dockerfile, 'w') as f:
            f.write(dockerfile_content)

        update_dockerfile(str(temp_dockerfile), config)
        temp_dockerfile.rename(output_dockerfile_path)

        # Add additional packages to Dockerfile if specified
        if config['additional_packages']:
            with open(output_dockerfile_path, 'r') as f:
                dockerfile_lines = f.readlines()

            # Find the line with python3-pip and add packages after
            for i, line in enumerate(dockerfile_lines):
                if 'apt-get install -y python3-pip' in line:
                    # Add new line with additional packages
                    dockerfile_lines.insert(
                        i + 1,
                        f"RUN apt-get install -y {config['additional_packages']}\n"
                    )
                    break

            with open(output_dockerfile_path, 'w') as f:
                f.writelines(dockerfile_lines)
            print_success("Added additional packages to Dockerfile")

        # Copy and update devcontainer.json
        with open(template_devcontainer_json_path, 'r') as f:
            devcontainer_data = json.load(f)

        with open(output_devcontainer_json_path, 'w') as f:
            json.dump(devcontainer_data, f, indent=4)

        update_devcontainer_json(str(output_devcontainer_json_path), config)

        print_header("=" * 60)
        print_success("Configuration completed successfully!")
        print_header("=" * 60)
        print_info("\nGenerated files:")
        print_info(f"  - {output_dockerfile_path}")
        print_info(f"  - {output_devcontainer_json_path}")
        print_info("\nNext steps:")
        print_info(f"1. Ensure the .devcontainer folder is in your workspace root: {config['output_dir'].parent}")
        print_info("2. Open your workspace in VSCode")
        print_info("3. Press F1 and select 'Dev Containers: Reopen in Container'")
        print_info("4. Wait for the container to build and enjoy your ROS 2 environment!")

    except Exception as e:
        print_error(f"Error during configuration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nConfiguration cancelled by user.")
        sys.exit(0)
