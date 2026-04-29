#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  ROS 2 shell setup installer
#  Adds helper functions to ~/.bashrc or ~/.zshrc
#
#  Usage:
#    ./ros2_setup.sh                   — first-time setup (interactive)
#    ./ros2_setup.sh --change-ws PATH  — update DEFAULT_ROS_WS in rc file
# ─────────────────────────────────────────────

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[ros2-setup]${RESET} $*"; }
success() { echo -e "${GREEN}[ros2-setup]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[ros2-setup]${RESET} $*"; }
err()     { echo -e "${RED}[ros2-setup]${RESET} $*"; exit 1; }

MARKER_BEGIN="# >>> ros2-setup >>>"
MARKER_END="# <<< ros2-setup <<<"

# ── --change-ws mode ──────────────────────────
if [[ "$1" == "--change-ws" ]]; then
    NEW_WS="$2"
    [[ -z "$NEW_WS" ]] && err "Usage: $0 --change-ws /path/to/workspace"

    # Detect which rc file has the ros2-setup block
    RC_FILE=""
    for f in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if grep -q "$MARKER_BEGIN" "$f" 2>/dev/null; then
            RC_FILE="$f"
            break
        fi
    done
    [[ -z "$RC_FILE" ]] && err "No ros2-setup block found. Run this script without arguments first."

    # Replace the DEFAULT_ROS_WS line in-place
    TMP=$(mktemp)
    sed "s|export DEFAULT_ROS_WS=.*|export DEFAULT_ROS_WS=\"${NEW_WS}\"|" "$RC_FILE" > "$TMP"
    mv "$TMP" "$RC_FILE"

    success "DEFAULT_ROS_WS updated to: ${NEW_WS}"
    echo -e "  Reload your shell: ${CYAN}source ${RC_FILE}${RESET}"
    echo ""
    exit 0
fi

# ── 1. Shell choice ───────────────────────────
echo ""
echo -e "${BOLD}Which shell are you using?${RESET}"
select SHELL_CHOICE in "bash" "zsh"; do
    case $SHELL_CHOICE in
        bash) RC_FILE="$HOME/.bashrc";  SETUP_EXT="bash"; break ;;
        zsh)  RC_FILE="$HOME/.zshrc";   SETUP_EXT="zsh";  break ;;
        *)    warn "Invalid choice, try again." ;;
    esac
done

# ── 2. ROS distro ─────────────────────────────
echo ""
echo -e "${BOLD}Which ROS 2 distro?${RESET}"
select ROS_DISTRO in "jazzy" "humble" "iron" "rolling" "other"; do
    case $ROS_DISTRO in
        jazzy|humble|iron|rolling) break ;;
        other)
            read -rp "  Enter distro name: " ROS_DISTRO
            break ;;
        *) warn "Invalid choice, try again." ;;
    esac
done

ROS_SETUP="/opt/ros/${ROS_DISTRO}/setup.${SETUP_EXT}"
[ -f "$ROS_SETUP" ] || warn "ROS setup not found at $ROS_SETUP — install ROS 2 first or path may differ."

# ── 3. Default workspace ──────────────────────
echo ""
DEFAULT_WS_SUGGESTION="$HOME/ws/robotics/ros2"
read -rp "$(echo -e "${BOLD}Default ROS 2 workspace path${RESET} [${DEFAULT_WS_SUGGESTION}]: ")" DEFAULT_ROS_WS
DEFAULT_ROS_WS="${DEFAULT_ROS_WS:-$DEFAULT_WS_SUGGESTION}"

# ── 4. Write to RC file ───────────────────────

# Remove any previous block written by this script
if grep -q "$MARKER_BEGIN" "$RC_FILE" 2>/dev/null; then
    warn "Removing existing ros2-setup block from $RC_FILE"
    TMP=$(mktemp)
    awk "/$MARKER_BEGIN/{found=1} !found{print} /$MARKER_END/{found=0}" "$RC_FILE" > "$TMP"
    mv "$TMP" "$RC_FILE"
fi

cat >> "$RC_FILE" <<EOF

${MARKER_BEGIN}
# ROS 2 config — managed by ros2_setup.sh
# To change workspace: ./ros2_setup.sh --change-ws /new/path
export ROS_DISTRO="${ROS_DISTRO}"
export DEFAULT_ROS_WS="${DEFAULT_ROS_WS}"

# cw — go to default ROS 2 workspace
cw() {
    if [ -d "\$DEFAULT_ROS_WS" ]; then
        cd "\$DEFAULT_ROS_WS" && echo "→ \$DEFAULT_ROS_WS"
    else
        echo "Workspace not found: \$DEFAULT_ROS_WS"
        echo -n "  Create it? (y/N): "
        read -r ans
        [[ "\$ans" =~ ^[Yy]$ ]] && mkdir -p "\$DEFAULT_ROS_WS" && cd "\$DEFAULT_ROS_WS" && echo "→ Created & moved to \$DEFAULT_ROS_WS"
    fi
}

# cs — source the ROS 2 system underlay
cs() {
    local setup="/opt/ros/\${ROS_DISTRO}/setup.${SETUP_EXT}"
    if [ -f "\$setup" ]; then
        # shellcheck disable=SC1090
        source "\$setup" && echo "✓ Sourced system ROS 2 (\$ROS_DISTRO)"
    else
        echo "ROS setup not found: \$setup"
    fi
}

# ci — source the workspace overlay
ci() {
    local setup="\${DEFAULT_ROS_WS}/install/setup.${SETUP_EXT}"
    if [ -f "\$setup" ]; then
        # shellcheck disable=SC1090
        source "\$setup" && echo "✓ Sourced overlay: \$DEFAULT_ROS_WS"
    else
        echo "Overlay not found: \$setup"
        echo "  Have you built the workspace? (colcon build)"
    fi
}
${MARKER_END}
EOF

echo ""
success "Written to ${RC_FILE}"
echo ""
echo -e "  ${BOLD}cw${RESET}  — cd to \$DEFAULT_ROS_WS"
echo -e "  ${BOLD}cs${RESET}  — source /opt/ros/${ROS_DISTRO}/setup.${SETUP_EXT}"
echo -e "  ${BOLD}ci${RESET}  — source \$DEFAULT_ROS_WS/install/setup.${SETUP_EXT}"
echo ""
echo -e "  To change workspace later:"
echo -e "  ${CYAN}./ros2_setup.sh --change-ws ~/ws/robotics/isaac${RESET}"
echo ""
echo -e "Reload your shell:"
echo -e "  ${CYAN}source ${RC_FILE}${RESET}"
echo ""