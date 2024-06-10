#!/bin/bash

# Prompt the user for the workspace name
read -p "Enter the name for your catkin workspace: " WORKSPACE_NAME

# Check if a specific Python executable should be used
PYTHON_EXECUTABLE=/usr/bin/python3

# Create catkin workspace directory structure
echo "[INFO] Creating catkin workspace named '$WORKSPACE_NAME'..."
mkdir -p $WORKSPACE_NAME/src
cd $WORKSPACE_NAME/

# Initialize the catkin workspace
echo "[INFO] Initializing catkin workspace with catkin_make..."
if [ -x "$PYTHON_EXECUTABLE" ]; then
    catkin_make -DPYTHON_EXECUTABLE=$PYTHON_EXECUTABLE
else
    catkin_make
fi

# Source the setup file
echo "[INFO] Sourcing setup.bash..."
source devel/setup.sh

# Verify the workspace overlay
echo "[INFO] Verifying ROS_PACKAGE_PATH..."
echo $ROS_PACKAGE_PATH 