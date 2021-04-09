if [[ -d "$HOME/.beu/venv/lib/python3.5/site-packages" ]]; then
    BEU_SITE_PACKAGES="$HOME/.beu/venv/lib/python3.5/site-packages"
elif [[ -d "$HOME/.beu/venv/lib/python3.6/site-packages" ]]; then
    BEU_SITE_PACKAGES="$HOME/.beu/venv/lib/python3.6/site-packages"
elif [[ -d "$HOME/.beu/venv/lib/python3.7/site-packages" ]]; then
    BEU_SITE_PACKAGES="$HOME/.beu/venv/lib/python3.7/site-packages"
elif [[ -d "$HOME/.beu/venv/lib/python3.8/site-packages" ]]; then
    BEU_SITE_PACKAGES="$HOME/.beu/venv/lib/python3.8/site-packages"
elif [[ -d "$HOME/.beu/venv/Lib/site-packages" ]]; then
    BEU_SITE_PACKAGES="$HOME/.beu/venv/Lib/site-packages"
fi

CLOUD_INSTANCE=
[[ -d /var/lib/cloud/instance ]] && CLOUD_INSTANCE=yes

beu-site-packages() {
    cd "$BEU_SITE_PACKAGES"
}

beu-reinstall() {
    oldpwd=$(pwd)
    [[ ! -d "$HOME/.beu" ]] && mkdir -p "$HOME/.beu"
    cd "$HOME/.beu"
    rm -rf venv 2>/dev/null
    find . \( -name '__pycache__' -o -name '.eggs' -o -name '*.egg-info' -o -name 'build' -o -name 'dist' \) -print0 |
        xargs -0 rm -rf
    curl -o- https://raw.githubusercontent.com/kenjyco/beu/master/install.sh | bash
    cd "$oldpwd"
}

beu-update() {
    [[ ! -d "$HOME/.beu/venv" ]] && echo "$HOME/.beu/venv does not exist" && return 1
    oldpwd=$(pwd)
    cd $HOME/.beu
    pip_args=(--no-warn-script-location --upgrade --upgrade-strategy eager)
    PYTHON="python3"
    PIP="venv/bin/pip3"
    if [[ $(uname) =~ "MINGW" ]]; then
        PYTHON="python"
        PIP="venv/Scripts/pip"
    fi
    PYTHON=$(dirname $PIP)/python
    $PYTHON -m pip install --upgrade pip wheel

    if [[ $(uname) =~ "MINGW" ]]; then
        $PIP install ${pip_args[@]} beu ipython
    elif [[ $(uname) == "Darwin" ]]; then
        $PIP install ${pip_args[@]} beu ipython mocp mocp-cli
    elif [[ -z "$CLOUD_INSTANCE" ]]; then
        $PIP install ${pip_args[@]} beu ipython mocp mocp-cli vlc-helper
    fi

    echo -e "\nSaving latest wrappers.sh"
    curl https://raw.githubusercontent.com/kenjyco/beu/master/wrappers.sh > wrappers.sh
    cd "$oldpwd"
}

BEU_REPO_NAMES=(
    aws-info-helper
    beu
    bg-helper
    chloop
    dt-helper
    easy-workflow-manager
    fs-helper
    input-helper
    jira-helper
    mocp
    mongo-helper
    parse-helper
    redis-helper
    settings-helper
    sql-helper
    vlc-helper
    webclient-helper
    yt-helper
)

beu-clone-all() {
    for repo in "${BEU_REPO_NAMES[@]}"; do
        git clone https://github.com/kenjyco/$repo ~/.beu/cloned_repos/$repo
    done
}

beu-repos-list() {
    level=$1
    [[ ! "$level" =~ [0-9]+ ]] && level=5
    find ~ -maxdepth $level \( -path ~/Library -o -path ~/.beu \) -prune -o -type d -name ".git" -print0 |
    xargs -0 -I {} dirname {} 2>/dev/null |
    sort |
    egrep $(echo ${BEU_REPO_NAMES[@]} | tr ' ' '|')
}

BEU_REPOS_LIST=$(beu-repos-list)
_REPO_AWS_INFO_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep aws-info-helper$)
_REPO_BEU=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep beu$)
_REPO_BG_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep bg-helper$)
_REPO_CHLOOP=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep chloop$)
_REPO_DT_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep dt-helper$)
_REPO_EASY_WORKFLOW_MANAGER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep easy-workflow-manager$)
_REPO_FS_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep fs-helper$)
_REPO_INPUT_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep input-helper$)
_REPO_JIRA_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep jira-helper$)
_REPO_MOCP=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep mocp$)
_REPO_MOCP_CLI=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep mocp-cli$)
_REPO_MONGO_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep mongo-helper$)
_REPO_PARSE_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep parse-helper$)
_REPO_REDIS_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep redis-helper$)
_REPO_SETTINGS_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep settings-helper$)
_REPO_SQL_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep sql-helper$)
_REPO_VLC_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep vlc-helper$)
_REPO_WEBCLIENT_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep webclient-helper$)
_REPO_YT_HELPER=$(echo $BEU_REPOS_LIST | tr ' ' '\n' | grep yt-helper$)

_get_beu_repos_base_dir() {
    for repo in $(beu-repos-list | tr '\n' '\0' | xargs -0); do
        dirname "$repo"
    done | uniq -c | sort -n | tail -n 1 | egrep -o '\/.*$'
}

_lasttag() {
    git describe --tags $(git rev-list --tags --max-count=1)
}

BEU_REPOS_DIR=$(_get_beu_repos_base_dir)

which colordiff &>/dev/null
[[ $? -eq 0 ]] && _use_colordiff="yes"

_beu-repos-diff-with-site-packages() {
    [[ -z "$BEU_REPOS_LIST" ]] && return
    [[ -d "$_REPO_AWS_INFO_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/aws_info_helper" "$_REPO_AWS_INFO_HELPER/aws_info_helper"
    [[ -d "$_REPO_BEU" ]] && diff -r "$BEU_SITE_PACKAGES/beu" "$_REPO_BEU/beu"
    [[ -d "$_REPO_BG_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/bg_helper" "$_REPO_BG_HELPER/bg_helper"
    [[ -d "$_REPO_CHLOOP" ]] && diff -r "$BEU_SITE_PACKAGES/chloop" "$_REPO_CHLOOP/chloop"
    [[ -d "$_REPO_DT_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/dt_helper" "$_REPO_DT_HELPER/dt_helper"
    [[ -d "$_REPO_EASY_WORKFLOW_MANAGER" ]] && diff -r "$BEU_SITE_PACKAGES/easy_workflow_manager" "$_REPO_EASY_WORKFLOW_MANAGER/easy_workflow_manager"
    [[ -d "$_REPO_FS_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/fs_helper" "$_REPO_FS_HELPER/fs_helper"
    [[ -d "$_REPO_INPUT_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/input_helper" "$_REPO_INPUT_HELPER/input_helper"
    [[ -d "$_REPO_JIRA_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/jira_helper" "$_REPO_JIRA_HELPER/jira_helper"
    [[ -d "$_REPO_MOCP" ]] && diff -r "$BEU_SITE_PACKAGES/moc" "$_REPO_MOCP/moc"
    [[ -d "$_REPO_MOCP_CLI" ]] && diff -r "$BEU_SITE_PACKAGES/mocp_cli" "$_REPO_MOCP_CLI/mocp_cli"
    [[ -d "$_REPO_MONGO_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/mongo_helper" "$_REPO_MONGO_HELPER/mongo_helper"
    [[ -d "$_REPO_PARSE_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/parse_helper" "$_REPO_PARSE_HELPER/parse_helper"
    [[ -d "$_REPO_REDIS_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/redis_helper" "$_REPO_REDIS_HELPER/redis_helper"
    [[ -d "$_REPO_SETTINGS_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/settings_helper" "$_REPO_SETTINGS_HELPER/settings_helper"
    [[ -d "$_REPO_SQL_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/sql_helper" "$_REPO_SQL_HELPER/sql_helper"
    [[ -d "$_REPO_VLC_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/vlc_helper" "$_REPO_VLC_HELPER/vlc_helper"
    [[ -d "$_REPO_WEBCLIENT_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/webclient_helper" "$_REPO_VLC_HELPER/webclient_helper"
    [[ -d "$_REPO_YT_HELPER" ]] && diff -r "$BEU_SITE_PACKAGES/yt_helper" "$_REPO_YT_HELPER/yt_helper"
    if [[ -s "$_REPO_BEU/wrappers.sh" ]]; then
        _output=$(diff "$HOME/.beu/wrappers.sh" "$_REPO_BEU/wrappers.sh")
        [[ -n "$_output" ]] && echo diff "$HOME/.beu/wrappers.sh" "$_REPO_BEU/wrappers.sh" && echo "$_output"
    fi
}

beu-repos-diff-with-site-packages() {
    if [[ -n "$_use_colordiff" ]]; then
        _beu-repos-diff-with-site-packages 2>/dev/null | egrep -v '(Only in|No such file|Binary files)' | colordiff | less -rFX
    else
        _beu-repos-diff-with-site-packages 2>/dev/null | egrep -v '(Only in|No such file|Binary files)' | less -FX
    fi
}

_beu-repos-diff-since-lasttag() {
    oldpwd=$(pwd)
    for repo in $(echo $BEU_REPOS_LIST | tr ' ' '\n'); do
        cd "$repo"
        the_diff=$(git diff $(_lasttag)..)
        if [[ -n "$the_diff" ]]; then
            echo -e "\n==============="
            echo "$(pwd)"
            echo "$the_diff"
        fi
    done
    cd "$oldpwd"
}

beu-repos-diff-since-lasttag() {
    if [[ -n "$_use_colordiff" ]]; then
        _beu-repos-diff-since-lasttag | colordiff | less -rFX
    else
        _beu-repos-diff-since-lasttag | less -FX
    fi
}

_beu-repos-diff() {
    oldpwd=$(pwd)
    for repo in $(echo $BEU_REPOS_LIST | tr ' ' '\n'); do
        cd "$repo"
        the_diff=$(git diff)
        if [[ -n "$the_diff" ]]; then
            echo -e "\n==============="
            echo "$(pwd)"
            echo "$the_diff"
        fi
    done
    cd "$oldpwd"
}

beu-repos-diff() {
    if [[ -n "$_use_colordiff" ]]; then
        _beu-repos-diff | colordiff | less -rFX
    else
        _beu-repos-diff | less -FX
    fi
}

beu-repos-commits-since-lasttag() {
    oldpwd=$(pwd)
    for repo in $(echo $BEU_REPOS_LIST | tr ' ' '\n'); do
        cd "$repo"
        the_log=$(git log --oneline $(_lasttag)..)
        if [[ -n "$the_log" ]]; then
            echo -e "\n==============="
            echo -e "$(pwd)\n$the_log"
        fi
    done | less -FX
    cd "$oldpwd"
}

beu-repos-status() {
    oldpwd=$(pwd)
    for repo in $(echo $BEU_REPOS_LIST | tr ' ' '\n'); do
        cd "$repo"
        the_status=$(git status -s)
        if [[ -n "$the_status" ]]; then
            echo -e "\n==============="
            echo -e "$(pwd)\n$the_status"
        fi
    done | less -FX
    cd "$oldpwd"
}

# -------------------- Wrappers to tools in ~/.beu/venv/bin  --------------------

ah-collection-update-ec2() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ah-collection-update-ec2 "$@"
}

ah-collection-update-route53() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ah-collection-update-route53 "$@"
}

ah-collection-update-s3() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ah-collection-update-s3 "$@"
}

ah-info-ec2() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ah-info-ec2 "$@"
}

ah-info-route53() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ah-info-route53 "$@"
}

ah-ssh-command-ec2() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ah-ssh-command-ec2 "$@"
}

beu-ipython() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/beu-ipython "$@"
}

alias b=beu-ipython

ipython-in-beu() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ipython "$@"
}

ewm-branch-from() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-branch-from "$@"
}

ewm-clear-qa() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-clear-qa "$@"
}

ewm-deploy-to-qa() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-deploy-to-qa "$@"
}

ewm-new-branch-from-source() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-new-branch-from-source "$@"
}

ewm-qa-to-source() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-qa-to-source "$@"
}

ewm-repo-info() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-repo-info "$@"
}

ewm-show-branches() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-show-branches "$@"
}

ewm-show-qa() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-show-qa "$@"
}

ewm-tag-release() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-tag-release "$@"
}

ewm-update-branch() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ewm-update-branch "$@"
}

jira-repl() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/jira-repl "$@"
}

if [[ ($(uname) == "Darwin" || -z "$CLOUD_INSTANCE") && ! $(uname) =~ "MINGW" ]]; then
    mocplayer() {
        PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/mocplayer "$@"
    }
    alias m=mocplayer
fi

ph-ddg() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-ddg "$@"
}

ph-download-file-as() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-download-file-as "$@"
}

ph-download-files() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-download-files "$@"
}

ph-soup-explore() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/ph-soup-explore "$@"
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

if [[ $(uname) != "Darwin" && -z "$CLOUD_INSTANCE" && ! $(uname) =~ "MINGW" ]]; then
    vlc-repl() {
        PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/vlc-repl "$@"
    }

    myvlc() {
        PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/myvlc "$@"
    }
fi

yt-download() {
    PYTHONPATH=$HOME/.beu $HOME/.beu/venv/bin/yt-download "$@"
}
