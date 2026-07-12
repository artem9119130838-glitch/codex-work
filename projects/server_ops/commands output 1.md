Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-216-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Сб 20 июн 2026 17:56:19 UTC

  System load:                      1.62
  Usage of /Storage:                63.4% of 245.02GB
  Memory usage:                     66%
  Swap usage:                       16%
  Processes:                        223
  Users logged in:                  0
  IPv4 address for br-51a95314f553: 172.20.0.1
  IPv4 address for br-8ae5f2d282b6: 172.18.0.1
  IPv4 address for br-99305089ee65: 172.19.0.1
  IPv4 address for docker0:         172.17.0.1
  IPv4 address for eth0:            109.248.170.181
  IPv4 address for lxcbr0:          10.0.3.1
  IPv4 address for tun0:            172.16.33.1
  IPv4 address for wg0:             10.10.0.1

Last login: Sat Jun 20 13:20:13 2026 from 10.10.0.5
root@server:~# uptime && free -h && df -h
 17:56:30 up 48 days, 11:53,  1 user,  load average: 1,37, 1,19, 1,07
              total        used        free      shared  buff/cache   available
Mem:          9,7Gi       6,2Gi       200Mi       2,0Gi       3,3Gi       1,2Gi
Swap:           9Gi       1,7Gi       8,3Gi
Filesystem      Size  Used Avail Use% Mounted on
udev            4,9G     0  4,9G   0% /dev
tmpfs           995M  1,4M  994M   1% /run
/dev/vda1        78G   61G   17G  79% /
tmpfs           4,9G  856K  4,9G   1% /dev/shm
tmpfs           5,0M     0  5,0M   0% /run/lock
tmpfs           4,9G     0  4,9G   0% /sys/fs/cgroup
/dev/vda15      105M  6,1M   99M   6% /boot/efi
/dev/sda        246G  156G   78G  67% /Storage
tmpfs           995M  4,0K  995M   1% /run/user/129
/dev/sr0        364K  364K     0 100% /media/root/CONTEXT
tmpfs           995M  8,0K  995M   1% /run/user/0
overlay         246G  156G   78G  67% /Storage/docker-data/overlay2/5c1dfe8eadf58486fdfd8c34103c69e21e6f8b9c2dabb286cd61cd2c7dc495fe/merged
shm              64M     0   64M   0% /Storage/docker-data/containers/36393bc8952ec7c656ef268f4c924f3222806ad587baaf34a04fb4d80e9b76d0/mounts/shm
overlay         246G  156G   78G  67% /Storage/docker-data/overlay2/aedcbeae482f5d1254470586a38ced9ba7a60b7dce888ac7b02eab1c29bd6e0e/merged
shm              64M     0   64M   0% /Storage/docker-data/containers/d84a37f957fe88ee2f8d68405491d01234eddd06261df4d9f417af1a00b8bbda/mounts/shm
root@server:~# sudo wg show
interface: wg0
  public key: RL0dKV7TqTfyiMd61AHleaMvad/jPXvmg54D3rIt0gU=
  private key: (hidden)
  listening port: 51820

peer: 25wPssewBDqp9DLPpd/PIyh110TTeIZ42ShN8aQzpxY=
  endpoint: 178.66.131.99:25758
  allowed ips: 10.10.0.5/32
  latest handshake: 17 seconds ago
  transfer: 34.47 GiB received, 12.70 GiB sent

peer: ESreXPGy+JDIZjZwmYAOEQaA/lYrARjZEAojBSHCSik=
  endpoint: 178.157.147.204:6693
  allowed ips: 10.10.0.2/32
  latest handshake: 33 seconds ago
  transfer: 7.15 GiB received, 7.93 GiB sent

peer: bMNTPRskyJVnBBj15NDbOT8v/m3p3rfPFu7bIyHRWVA=
  endpoint: 188.170.72.177:32115
  allowed ips: 10.10.0.3/32
  latest handshake: 1 minute, 21 seconds ago
  transfer: 14.90 GiB received, 38.38 GiB sent

peer: WWyL55cssDQ2uAhBMbQ33vDJWkFbHICyzUW/D1kTtFQ=
  endpoint: 178.66.131.99:25783
  allowed ips: 10.10.0.4/32
  latest handshake: 2 minutes, 48 seconds ago
  transfer: 12.03 GiB received, 29.88 GiB sent

peer: O1FohmwRlbXBiEB9maWRxNudk32VwJVFBNiKPUgwVzg=
  endpoint: 184.22.188.233:51580
  allowed ips: 10.10.0.8/32
  latest handshake: 7 minutes, 35 seconds ago
  transfer: 1.77 GiB received, 15.42 GiB sent

peer: U+ycGwbOKlk+4cOk/g5kxmy8mNDP0SN5AW8oQKoR5HE=
  endpoint: 89.148.224.232:56072
  allowed ips: 10.10.0.6/32
  latest handshake: 8 minutes, 8 seconds ago
  transfer: 5.12 GiB received, 17.91 GiB sent

peer: 5opdMXg8CsZp+U9DqUpCa7hhJs7Ok8CbgBKIXu9EMC0=
  endpoint: 85.140.92.31:57188
  allowed ips: 10.10.0.7/32
  latest handshake: 2 hours, 46 minutes, 43 seconds ago
  transfer: 6.10 GiB received, 15.28 GiB sent

peer: SgDsgPMSSoG7NBbMz3eLf/u7LbJqJll8tWupCus4YzE=
  allowed ips: 10.10.0.9/32
root@server:~# ^C
root@server:~# ping -c 4 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=110 time=96.0 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=110 time=95.8 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=110 time=95.7 ms
64 bytes from 8.8.8.8: icmp_seq=4 ttl=110 time=95.8 ms

--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 95.676/95.830/96.027/0.126 ms
root@server:~# sudo journalctl -u wg-quick@wg0 --no-pager -n 20
-- Logs begin at Mon 2026-05-18 03:19:53 UTC, end at Sat 2026-06-20 17:57:56 UTC. --
-- No entries --
root@server:~#
