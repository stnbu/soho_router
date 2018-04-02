#!/usr/bin/env python3

import iptc
import subprocess


def system(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise RuntimeError(err)
    return out


def flush_netfilter():
    commands = """
    iptables --flush
    iptables -P INPUT ACCEPT
    iptables -P FORWARD ACCEPT
    iptables -P OUTPUT ACCEPT
    """

    for command in commands.splitlines():
        command = command.strip()
        if not command:
            continue
        command = command.split()
        system(command)


def sysctl(param, value):
    command = [
        'sysctl',
        '-w',
        '%s=%s' % (param, value),
    ]
    system(command)


def sane_nat(lan, internet):

    input_ = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
    postrouting = iptc.Chain(iptc.Table(iptc.Table.NAT), "POSTROUTING")
    forward = iptc.Chain(iptc.Table(iptc.Table.FILTER), "FORWARD")

    # /sbin/iptables -A INPUT -i internet -m state --state RELATED,ESTABLISHED -j ACCEPT
    rule = iptc.Rule()
    rule.in_interface = internet
    rule.target = iptc.Target(rule, "ACCEPT")
    match = iptc.Match(rule, "state")
    match.state = "RELATED,ESTABLISHED"
    rule.add_match(match)
    input_.append_rule(rule)


    # -A INPUT -m state --state NEW -j REJECT
    # iptables -A INPUT -i eth0 -j DROP
    rule = iptc.Rule()
    rule.in_interface = internet
    rule.target = iptc.Target(rule, "REJECT")
    match = iptc.Match(rule, "state")
    match.state = "NEW"
    rule.add_match(match)
    input_.insert_rule(rule)

    # /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    rule = iptc.Rule()
    rule.out_interface = internet
    rule.target = iptc.Target(rule, "MASQUERADE")
    postrouting.insert_rule(rule)

    # /sbin/iptables -A FORWARD -i internet -o lan -m state --state RELATED,ESTABLISHED -j ACCEPT
    rule = iptc.Rule()
    rule.out_interface = lan
    rule.in_interface = internet
    rule.target = iptc.Target(rule, "ACCEPT")
    match = iptc.Match(rule, "state")
    match.state = "RELATED,ESTABLISHED"
    rule.add_match(match)
    forward.append_rule(rule)

    # /sbin/iptables -A FORWARD -i lan -o internet -j DROP
    rule = iptc.Rule()
    rule.out_interface = 'ens2'
    rule.in_interface = 'enp63s0'
    rule.target = iptc.Target(rule, "REJECT")
    forward.append_rule(rule)

    # /sbin/iptables -A FORWARD -i lan -o internet -j ACCEPT
    rule = iptc.Rule()
    rule.out_interface = internet
    rule.in_interface = lan
    rule.target = iptc.Target(rule, "ACCEPT")
    forward.append_rule(rule)


if __name__ == '__main__':

    import sys
    flush_netfilter()
    sysctl('net.ipv4.ip_forward', 1)
    import sys
    internet = sys.argv[1]
    sane_nat(lan='enp63s0', internet=internet)
