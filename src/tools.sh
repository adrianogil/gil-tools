

function install_mac_utils()
{
    brew install bat
    brew install ripgrep
    brew install fd
    brew install exa
}


TEMP_REPOS_DIR=/tmp/tmp_repos/

function gil-clone()
{
    # git clone, enter repo directory and setup as gil-project
    current_dir=$PWD

    mkdir -p ${TEMP_REPOS_DIR}
    cd ${TEMP_REPOS_DIR}

    target_url=$1
    target_folder=$2

    if [ -z "$target_folder" ]; then
        target_folder=${target_url##*/}
        # remove .git
        target_folder=${target_folder%.git}
    fi

    echo "# Downloading repo"
    gol $1 $target_folder

    default_target_folder=${current_dir}/${target_folder}
    new_dir=$(gil-install --verify-dir ${default_target_folder})

    cd..

    echo "# Cloning repo to ${new_dir}"
    mv ${TEMP_REPOS_DIR}/${target_folder} ${new_dir}/

    cd ${new_dir}/

    gil-install -i
}

# Convert a project to be a gil-project
function gil-project-setup()
{
    target_install_dir=$1

    touch bashrc.sh
    gil-install -c $target_install_dir

    ga bashrc.sh
    ga install.gil

    gc -m "Setup as gil-project"
}
