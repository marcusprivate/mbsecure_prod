#!/bin/bash
#
# Download CodeQL SARIF files from GitHub Code Scanning API
# Usage: ./scripts/download-sarif.sh
#
# Files are saved to .sarif/ with timestamps to preserve history.
# Files older than 90 days are automatically cleaned up.
#

set -euo pipefail

# Constants
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'
readonly SARIF_DIR=".sarif"
readonly RETENTION_DAYS=90
readonly DATE_STAMP=$(date +%Y-%m-%d)

# Logging helpers
log_info()    { echo -e "${YELLOW}$*${NC}"; }
log_success() { echo -e "${GREEN}$*${NC}"; }
log_error()   { echo -e "${RED}$*${NC}" >&2; }

die() {
    log_error "Error: $*"
    exit 1
}

# Sanitize string for safe use in filenames (alphanumeric, dash, underscore only)
sanitize_filename() {
    local input="$1"
    # Remove any characters that aren't alphanumeric, dash, or underscore
    echo "${input//[^a-zA-Z0-9_-]/}"
}

# Validate repo slug format (owner/repo)
validate_repo_slug() {
    local slug="$1"
    # Must match: alphanumeric/dash owner, slash, alphanumeric/dash/underscore repo
    if [[ ! "$slug" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+$ ]]; then
        die "Invalid repository slug format: $slug"
    fi
}

# Change to repository root
cd_to_repo_root() {
    local repo_root
    repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || die "Not inside a git repository"
    cd "$repo_root"
}

# Extract owner/repo from git remote URL
get_repo_slug() {
    local remote_url
    remote_url=$(git remote get-url origin 2>/dev/null) || die "No origin remote configured"
    
    # Match: user/repo from various URL formats (github.com, SSH aliases)
    if [[ "$remote_url" =~ [:/]([^/]+)/([^/.]+)(\.git)?$ ]]; then
        echo "${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    else
        die "Could not parse repository from: $remote_url"
    fi
}

# Verify required tools are available
check_dependencies() {
    log_info "Checking prerequisites..."
    
    command -v gh &>/dev/null  || die "GitHub CLI (gh) not installed. Run: brew install gh"
    command -v jq &>/dev/null  || die "jq not installed. Run: brew install jq"
    gh auth status &>/dev/null || die "GitHub CLI not authenticated. Run: gh auth login"
    
    log_success "✓ Prerequisites met"
}

# Remove SARIF files older than RETENTION_DAYS
cleanup_old_files() {
    log_info "Cleaning up files older than ${RETENTION_DAYS} days..."
    
    [[ -d "$SARIF_DIR" ]] || return 0
    
    local count=0
    while IFS= read -r -d '' file; do
        rm -f "$file"
        ((++count)) || true
    done < <(find "$SARIF_DIR" -name "*.sarif" -type f -mtime +${RETENTION_DAYS} -print0 2>/dev/null)
    
    if [[ $count -gt 0 ]]; then
        log_success "✓ Removed $count old file(s)"
    else
        log_success "✓ No old files to remove"
    fi
}

# Fetch analyses from GitHub API (returns TSV: id, language, results)
fetch_analyses() {
    local repo=$1
    
    gh api "repos/${repo}/code-scanning/analyses" --jq '
        group_by(.category)
        | map(max_by(.created_at))
        | .[]
        | [.id, (.category | split(":")[1]), .results_count]
        | @tsv
    ' 2>/dev/null
}

# Download SARIF for a single analysis
download_one() {
    local repo=$1 id=$2 language=$3 results=$4
    
    # Sanitize language for safe filename (prevent path traversal)
    local safe_language
    safe_language=$(sanitize_filename "$language")
    [[ -n "$safe_language" ]] || { log_error "Invalid language: $language"; return 1; }
    
    local filepath="${SARIF_DIR}/codeql-${safe_language}-${DATE_STAMP}.sarif"
    
    echo -e "Downloading ${language} analysis (${results} findings)..."
    
    # Validate id is numeric (prevent injection)
    if [[ ! "$id" =~ ^[0-9]+$ ]]; then
        log_error "  ✗ Invalid analysis ID: $id"
        return 1
    fi
    
    if gh api "repos/${repo}/code-scanning/analyses/${id}" \
        -H "Accept: application/sarif+json" > "$filepath" 2>/dev/null; then
        log_success "  ✓ Saved to ${filepath}"
        return 0
    else
        log_error "  ✗ Failed to download ${language}"
        rm -f "$filepath"
        return 1
    fi
}

# Download all SARIF files
download_sarif() {
    local repo=$1
    local success=0 failed=0
    local -a failed_languages=()
    
    log_info "Fetching code scanning analyses..."
    
    local analyses
    analyses=$(fetch_analyses "$repo") || die "Failed to fetch analyses from API"
    
    if [[ -z "$analyses" ]]; then
        log_info "No code scanning analyses found"
        return 0
    fi
    
    mkdir -p "$SARIF_DIR"
    
    while IFS=$'\t' read -r id language results; do
        if download_one "$repo" "$id" "$language" "$results"; then
            ((++success)) || true
        else
            ((++failed)) || true
            failed_languages+=("$language")
        fi
    done <<< "$analyses"
    
    # Summary
    echo ""
    log_info "========== Summary =========="
    log_success "Downloaded: ${success}"
    
    if [[ $failed -gt 0 ]]; then
        log_error "Failed: ${failed}"
        log_error "Failed languages: ${failed_languages[*]}"
        return 1
    fi
    
    log_success "All downloads completed successfully"
}

# Main entry point
main() {
    cd_to_repo_root
    check_dependencies
    
    local repo
    repo=$(get_repo_slug)
    validate_repo_slug "$repo"
    
    echo -e "Repository: ${repo}"
    echo ""
    
    cleanup_old_files
    echo ""
    
    download_sarif "$repo"
}

main "$@"
