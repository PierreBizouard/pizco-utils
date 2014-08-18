Pizco-utils
=============

Depends
--------

Depends on py2exe if binaries are to be created (windows/deployable release)
Depends on pizco > 0.2


Goals
------

Provide a way to use pizco as a program under windows : 
    - look for services over the network
    - start the naming service on windows startup
    - add the naming service a systray utility
    - add a Qwidget for displaying a list of services (filterable/selectable)
    - add a Qwidget for displaying a list of ips

Features
---------

+ pizco-naming-bin compilation from setup.py / setup_build_console_bin.py (simple naming service executable)

+ pizco-naming-gui compilation from setup.py / setup_build_gui_bin.py (simple naming service executable)
    + view of services and services attributes
    + view of ips of beacons
    + restart the naming services

+ PizcoServicesWidget(selectable) + AutoRefresh

+ PizcoServicesDialog(selection+OK) + AutoRefresh

+ PizcoBeaconWidget(selection) + AutoRefresh

+ installation of pizco scripts in a dir in environ (setup.py)

+ environment variable configuration setup PZC_BEACON_PORT / PZC_NAMING_PORT / PZC_HIDE_TRACEBACK / PZC_SERIALIZER

