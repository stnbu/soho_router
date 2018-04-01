#!/usr/bin/env python

import iptc
import subprocess

def sysctl(param, value):
    cmd = [
        'sysctl',
        '-w',
        '%s=%s' % (param, value),
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise RuntimeError(err)

def sane_nat(lan, internet):

    postrouting = iptc.Chain(iptc.Table(iptc.Table.NAT), "POSTROUTING")
    forward = iptc.Chain(iptc.Table(iptc.Table.FILTER), "FORWARD")

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

    # /sbin/iptables -A FORWARD -i lan -o internet -j ACCEPT
    rule = iptc.Rule()
    rule.out_interface = internet
    rule.in_interface = lan
    rule.target = iptc.Target(rule, "ACCEPT")
    forward.append_rule(rule)


if __name__ == '__main__':

    sysctl('net.ipv4.ip_forward', 1)
    sane_nat(lan='enp63s0', internet='ens2')
