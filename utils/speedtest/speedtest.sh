#准备好所需文件
wget -O singtools.tar.gz https://github.com/Kdwkakcs/singtools/releases/download/vv0.2.0/singtools_linux32.tar.gz
tar -zxvf singtools.tar.gz
chmod +x ./singtools
#运行 SingTools 测试
./singtools test -i ./sub/sub_merge.txt -c ./utils/speedtest/singtools_config.json -o out.json -f ""
