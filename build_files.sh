# build_files.sh
echo "TOPO ES Guapsiimo..."
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9
echo "TOPO ES Guapo..."
python3.9 -m pip --version
pip3 --version
echo "TOPO ES PUTO..."
pip3 install -U pip
echo "TOPO ES SEXY..."
pip3 install -r requirements.txt

# Make migrations
echo "Making migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

python3.9 manage.py collectstatic --noinput --clear

echo "Build process completed!"

