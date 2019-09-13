# !/bin/bash
cd /home/ubuntu/dataignition-tech/src/s3;
python3 urls_retrieve.py
./transfer_to_s3.sh
python3 s3_xml.py
