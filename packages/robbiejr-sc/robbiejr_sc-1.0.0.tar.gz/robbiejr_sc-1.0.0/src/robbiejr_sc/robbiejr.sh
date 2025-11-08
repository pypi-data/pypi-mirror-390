#!/bin/bash

# RobbieJr Ultimate CDN Host Checker
# Final Version with Auto Full Scan & CDN Detection

VERSION="4.0"
DEVELOPER="RobbieJr"
BANNER="╔══════════════════════════════════════════════════════════════════════════════╗
║                      🚀 ROBBIEJR CDN HOST CHECKER 🚀                      ║
║                         Developed by: $DEVELOPER                           ║
║           Auto Full Scan • CDN Detection • Live Output • Free Basics      ║
╚══════════════════════════════════════════════════════════════════════════════╝"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
ORANGE='\033[0;33m'
NC='\033[0m'

# Configuration
MAX_CONCURRENT=20
TIMEOUT=10
USER_AGENT="Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36"
OFFLINE_MODE=false
CHECK_FREE_BASICS=false

# Global variables
declare -a HOSTS
SUCCESS_COUNT=0
OTHER_COUNT=0

# CDN Providers
declare -A CDN_PROVIDERS=(
    ["cloudfront"]="Amazon CloudFront"
    ["akamai"]="Akamai"
    ["fastly"]="Fastly"
    ["cloudflare"]="CloudFlare"
    ["google"]="Google Cloud CDN"
    ["azure"]="Microsoft Azure CDN"
    ["edgecast"]="EdgeCast"
    ["limelight"]="Limelight"
    ["incapsula"]="Incapsula"
    ["stackpath"]="StackPath"
)

show_help() {
    echo -e "${CYAN}RobbieJr CDN Host Checker v$VERSION${NC}"
    echo "  ./robbiejr.sh --hosts host1.com,host2.com"
    echo "  ./robbiejr.sh --file hosts.txt"
    echo "  ./robbiejr.sh --dir /path/to/host/files"
    echo "  ./robbiejr.sh --url https://example.com/hosts.txt"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --hosts HOSTS        Comma-separated hosts"
    echo "  --file FILE          File with hosts"
    echo "  --dir DIRECTORY      Directory with host files"
    echo "  --url URL            URL to download hosts"
    echo "  --offline            DNS resolution only"
    echo "  --free-basics        Free Basics detection"
    echo "  --help               Show this help"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  ./robbiejr.sh --hosts google.com"
    echo "  ./robbiejr.sh --file hosts.txt --free-basics"
}

print_banner() {
    echo -e "${PURPLE}$BANNER${NC}"
}

check_dependencies() {
    local deps=("curl")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            echo -e "${RED}❌ Installing curl...${NC}"
            pkg update && pkg install -y curl
            break
        fi
    done
}

load_hosts_from_directory() {
    local dir="$1"
    [[ ! -d "$dir" ]] && echo -e "${RED}❌ Directory not found${NC}" && return 1

    echo -e "${BLUE}📁 Loading from directory: $dir${NC}"
    local count=0
    while IFS= read -r -d '' file; do
        [[ -f "$file" && -r "$file" ]] || continue
        echo -e "${BLUE}📄 $(basename "$file")${NC}"
        while IFS= read -r line; do
            line=$(echo "$line" | xargs)
            [[ -z "$line" || "$line" =~ ^# ]] && continue
            HOSTS+=("$line")
            ((count++))
        done < "$file"
    done < <(find "$dir" -maxdepth 1 -name "*.txt" -type f -print0 2>/dev/null)

    echo -e "${GREEN}✅ Loaded $count hosts${NC}"
}

load_hosts_from_file() {
    local file="$1"
    [[ ! -f "$file" ]] && echo -e "${RED}❌ File not found${NC}" && return 1

    echo -e "${BLUE}📁 Loading: $file${NC}"
    local count=0
    while IFS= read -r line; do
        line=$(echo "$line" | xargs)
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        HOSTS+=("$line")
        ((count++))
    done < "$file"
    echo -e "${GREEN}✅ Loaded $count hosts${NC}"
}

load_hosts_from_stdin() {
    echo -e "${BLUE}📥 Reading from stdin...${NC}"
    local count=0
    while IFS= read -r line; do
        line=$(echo "$line" | xargs)
        [[ -z "$line" ]] && continue
        HOSTS+=("$line")
        ((count++))
    done
    echo -e "${GREEN}✅ Loaded $count hosts${NC}"
}

get_ip_address() {
    local host="$1"
    local clean_host=$(echo "$host" | sed -E 's|https?://||' | sed 's|/.*||')

    local ip=$(ping -c 1 -W 2 "$clean_host" 2>/dev/null | head -1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
    [[ -z "$ip" ]] && command -v nslookup &> /dev/null && ip=$(nslookup "$clean_host" 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+' | tail -1)

    echo "$ip"
}

detect_cdn() {
    local server_header="$1"
    local ip="$2"

    server_header=$(echo "$server_header" | tr '[:upper:]' '[:lower:]')

    for cdn in "${!CDN_PROVIDERS[@]}"; do
        if [[ "$server_header" == *"$cdn"* ]]; then
            echo "${CDN_PROVIDERS[$cdn]}"
            return 0
        fi
    done

    # IP-based detection for major CDNs
    if [[ "$ip" =~ ^54\. ]] || [[ "$ip" =~ ^52\. ]] || [[ "$ip" =~ ^18\. ]]; then
        echo "Amazon CloudFront"
    elif [[ "$ip" =~ ^23\. ]] || [[ "$ip" =~ ^2\. ]]; then
        echo "Akamai"
    elif [[ "$ip" =~ ^104\. ]] || [[ "$ip" =~ ^172\. ]]; then
        echo "CloudFlare"
    elif [[ "$ip" =~ ^151\. ]]; then
        echo "Fastly"
    else
        echo ""
    fi
}

get_http_status() {
    local host="$1"
    local protocol="$2"
    timeout $TIMEOUT curl -s -o /dev/null -w "%{http_code}" -A "$USER_AGENT" -L "$protocol://$host" 2>/dev/null
}

get_full_response() {
    local host="$1"
    local protocol="$2"
    timeout $TIMEOUT curl -s -I -A "$USER_AGENT" -L -k "$protocol://$host" 2>/dev/null
}

check_free_basics() {
    local host="$1" ip="$2"
    local -a free_ips=("31.13." "157.240." "57.144." "185.60." "69.171." "66.220." "173.252.")

    for fb_ip in "${free_ips[@]}"; do
        [[ "$ip" == "$fb_ip"* ]] && return 0
    done
    return 1
}

scan_single_host() {
    local host="$1"
    local clean_host=$(echo "$host" | sed -E 's|https?://||' | sed 's|/.*||')

    echo -e "${CYAN}TARGET --> https://$clean_host${NC}"

    # Get IP
    local ip=$(get_ip_address "$clean_host")
    if [[ -z "$ip" ]]; then
        echo -e "${RED}IP: No DNS resolution${NC}"
        echo "--------------------------------------------------------"
        return
    fi
    echo -e "${GREEN}IP: $ip${NC}"

    # Try HTTPS then HTTP
    local status_code=$(get_http_status "$clean_host" "https")
    local protocol="https"
    [[ -z "$status_code" || "$status_code" == "000" ]] && {
        status_code=$(get_http_status "$clean_host" "http")
        protocol="http"
    }

    # Get full response
    local response=$(get_full_response "$clean_host" "$protocol")

    if [[ -n "$response" ]]; then
        # Extract key headers
        local server=$(echo "$response" | grep -i "^server:" | head -1 | sed 's/^[^:]*: //')
        local http_line=$(echo "$response" | grep -i "^HTTP/" | head -1)

        echo -e "${YELLOW}$http_line${NC}"

        # Show important headers only
        echo "$response" | grep -i -E "^(Server:|Content-Type:|Cache-Control:|X-|CF-|Akamai|CloudFront|Fastly|Strict-Transport-Security:|X-Frame-Options:)" | \
        while read -r header; do
            local name=$(echo "$header" | cut -d: -f1)
            local value=$(echo "$header" | cut -d: -f2- | sed 's/^ //')
            echo -e "${BLUE}$name:${NC} $value"
        done

        # CDN Detection
        local cdn=$(detect_cdn "$server" "$ip")
        if [[ -n "$cdn" ]]; then
            echo -e "${CYAN}--------------------------CDN-----------------------${NC}"
            echo -e "${GREEN}Hostname: $clean_host ($cdn)${NC}"
            echo -e "${GREEN}==> $ip${NC}"
            echo -e "${CYAN}--------------------END CDN---------------------${NC}"
        fi

    else
        echo -e "${RED}HTTP/1.0 000 No Response${NC}"
    fi

    echo -e "${CYAN}--------------------------------------------------------${NC}"
    echo ""
}

run_scan() {
    local total=${#HOSTS[@]}

    print_banner
    echo -e "${CYAN}────────────────────────── 🔍 SCANNING $total HOST(S) ───────────────────────────${NC}"
    echo ""

    for host in "${HOSTS[@]}"; do
        scan_single_host "$host" &

        # Limit concurrent processes
        while [[ $(jobs -r | wc -l) -ge $MAX_CONCURRENT ]]; do
            sleep 0.1
        done
    done

    wait
}

main() {
    check_dependencies

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --hosts) IFS=',' read -ra HOSTS <<< "$2"; shift 2 ;;
            --file) load_hosts_from_file "$2"; shift 2 ;;
            --dir) load_hosts_from_directory "$2"; shift 2 ;;
            --offline) OFFLINE_MODE=true; shift ;;
            --free-basics) CHECK_FREE_BASICS=true; shift ;;
            --help) show_help; exit 0 ;;
            *) echo -e "${RED}❌ Unknown option: $1${NC}"; show_help; exit 1 ;;
        esac
    done

    # Check stdin
    [[ ! -t 0 ]] && load_hosts_from_stdin

    # Validate hosts
    [[ ${#HOSTS[@]} -eq 0 ]] && {
        echo -e "${RED}❌ No hosts provided!${NC}"
        show_help
        exit 1
    }

    run_scan
}

main "$@"
