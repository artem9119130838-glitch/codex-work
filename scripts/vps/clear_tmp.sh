#!/bin/sh
echo "was:" &&  du -h /tmp
find /tmp -name "*.tmp" -type f -mtime +5 -exec rm -rf {} \;
echo "now:" &&  du -h /tmp
