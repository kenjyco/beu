#!/usr/bin/env bash

if [[ ! -f $HOME/.zshrc && ! -f $HOME/.bashrc && ! -f $HOME/.bash_profile ]]; then
    echo -e "\nCreating an empty $HOME/.bash_profile"
    touch $HOME/.bash_profile
fi

if [[ $(uname) == "Darwin" ]]; then
    if [[ ! -f /usr/local/bin/brew ]]; then
        echo -e "\nInstalling homebrew"
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" || exit 1
    fi

    echo -e "\nGetting the list of packages already installed with brew"
    _installed=$(brew list -1)
    _brew_install_or_upgrade() {
        for x in "$@"; do
            echo "checking $x"
            if [[ -z "$(echo -e "$_installed" | grep "$x")" ]]; then
                brew install $x
            else
                brew upgrade $x 2>/dev/null
            fi
        done
    }
fi

CLOUD_INSTANCE=
[[ -d /var/lib/cloud/instance ]] && CLOUD_INSTANCE=yes

if [[ -f /usr/bin/apt-get && -n "$(groups | grep sudo)" ]]; then
    echo -e "\nUpdating apt-get package listing"
    sudo apt-get update || exit 1
    echo -e "\nInstalling tools"
    sudo apt-get install -y binutils-multiarch gcc g++ python3-dev python3-venv python3-pip python3-setuptools build-essential
    sudo apt-get install -y libav-tools
    [[ $? -ne 0 ]] && sudo apt-get install -y ffmpeg
    sudo apt-get install -y redis-server sox rtmpdump
    # Requirements for lxml
    sudo apt-get install -y libxml2 libxslt1.1 libxml2-dev libxslt1-dev zlib1g-dev
    if [[ -z "$CLOUD_INSTANCE" ]]; then
        sudo apt-get install -y moc vlc imagemagick wmctrl
        # Requirements for dbus-python
        sudo apt-get install -y pkg-config libdbus-1-dev libdbus-glib-1-dev
    fi
elif [[ -f /usr/local/bin/brew ]]; then
    echo -e "\nUpdating homebrew package listing"
    brew update || exit 1
    echo -e "\nInstalling/upgrading tools"
    _brew_install_or_upgrade python3 moc libav sox rtmpdump libxml2 redis@3.2
    if [[ -z $(brew services list | grep "redis@3.2.*started") ]]; then
        brew services start redis@3.2
    fi
fi

if [[ ! -d "$HOME/.beu" ]]; then
    echo -e "\nCreating $HOME/.beu directory"
    mkdir -p $HOME/.beu
fi

cd $HOME/.beu || exit 1
PYTHON="python3"
PIP="venv/bin/pip3"
if [[ $(uname) =~ "MINGW" ]]; then
    PYTHON="python"
    PIP="venv/Scripts/pip"
fi

echo -e "\nCreating $HOME/.beu/venv virtual environment and installing"
[[ ! -d venv ]] && $PYTHON -m venv venv
PYTHON=$(dirname $PIP)/python
$PYTHON -m pip install --upgrade pip wheel
if [[ $(uname) =~ "MINGW" ]]; then
    $PIP install beu ipython
elif [[ $(uname) == "Darwin" ]]; then
    $PIP install beu ipython pdbpp mocp mocp-cli
elif [[ -z "$CLOUD_INSTANCE" ]]; then
    $PIP install beu ipython pdbpp mocp mocp-cli vlc-helper
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
