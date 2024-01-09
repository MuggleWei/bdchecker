#!/bin/bash

origin_dir="$(dirname "$(readlink -f "$0")")"
cd $origin_dir

if [ -d "venv" ]; then
	echo "venv already exists"
else
	echo "create venv"
	python -m venv venv
fi

source venv/bin/activate

if [ $? -eq 0 ]; then
	echo "success source activate"
else
	echo "failed source activate"
	exit 1
fi

pip install -r requirements-dev.txt

pyinstaller -F bdchecker/main.py --distpath dist/bdchecker -n bdchecker
cp -r ./etc dist/bdchecker/
cp ./README.md dist/bdchecker/
cp ./README_cn.md dist/bdchecker/
cp ./LICENSE dist/bdchecker/
