beu-site-packages() {
    if [[ -d "$HOME/.beu/venv/lib/python3.5/site-packages" ]]; then
        cd "$HOME/.beu/venv/lib/python3.5/site-packages"
    elif [[ -d "$HOME/.beu/venv/lib/python3.6/site-packages" ]]; then
        cd "$HOME/.beu/venv/lib/python3.6/site-packages"
    fi
}

beu-reinstall() {
    oldpwd=$(pwd)
    [[ ! -d "$HOME/.beu" ]] && mkdir -p "$HOME/.beu"
    cd "$HOME/.beu"
    rm -rf venv 2>/dev/null
    curl -o- https://raw.githubusercontent.com/kenjyco/beu/master/install.sh | bash
    cd "$oldpwd"
}

beu-update() {
    [[ ! -d "$HOME/.beu/venv" ]] && echo "$HOME/.beu/venv does not exist" && return 1
    oldpwd=$(pwd)
    cd $HOME/.beu
    if [[ $(uname) == 'Darwin' ]]; then
        venv/bin/pip3 install --upgrade beu
    else
        venv/bin/pip3 install --upgrade beu vlc-helper
    fi
    echo -e "\nSaving latest wrappers.sh"
    curl https://raw.githubusercontent.com/kenjyco/beu/master/wrappers.sh > wrappers.sh
    cd "$oldpwd"
}

rh-download-examples() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/rh-download-examples "$@"
}

rh-download-scripts() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/rh-download-scripts "$@"
}

rh-notes() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/rh-notes "$@"
}

rh-shell() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/rh-shell "$@"
}

yt-download() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/yt-download "$@"
}

yt-search() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/yt-search "$@"
}

ph-goo() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-goo "$@"
}

ph-you() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-you "$@"
}

ph-ddg() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-ddg "$@"
}

ph-download-files() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-download-files "$@"
}

ph-download-file-as() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-download-file-as "$@"
}

ph-soup-explore() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-soup-explore "$@"
}

mocplayer() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/mocplayer "$@"
}

beu-ipython() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/beu-ipython "$@"
}

beu-trending() {
    PYTHONPATH=$HOME $HOME/venv/bin/beu-trending "$@"
}

beu-related-to() {
    PYTHONPATH=$HOME $HOME/venv/bin/beu-related-to "$@"
}

if [[ $(uname) != 'Darwin' ]]; then
    vlc-repl() {
        PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/vlc-repl "$@"
    }

    myvlc() {
        PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/myvlc "$@"
    }
fi

alias m=mocplayer
alias b=beu-ipython
alias v='yt-search'
alias a='yt-search --audio-only'
alias trending=beu-trending
alias related=beu-related-to
alias pdfsearch='ph-goo --filetype pdf'
