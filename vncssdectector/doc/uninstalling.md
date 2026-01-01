# Uninstalling

## Orbic

To uninstall VNCSSdetector, power on your Orbic device and connect to it via USB. Then, start a rootshell on it by running `adb shell`, followed by `rootshell`.

Once in a rootshell, run:

```shell
echo 3 > /usrdata/mode.cfg
rm -rf /data/vncssdetector /etc/init.d/vncssdetector_daemon /bin/rootshell
reboot
```

Your device is now VNCSSdetector-free, and should no longer be in a rooted ADB-enabled mode.

## TPLink

1. Run `./installer util tplink-start-telnet`
2. Telnet into the device `telnet 192.168.0.1`
3. `rm /data/vncssdetector /etc/init.d/vncssdetector_daemon`
4. `update-rc.d vncssdetector_daemon remove`
5. (hardware revision v4.0+ only) In `Settings > NAT Settings > Port Triggers` in TP-Link's admin UI, remove any leftover port triggers.

## MSM8916

0. (Optional): Back up the qmdl folder with all of the captures:
`adb pull /data/vncssdetector/qmdl .`
1. Run `adb shell` to get a root shell on the device
2. Delete the /data/vncssdetector folder: `rm -rf /data/vncssdetector`
3. Modify the initmifiservice.sh script to remove the vncssdetector 
startup line:
```sh
mount -o remount,rw /system
busybox vi /system/bin/initmifiservice.sh
```
Then type 999G (shift+g), then type dd. Then press the colon key (:) and type wq. Finally, press Enter.
4. Lastly, run `setprop persist.sys.usb.config rndis`.
5. Type `reboot` to reboot the device.
