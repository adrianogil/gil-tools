

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
    # git clone and enter repo directory

    current_dir=$PWD

    mkdir -p ${TEMP_REPOS_DIR}
    cd ${TEMP_REPOS_DIR}

    target_url=$1
    target_folder=$2
    gol $1 $target_folder

    new_dir=$(gil-install --verify-dir ${current_dir})

    repo_folder_name=${PWD##*/}

    cd..

    mv ${repo_folder_name} ${new_dir}/

    cd ${new_dir}/repo_folder_name

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
