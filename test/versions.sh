{
    echo "Nautilus Version:";
    nautilus --version;
    echo "";

    echo "Nautilus-Python Version:";
    python3 -c "import gi; gi.require_version('Nautilus', '3.0'); from gi.repository import Nautilus; print('Nautilus Python Bindings are available')" || echo "nautilus-python not found";
    echo "";

    echo "Nautilus-Python Package Info:";
    dpkg -l | grep python3-nautilus || rpm -qi nautilus-python;
    echo "";

    echo "Operating System Info:";
    lsb_release -a || cat /etc/os-release;
    echo "";

    echo "Kernel Version:";
    uname -r;
} 2>/dev/null