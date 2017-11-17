if [[ -d "$HOME/.beu/venv/lib/python3.5/site-packages" ]]; then
    BEU_SITE_PACKAGES="$HOME/.beu/venv/lib/python3.5/site-packages"
elif [[ -d "$HOME/.beu/venv/lib/python3.6/site-packages" ]]; then
    BEU_SITE_PACKAGES="$HOME/.beu/venv/lib/python3.6/site-packages"
fi

beu-site-packages() {
    cd "$BEU_SITE_PACKAGES"
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

beu-repos-list() {
    level=$1
    [[ ! "$level" =~ [0-9]+ ]] && level=3
    find ~ -maxdepth $level -type d -name ".git" -print0 |
    xargs -0 -I {} dirname {} 2>/dev/null |
    sort |
    egrep '(beu|bg-helper|chloop|input-helper|mocp|parse-helper|redis-helper|vlc-helper|yt-helper)'
}

BEU_REPOS_LIST=$(beu-repos-list)
_REPO_BEU=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep beu$)
_REPO_BG_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep bg-helper$)
_REPO_CHLOOP=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep chloop$)
_REPO_INPUT_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep input-helper$)
_REPO_MOCP=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep mocp$)
_REPO_MOCP_CLI=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep mocp-cli$)
_REPO_PARSE_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep parse-helper$)
_REPO_REDIS_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep redis-helper$)
_REPO_VLC_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep vlc-helper$)
_REPO_YT_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep yt-helper$)

which colordiff &>/dev/null
[[ $? -eq 0 ]] && _use_colordiff="yes"

_beu-repos-diff() {
    [[ -z "$BEU_REPOS_LIST" ]] && return
    [[ -d "$_REPO_BEU" ]] && diff -r "$BEU_SITE_PACKAGES/beu" "$_REPO_BEU/beu"
    [[ -d "$_REPO_BG_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/bg_helper" "$_REPO_BG_HELPER/bg_helper"
    [[ -d "$_REPO_CHLOOP" ]] && diff -r "$BEU_SITE_PACKAGES/chloop" "$_REPO_CHLOOP/chloop"
    [[ -d "$_REPO_INPUT_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/input_helper" "$_REPO_INPUT_HELPER/input_helper"
    [[ -d "$_REPO_MOCP" ]] && diff -r "$BEU_SITE_PACKAGES/moc" "$_REPO_MOCP/moc"
    [[ -d "$_REPO_MOCP_CLI" ]] && diff -r "$BEU_SITE_PACKAGES/mocp_cli" "$_REPO_MOCP_CLI/mocp_cli"
    [[ -d "$_REPO_PARSE_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/parse_helper" "$_REPO_PARSE_HELPER/parse_helper"
    [[ -d "$_REPO_REDIS_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/redis_helper" "$_REPO_REDIS_HELPER/redis_helper"
    [[ -d "$_REPO_VLC_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/vlc_helper" "$_REPO_VLC_HELPER/vlc_helper"
    [[ -d "$_REPO_YT_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/yt_helper" "$_REPO_YT_HELPER/yt_helper"
}

beu-repos-diff() {
    if [[ -n "$_use_colordiff" ]]; then
        _beu-repos-diff 2>/dev/null | egrep -v '(Only in|No such file)' | colordiff | less -rFX
    else
        _beu-repos-diff 2>/dev/null | egrep -v '(Only in|No such file)' | less -FX
    fi
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
