

function install_mac_utils()
{
    brew install bat
    brew install ripgrep
    brew install fd
    brew install exa
}

function gil-clone()
{
    # git clone and enter repo directory

    target_url=$1
    target_folder=$2
    gol $1 $target_folder
    mydirs -s
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
