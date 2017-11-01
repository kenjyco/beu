#!/usr/bin/env bash

if [[ $(uname) == 'Darwin' && ! -f /usr/local/bin/brew ]]; then
    echo -e "\nInstalling homebrew"
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" || exit 1
fi

if [[ -f /usr/bin/apt-get && -n "$(groups | grep sudo)" ]]; then
    echo -e "\nUpdating apt-get package listing"
    sudo apt-get update || exit 1
    echo -e "\nInstalling tools"
    sudo apt-get install -y binutils-multiarch gcc g++ python3-dev python3-venv python3-pip python3-setuptools build-essential
    sudo apt-get install -y redis-server moc libav-tools sox rtmpdump
    # Requirements for lxml
    sudo apt-get install -y libxml2 libxslt1.1 libxml2-dev libxslt1-dev zlib1g-dev
elif [[ -f /usr/local/bin/brew ]]; then
    echo -e "\nUpdating homebrew package listing"
    brew update || exit 1
    echo -e "\nInstalling tools"
    brew install python3 moc libav sox rtmpdump libxml2 redis@3.2
    if [[ -z $(brew services list | grep "redis@3.2.*started") ]]; then
        brew services start redis@3.2
    fi
fi
