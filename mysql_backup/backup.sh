#!/bin/bash
echo "Mysql 备份程序 V 1.0.0 ."
echo
today=`date "+%Y%m%d"`
command="mysqldump -h192.168.1.210 -uroot -p123456 $1 > $1-$today-backup.sql"
echo $command
echo
echo `$command`
# myqldump -h192.168.1.210 -uroot -p123456 $1 > $1-$today-backup.sql
