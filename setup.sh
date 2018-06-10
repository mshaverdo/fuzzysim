#!/bin/bash

#./makeself/makeself.sh --tar-extra "--exclude=.git" sources/ ./setup.run "FuzzySim" ./setup.sh

SRC="`pwd`"
cd ..

WHERE="${HOME}/fuzzysim"
if [[ -n $1 ]]; then
    WHERE="$1"
fi
echo "moving application to ${WHERE}..."

mkdir -p "$WHERE"
mv -f $SRC/* "$WHERE"

echo Done!
