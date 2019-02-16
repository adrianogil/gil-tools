source $AGIL_SCRIPTS_DIR/tools.sh

alias gil-install="python2 $AGIL_SCRIPTS_DIR/python/gil_install.py"


function setup-as-gil-project()
{
    target_install_dir=$1

    touch bashrc.sh
    gil-install -c $target_install_dir
    
    ga bashrc.sh
    ga install.gil

    gc -m "Setup as gil-project"
}