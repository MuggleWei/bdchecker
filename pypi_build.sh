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

python -m pip install --upgrade build
python -m build
