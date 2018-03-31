soho_router
\\\\\\\\\\\

`soho_router` aims to be _most_ of what you need to build a reasonably secure, easy to use router. It includes a CLI
interface, but is designed to be easily adapted to work with a "REST" API or similar. Unless you know what you're doing
you'd be wise to just stick to the CLI. Which is bundled. So in a sense, this package is "all you need" to set up an
easily configurable SOHO router. It's a systems interface library (sort of) and it's also a complete usable application.

Design
======

There are two main modules: `system.py` and `interface.py`.

`system.py` has all the code to talk to the system using
ctypes, ffi, etc. Stuff that modifies the system's iptables for example live here.

`interfac.py` a low-level interface for tool implementers. For example:


.. code:: python

    firewall = Firewall()
    firewall.register_event(action='reinit', event=(ALL_INTERFACES, UP_DOWN))

    vpn = VPN(name='larry')
    if not vpn.is_up():
        vpn.start():
    while True:
        time.sleep(30)
        if not vpn.is_usable():  # can "ping" through or something.
            vpn.restart()

contrived, silly code, but you get it.

The `soho_router_ctl` contains code that interacts with `interface.py`, both serving as a working example of how to
"interface" and also a usable utility.
