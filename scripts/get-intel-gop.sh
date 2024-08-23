#!/bin/bash
set -e

# This script downloads and extracts IntelGopDriver DXEs. These are later used to build PCI Option
# ROMs by the 'igd-roms' tool, which can be used for getting GPU passthrough to behave exactly
# like on real hardware.

if [ ! -L "bootstrap.link" ]; then
	echo "Please run this script from your build directory."
	exit 1
fi

mkdir -p tools/intel-gop-dxe
cd tools/intel-gop-dxe
curl -L https://github.com/LongSoft/UEFITool/releases/download/A73/UEFIExtract_NE_A73_x64_linux.zip -o uefiextract.zip
echo "01961c9537ee2cad3f481ed5a0393ab04acc0d19e174017e58e5e83babea9bea uefiextract.zip" | sha256sum -c
unzip -o uefiextract.zip
rm uefiextract.zip

curl https://download.lenovo.com/pccbbs/mobiles/r0huj32w.exe -o r0huj32w.exe
innoextract -I "code\$GetExtractPath$/R0HET64W/\$0AR0H00.FL1" r0huj32w.exe
./uefiextract code\$GetExtractPath\$/R0HET64W/\$0AR0H00.FL1 unpack
cp code\$GetExtractPath\$/R0HET64W/\$0AR0H00.FL1.dump/Section_PE32_image_FF0C8745-3270-4439-B74F-3E45F8C77064_IntelGopDriver_body.bin SKL-1061.efi
rm -rf code\$GetExtractPath\$/ r0huj32w.exe
