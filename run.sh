# USAGE:
# ./run.sh install - install into python virtual environment
# ./run.sh socket - run as uwsgi socket (for production use)
# ./run.sh http - run as http (for development use)

for arg in "$@"
do
    if [ "$arg" == "install" ]
    then
        virtualenv --python=python3 venv
        source venv/bin/activate
        pip3 install -e .
        python3 -m spacy download en
        mkdir -p identibooru/static/files/
        mkdir -p identibooru/static/.thumbnails/
        mkdir -p logs/
        touch logs/access.log
        touch logs/error.log
        break
    fi

    if [ "$arg" == "make-release" ]
    then
        zip ../identibooru-release.zip . -r9 -x \*.git\* -x \*.eggs\* -x \*config -x \*logs/\* -x \*venv/\* -x \*identibooru/static/files/\*
        stat ../identibooru-release.zip
        break
    fi

    source venv/bin/activate
    source config

    echo "=== Configuration ==="
    echo "Host:" $identibooru_Host
    echo "Port:" $identibooru_Port

    echo "=== Starting Server ==="
    if [ "$arg" == "socket" ]
    then
        echo "Running in socket mode..."
        echo "Attempting to set up socket on $identibooru_Host:$identibooru_Port..."
        uwsgi --socket $identibooru_Host:$identibooru_Port --module identibooru --master --enable-threads --workers 8 --processes 8 --threads 4 --callab app -H venv
    elif [ "$arg" == "http" ] || [ -z "$arg" ]
    then
        echo "Running in http mode..."
        flask run --host=$identibooru_Host --port=$identibooru_Port
    fi
done
