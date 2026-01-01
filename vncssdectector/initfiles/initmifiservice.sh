#! /system/bin/sh
usbcfg=`getprop persist.sys.usb.config`
usbdebug="rndis,serial_smd,diag,adb"
usbrndis="rndis"

if [ $usbcfg == $usbdebug ]; then
	echo "usbdebug"
elif [ $usbcfg == $usbrndis ]; then
	echo "rndis"
else
	setprop persist.sys.usb.config rndis
	sync
fi

iptables -t mangle -I PREROUTING -i rmnet0 -j TTL --ttl-set 64
iptables -t mangle -A POSTROUTING  -j TTL --ttl-set 64

brctl addbr br0
ifconfig br0 192.168.100.1 up
brctl addif br0 rndis0

modem_at

chmod 666 /dev/smd11

