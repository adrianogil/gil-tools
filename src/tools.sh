

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
    rw -s
}