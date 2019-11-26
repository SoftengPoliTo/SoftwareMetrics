#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BASEDIR="${DIR}/CC++_Tools"

CCCC="${BASEDIR}/CCCC/cccc"
TOKEI="${BASEDIR}/Tokei/tokei"
#HALSTEAD_TOOL="${BASEDIR}/Halstead_Metrics/halstead-metrics.sh"
HALSTEAD_TOOL="java -Duser.country=US -Duser.language=en -jar ${BASEDIR}/Halstead_Metrics/Halstead-Metrics.jar"
MI_TOOL="${BASEDIR}/Maintainability_Index/lizard"

if [ $# -eq 0 ]; then
	echo "No path to analyze!"
	echo "USAGE: $0 <path_to_the_code>";
	exit
fi

OUTPUT_DIR="$(date +results_%Y.%m.%d_%H.%M.%S)"
mkdir $OUTPUT_DIR

echo " ### RUNNING TOKEI ###"
$TOKEI -o json "$1" > "${OUTPUT_DIR}/output_tokei.json"

echo " ### RUNNING CCCC ###"
$CCCC --outdir=${OUTPUT_DIR} "$1"

echo " ### RUNNING MI_TOOL ###"
$MI_TOOL -X "$1" > "${OUTPUT_DIR}/output_mi_tool.xml"

echo " ### RUNNING HALSTEAD_METRICS_TOOL ###"
cd $OUTPUT_DIR
$HALSTEAD_TOOL "$1"
cd ..