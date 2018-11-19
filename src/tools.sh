

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
    gol $1
    mydirs -s
    rw -s
}