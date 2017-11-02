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
    sudo apt-get install -y vlc imagemagick wmctrl
    # Requirements for lxml
    sudo apt-get install -y libxml2 libxslt1.1 libxml2-dev libxslt1-dev zlib1g-dev
    # Requirements for dbus-python
    sudo apt-get install -y pkg-config libdbus-1-dev libdbus-glib-1-dev
elif [[ -f /usr/local/bin/brew ]]; then
    echo -e "\nUpdating homebrew package listing"
    brew update || exit 1
    echo -e "\nInstalling tools"
    brew install python3 moc libav sox rtmpdump libxml2 redis@3.2
    if [[ -z $(brew services list | grep "redis@3.2.*started") ]]; then
        brew services start redis@3.2
    fi
fi

if [[ ! -d "$HOME/.beu" ]]; then
    echo -e "\nCreating $HOME/.beu directory"
    mkdir -p $HOME/.beu
fi

cd $HOME/.beu || exit 1
echo -e "\nCreating $HOME/.beu/venv virtual environment and installing"
python3 -m venv venv && venv/bin/pip3 install --upgrade pip wheel
if [[ $(uname) == 'Darwin' ]]; then
    venv/bin/pip3 install beu
else
    venv/bin/pip3 install beu vlc-helper
fi
echo -e "\nSaving latest wrappers.sh"
curl https://raw.githubusercontent.com/kenjyco/beu/master/wrappers.sh > wrappers.sh

if [[ -f $HOME/.zshrc ]]; then
    if [[ -z "$(grep '.beu' $HOME/.zshrc)" ]]; then
        echo -e '\n[[ -f $HOME/.beu/wrappers.sh ]] && source $HOME/.beu/wrappers.sh' >> $HOME/.zshrc
    fi
fi

if [[ -f $HOME/.bashrc ]]; then
    if [[ -z "$(grep '.beu' $HOME/.bashrc)" ]]; then
        echo -e '\n[[ -f $HOME/.beu/wrappers.sh ]] && source $HOME/.beu/wrappers.sh' >> $HOME/.bashrc
    fi
elif [[ -f $HOME/.bash_profile ]]; then
    if [[ -z "$(grep '.beu' $HOME/.bash_profile)" ]]; then
        echo -e '\n[[ -f $HOME/.beu/wrappers.sh ]] && source $HOME/.beu/wrappers.sh' >> $HOME/.bash_profile
    fi
fi
