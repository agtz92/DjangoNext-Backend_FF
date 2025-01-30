# build_files.sh
# Los colores se aplican encerrando el texto en las siguientes llaves: \e[32m \e[0m
echo -e "\e[32mStart build_files.sh ...\e[0m"
echo -e "\e[32mInstall python\e[0m"
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9
echo -e "\e[32mVersions\e[0m"
python3.9 -m pip --version
pip3 --version
echo -e "\e[32mUpgrade Pip\e[0m"
pip3 install -U pip
echo -e "\e[32mInstall requirements.txt\e[0m"
pip3 install -r requirements.txt

# Make migrations
echo "Making migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

python3.9 manage.py collectstatic --noinput --clear

echo "Build process completed!"

