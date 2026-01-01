#!/bin/bash
# VNCSSdetector Installation Script for Sony Xperia 5 (LineageOS 22.1)
# This script installs the IMSI catcher detector on a rooted Android device

set -e

DEVICE_IP="${1:-}"
USE_WIFI="${2:-false}"

echo "======================================"
echo "  VNCSSdetector Installer for aarch64"
echo "  Sony Xperia 5 / Snapdragon 855"
echo "======================================"
echo ""

# Check if adb is available
if ! command -v adb &> /dev/null; then
    echo "ERROR: adb not found. Please install Android Debug Bridge (ADB)."
    exit 1
fi

# If IP provided, connect via WiFi ADB
if [ -n "$DEVICE_IP" ]; then
    echo "[*] Connecting to device via WiFi at $DEVICE_IP:5555..."
    adb connect "$DEVICE_IP:5555"
    sleep 2
fi

# Wait for device
echo "[*] Waiting for device..."
adb wait-for-device

# Verify root access
echo "[*] Verifying root access..."
ROOT_TEST=$(adb shell "su -c 'id'" 2>/dev/null | grep -c "uid=0" || true)
if [ "$ROOT_TEST" -eq 0 ]; then
    echo "ERROR: Root access not available. Please ensure your device is rooted and grant root access."
    exit 1
fi
echo "[+] Root access confirmed!"

# Check for /dev/diag
echo "[*] Checking for /dev/diag interface..."
DIAG_CHECK=$(adb shell "su -c 'ls /dev/diag'" 2>/dev/null | grep -c "diag" || true)
if [ "$DIAG_CHECK" -eq 0 ]; then
    echo "WARNING: /dev/diag not found. The Qualcomm DIAG interface may need to be enabled."
    echo "         VNCSSdetector requires this interface to capture cellular data."
    echo ""
    echo "Try one of these options:"
    echo "  1. Install a diag enabler module for your kernel"
    echo "  2. Check if your kernel supports DIAG interface"
    echo ""
    read -p "Continue anyway? (y/N): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        exit 1
    fi
else
    echo "[+] /dev/diag found!"
fi

# Create directories
echo "[*] Creating directories on device..."
adb shell "su -c 'mkdir -p /data/vncssdetector/qmdl'"
adb shell "su -c 'chmod 755 /data/vncssdetector'"
adb shell "su -c 'chmod 755 /data/vncssdetector/qmdl'"

# Push binary
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[*] Installing vncssdetector-daemon..."
adb push "$SCRIPT_DIR/vncssdetector-daemon" /data/local/tmp/
adb shell "su -c 'mv /data/local/tmp/vncssdetector-daemon /data/vncssdetector/'"
adb shell "su -c 'chmod 755 /data/vncssdetector/vncssdetector-daemon'"

# Push config
echo "[*] Installing configuration..."
adb push "$SCRIPT_DIR/config.toml" /data/local/tmp/
adb shell "su -c 'mv /data/local/tmp/config.toml /data/vncssdetector/'"
adb shell "su -c 'chmod 644 /data/vncssdetector/config.toml'"

# Push start/stop script
echo "[*] Installing start script..."
adb push "$SCRIPT_DIR/start-vncssdetector.sh" /data/local/tmp/
adb shell "su -c 'mv /data/local/tmp/start-vncssdetector.sh /data/vncssdetector/'"
adb shell "su -c 'chmod 755 /data/vncssdetector/start-vncssdetector.sh'"

echo ""
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "To start VNCSSdetector:"
echo "  adb shell \"su -c '/data/vncssdetector/start-vncssdetector.sh start'\""
echo ""
echo "To stop VNCSSdetector:"
echo "  adb shell \"su -c '/data/vncssdetector/start-vncssdetector.sh stop'\""
echo ""
echo "To access the web interface:"
echo "  1. Forward port: adb forward tcp:8080 tcp:8080"
echo "  2. Open browser: http://localhost:8080"
echo ""
echo "Or access directly at: http://<device-ip>:8080"
echo ""
