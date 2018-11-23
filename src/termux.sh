function termux-install()
{
    cd $TERMUX_PATH
    ikc
    pkg install openssh
}