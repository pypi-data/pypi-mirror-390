#!/bin/bash

echo "🚀 Installing RobbieJr Advanced Host Scanner v5.0..."

# Check Termux
[[ ! -d "/data/data/com.termux" ]] && {
    echo "⚠️  Run in Termux"
    exit 1
}

echo "📦 Updating packages..."
pkg update -y

echo "📥 Installing dependencies..."
pkg install -y curl

chmod +x robbiejr.sh
ln -sf "$(pwd)/robbiejr.sh" "$PREFIX/bin/robbiejr"

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Usage:"
echo "   robbiejr --hosts google.com --subdomain"
echo "   robbiejr --file hosts.txt --free-basics"
echo "   robbiejr --dir /sdcard/hostfiles"
echo ""
echo "📖 robbiejr --help"
