#!/bin/bash -e
pushd daemon/web
    npm install
    npm run build
popd
cargo build-daemon-firmware-devel
adb shell '/bin/rootshell -c "/etc/init.d/vncssdetector_daemon stop"'
adb push target/armv7-unknown-linux-musleabihf/firmware-devel/vncssdetector-daemon \
    /data/vncssdetector/vncssdetector-daemon
echo "rebooting the device..."
adb shell '/bin/rootshell -c "reboot"'
