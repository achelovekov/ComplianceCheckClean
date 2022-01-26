import ttp

data = """
interface Ethernet1/16
  description gigamon ACOD-MR-TA25-1 55/1/x41 ERSPAN [L3]
  no cdp enable
  mtu 9216
  speed 25000
  no ip redirects
  ip address 10.4.11.166/31
  no ipv6 redirects
  no ip ospf passive-interface
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface Ethernet1/59
  description ACOD-PROD-SPINE-4_Eth3/2 [2][L3]
  mtu 9216
  no ip redirects
  ip address 10.4.9.65/31
  no ipv6 redirects
  ip ospf authentication message-digest
  ip ospf message-digest-key 1 md5 3 xxxxxxxx
  ip ospf network point-to-point
  ip ospf passive-interface
  ip router ospf UNDERLAY area 0.0.0.1
  ip ospf bfd
  ip pim bfd-instance
  ip pim sparse-mode
  no shutdown
"""

template = """
<vars>
# template variable with custom regular expression:
physIf = "Ethernet\d+\/\d+|mgmt0|port-channel\d+"
loIf = "loopback\d+"
</vars>

<group name="interfaces">
<group name="l3PhysIf*" containsall="ipAddress">
interface {{ id | re("physIf") | _start_ }} 
  <group name="general">
  ip address {{ ipAddress }}
  mtu {{ mtu | default("default") }}
  no ip redirects {{ ipv4Redirects | set("False") }}
  ip redirects {{ ipv4Redirects | set("True") }}
  no ipv6 redirects {{ ipv6Redirects | set("False") }}
  ipv6 redirects {{ ipv6Redirects | set("True") }}
  </group>
</group>
</group>
"""

parser = ttp.ttp(data=data, template=template)
parser.parse()

results = parser.result(format='json')[0]
print(results)
