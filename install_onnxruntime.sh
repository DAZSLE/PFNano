#!/bin/bash -xe

if [[ -z "$CMSSW_BASE" ]]; then
	echo '$CMSSW_BASE not defined -- run cmsenv first!'
fi

curdir=`pwd`
INSTALL_DIR="$CMSSW_BASE/ORT_INSTALL"

[[ -d $INSTALL_DIR ]] && rm -r $INSTALL_DIR
mkdir $INSTALL_DIR && cd $INSTALL_DIR

curl -s https://coli.web.cern.ch/coli/tmp/.221016-012210_ort_patch/ort_fix.tgz --retry 5 -o ort.tgz
tar -xf ort.tgz && rm ort.tgz

sed -i 's@_ONNXRUNTIME_INSTALL_PATH_@'"$INSTALL_DIR"'@g' $INSTALL_DIR/onnxruntime.xml
scram setup $INSTALL_DIR/onnxruntime.xml

cd $CMSSW_BASE/src
# rsync -avP /cvmfs/cms.cern.ch/$SCRAM_ARCH/cms/cmssw/$CMSSW_VERSION/src/PhysicsTools/ONNXRuntime $CMSSW_BASE/src/PhysicsTools
curl -s https://coli.web.cern.ch/coli/tmp/.221016-012210_ort_patch/physics_onnx.tgz --retry 5 -o physics_onnx.tgz
tar -xf physics_onnx.tgz && rm physics_onnx.tgz

cd $CMSSW_BASE/src/PhysicsTools/ONNXRuntime
scram b clean && scram b -j16

cp -a --remove-destination $INSTALL_DIR/lib/libonnxruntime.so* $CMSSW_BASE/external/$SCRAM_ARCH/lib
rm -r $INSTALL_DIR/lib

cd $curdir