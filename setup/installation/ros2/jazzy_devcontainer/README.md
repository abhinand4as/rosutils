# ROS 2 Dev Container Setup

This directory contains a development container configuration for ROS 2 development using Visual Studio Code.

## Overview

The dev container provides a complete ROS 2 development environment with:

- ROS 2 (configurable distribution)
- Python 3 and pip
- Common VSCode extensions for C++, Python, CMake, and ROS development
- GUI support via X11 forwarding
- Network and hardware access configuration

## Quick Start

### Prerequisites

- Docker installed and running
- Visual Studio Code with the "Dev Containers" extension
- X11 server running (for GUI applications)

### Setup Steps

1. **Configure the dev container** (optional but recommended):

   ```bash
   python3 configure_devcontainer.py
   ```

   This interactive script will prompt you for:
   - ROS 2 distribution (e.g., jazzy, humble, iron)
   - Username
   - Workspace path
   - ROS Domain ID
   - Additional packages to install (optional)

   The script will automatically create:
   - `.devcontainer` folder with configured `Dockerfile` and `devcontainer.json`
   - `src` directory for your ROS 2 packages

2. **Open in VSCode**:

   - The `.devcontainer` folder and `src` directory are created in your workspace
   - Open your workspace in VSCode
   - Press `F1` and select "Dev Containers: Reopen in Container"
   - Wait for the container to build (first time takes a few minutes)

3. **Start developing**:

   - The container will automatically run `rosdep update` and install dependencies
   - Your workspace is mounted and ready to use
   - Add your ROS 2 packages to the `src` directory

## Manual Configuration

If you prefer to manually configure the dev container, edit these fields:

### In `.devcontainer/devcontainer.json`

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Container name shown in VSCode | `"ROS 2 Humble Dev"` |
| `remoteUser` | Username inside the container | `"developer"` |
| `build.args.USERNAME` | Username to create in container | `"developer"` |
| `workspaceFolder` | Path inside container | `"/home/developer/workspace"` |
| `workspaceMount` | Workspace mount configuration | Update `target` to match `workspaceFolder` |
| `containerEnv.ROS_DOMAIN_ID` | ROS Domain ID (0-101) | `"42"` |
| `postCreateCommand` | Commands to run after container creation | Update paths to match your workspace |

### In `.devcontainer/Dockerfile`

| Field | Description | Example |
|-------|-------------|---------|
| `FROM` | Base ROS 2 image | `ros:humble`, `ros:iron`, `ros:jazzy` |
| `ARG USERNAME` | Default username | `USERNAME` (set via devcontainer.json) |
| `ARG USER_UID` | User ID | `1000` |

## Changing ROS 2 Distribution

To change the ROS 2 distribution:

### Option 1: Using the configuration script

```bash
python3 configure_devcontainer.py
```

Select your desired ROS 2 distribution when prompted.

### Option 2: Manual edit

1. Edit `.devcontainer/Dockerfile` line 1:

   ```dockerfile
   FROM ros:humble  # Change 'jazzy' to your desired distro
   ```

2. Rebuild the container in VSCode:

   - Press `F1`
   - Select "Dev Containers: Rebuild Container"

## Customization Options

### Adding Additional Packages

Edit the `.devcontainer/Dockerfile` and add package installations before the final `USER` command:

```dockerfile
RUN apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-navigation2 \
    ros-${ROS_DISTRO}-gazebo-ros-pkgs \
    your-package-here
```

### Adding VSCode Extensions

Edit `.devcontainer/devcontainer.json` under `customizations.vscode.extensions`:

```json
"extensions": [
    "ms-vscode.cpptools",
    "your-extension-id-here"
]
```

### Changing Network Configuration

The container uses `--net=host` for easy ROS 2 networking. To use bridge networking instead, modify `runArgs` in `.devcontainer/devcontainer.json`.

### Display and GUI Configuration

The container is configured for X11 forwarding. Ensure you run `xhost +local:docker` on your host system for GUI applications.

## File Structure

```
.devcontainer/
├── devcontainer.json    # VSCode dev container configuration
└── Dockerfile           # Container image definition

configure_devcontainer.py # Interactive configuration script
README.md                 # This file
```

## Common Issues

### GUI applications won't start

- Run `xhost +local:docker` on your host machine
- Verify DISPLAY environment variable is set correctly

### Permission denied errors

- Check that `USER_UID` matches your host user ID
- The `postCreateCommand` sets ownership of the workspace

### ROS commands not found

- Ensure you've sourced the ROS setup: `source /opt/ros/${ROS_DISTRO}/setup.bash`
- The container should auto-source this in the shell

### Container won't build

- Check Docker is running and you have internet connectivity
- Verify the ROS distribution name is correct in the Dockerfile

## Advanced Usage

### Multiple Workspaces

To use multiple workspaces, you can:

1. Create separate `.devcontainer` configurations
2. Use the configuration script to generate different setups
3. Copy the entire directory and modify for each workspace

### Sharing Configurations

The configuration script makes it easy to share standardized setups across teams. Commit the generated files to version control.

## References

- [VSCode Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [ROS 2 Documentation](https://docs.ros.org/)
- [Docker ROS Images](https://hub.docker.com/_/ros)
