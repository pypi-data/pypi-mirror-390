#!/bin/bash

# Nia MCP Server Universal Installer for macOS
# This script automatically installs dependencies and configures Nia MCP Server

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running on macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This installer is designed for macOS only."
        print_info "For other platforms, please visit: https://docs.trynia.ai"
        exit 1
    fi
}

# Check if Homebrew is installed
check_homebrew() {
    if command -v brew &> /dev/null; then
        print_success "Homebrew is already installed"
        return 0
    else
        print_warning "Homebrew is not installed"
        return 1
    fi
}

# Install Homebrew
install_homebrew() {
    print_header "Installing Homebrew"
    print_info "Homebrew is required to install pipx. This may take a few minutes..."

    if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        print_success "Homebrew installed successfully"
        return 0
    else
        print_error "Failed to install Homebrew"
        return 1
    fi
}

# Check if pipx is installed
check_pipx() {
    if command -v pipx &> /dev/null; then
        print_success "pipx is already installed"
        return 0
    else
        print_warning "pipx is not installed"
        return 1
    fi
}

# Install pipx
install_pipx() {
    print_header "Installing pipx"

    # Try installing with brew first
    if command -v brew &> /dev/null; then
        if brew install pipx; then
            pipx ensurepath
            print_success "pipx installed successfully via Homebrew"
            return 0
        fi
    fi

    # Fallback to pip
    print_info "Attempting to install pipx via pip..."
    if python3 -m pip install --user pipx; then
        python3 -m pipx ensurepath
        print_success "pipx installed successfully via pip"
        return 0
    else
        print_error "Failed to install pipx"
        return 1
    fi
}

# Install nia-mcp-server
install_nia_mcp_server() {
    print_header "Installing Nia MCP Server"

    # Check if already installed
    if pipx list | grep -q "nia-mcp-server"; then
        print_info "Nia MCP Server is already installed. Upgrading to latest version..."
        if pipx upgrade nia-mcp-server; then
            print_success "Nia MCP Server upgraded successfully"
            return 0
        else
            print_warning "Upgrade failed, but existing installation should still work"
            return 0
        fi
    else
        print_info "Installing Nia MCP Server package..."
        if pipx install nia-mcp-server; then
            print_success "Nia MCP Server installed successfully"
            return 0
        else
            print_error "Failed to install Nia MCP Server"
            return 1
        fi
    fi
}

# Validate inputs
validate_inputs() {
    if [ -z "$1" ]; then
        print_error "API key is required"
        echo ""
        echo "Usage: curl -fsSL https://app.trynia.ai/api/setup-script | bash -s -- API_KEY IDE_NAME"
        echo ""
        echo "Supported IDEs: cursor, claude-code, vscode, windsurf, continue, cline, codex"
        exit 1
    fi

    if [ -z "$2" ]; then
        print_error "IDE name is required"
        echo ""
        echo "Usage: curl -fsSL https://app.trynia.ai/api/setup-script | bash -s -- API_KEY IDE_NAME"
        echo ""
        echo "Supported IDEs: cursor, claude-code, vscode, windsurf, continue, cline, codex"
        exit 1
    fi

    # Validate API key format
    if [[ ! "$1" =~ ^nk_ ]]; then
        print_error "Invalid API key format. API key should start with 'nk_'"
        exit 1
    fi

    # Validate IDE name
    local supported_ides=("cursor" "claude-code" "vscode" "windsurf" "continue" "cline" "codex")
    local ide_valid=false
    for supported_ide in "${supported_ides[@]}"; do
        if [ "$2" = "$supported_ide" ]; then
            ide_valid=true
            break
        fi
    done

    if [ "$ide_valid" = false ]; then
        print_error "Unsupported IDE: $2"
        echo ""
        echo "Supported IDEs: cursor, claude-code, vscode, windsurf, continue, cline, codex"
        exit 1
    fi
}

# Run the setup
run_setup() {
    local api_key=$1
    local ide=$2

    print_header "Configuring $ide"

    # Ensure pipx is in PATH
    export PATH="$HOME/.local/bin:$PATH"

    # Handle command-based IDEs differently
    if [ "$ide" = "claude-code" ]; then
        print_info "Running Claude Code MCP setup (global scope)..."
        # Capture output to only show errors if it fails
        if output=$(claude mcp add nia --scope user -e "NIA_API_KEY=$api_key" -e "NIA_API_URL=https://apigcp.trynia.ai/" -- pipx run --no-cache nia-mcp-server 2>&1); then
            print_success "Setup completed successfully!"
            print_info "Nia MCP server is now available across all your projects!"
            return 0
        else
            print_error "Setup failed. Make sure Claude Code CLI is installed."
            print_info "Install from: https://www.claude.ai/download"
            echo "$output"  # Show error details
            return 1
        fi
    elif [ "$ide" = "codex" ]; then
        print_info "Running Codex MCP setup..."
        # Capture output to only show errors if it fails
        if output=$(codex mcp add nia --env "NIA_API_KEY=$api_key" --env "NIA_API_URL=https://apigcp.trynia.ai/" -- pipx run --no-cache nia-mcp-server 2>&1); then
            print_success "Setup completed successfully!"
            return 0
        else
            print_error "Setup failed. Make sure Codex CLI is installed."
            echo "$output"  # Show error details
            return 1
        fi
    else
        # For file-based IDEs, use nia-mcp-server setup command
        # Capture output to only show errors if it fails
        if output=$(pipx run --no-cache nia-mcp-server setup "$api_key" --ide "$ide" 2>&1); then
            print_success "Setup completed successfully!"
            return 0
        else
            print_error "Setup failed"
            echo "$output"  # Show error details
            return 1
        fi
    fi
}

# Print next steps
print_next_steps() {
    local ide=$1

    print_header "Setup Complete!"

    # ASCII art
    echo -e "${BLUE}"
    cat << "EOF"
    ███╗   ██╗██╗ █████╗
    ████╗  ██║██║██╔══██╗
    ██╔██╗ ██║██║███████║
    ██║╚██╗██║██║██╔══██║
    ██║ ╚████║██║██║  ██║
    ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝
EOF
    echo -e "${NC}"

    echo -e "${GREEN}✓ Nia MCP Server is now configured!${NC}\n"

    echo "Next steps:"
    echo "  1. Restart your coding agent to load Nia"
    echo "  2. Try these commands in your agent:"
    echo ""
    echo -e "     ${YELLOW}\"Index the Turborepo documentation\"${NC}"
    echo "     index https://turborepo/docs"
    echo ""
    echo -e "     ${YELLOW}\"Use Nia package search and search the numpy package for array slicing\"${NC}"
    echo "     (Nia will search through numpy's source code)"
    echo ""
    echo -e "     ${YELLOW}\"Index Flask\"${NC}"
    echo "     index https://github.com/pallets/flask"
    echo ""
    echo "Learn more:"
    echo "  📚 Documentation: https://docs.trynia.ai"
    echo "  💬 Discord: https://discord.gg/BBSwUMrrfn"
    echo ""
}

# Main installation flow
main() {
    local api_key=$1
    local ide=$2

    print_header "Nia MCP Server Installer"

    # Validate inputs
    validate_inputs "$api_key" "$ide"

    # Check if running on macOS
    check_macos

    # Step 1: Ensure Homebrew is installed
    if ! check_homebrew; then
        if ! install_homebrew; then
            print_error "Cannot proceed without Homebrew. Please install it manually from https://brew.sh"
            exit 1
        fi
    fi

    # Step 2: Ensure pipx is installed
    if ! check_pipx; then
        if ! install_pipx; then
            print_error "Cannot proceed without pipx. Please install it manually."
            exit 1
        fi

        # Refresh PATH to pick up newly installed pipx
        export PATH="$HOME/.local/bin:$PATH"

        # Verify pipx is now available
        if ! command -v pipx &> /dev/null; then
            print_warning "pipx was installed but not found in PATH. You may need to restart your terminal."
            print_info "Try running this in a new terminal:"
            echo ""
            echo "  pipx run nia-mcp-server setup $api_key --ide $ide"
            echo ""
            exit 1
        fi
    fi

    # Step 3: Install/upgrade nia-mcp-server
    if ! install_nia_mcp_server; then
        exit 1
    fi

    # Step 4: Run the setup
    if ! run_setup "$api_key" "$ide"; then
        print_error "Setup failed. Please check the error messages above."
        print_info "For manual setup instructions, visit: https://docs.trynia.ai"
        exit 1
    fi

    # Step 5: Print next steps
    print_next_steps "$ide"
}

# Run main with all arguments
main "$@"
