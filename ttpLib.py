from typing import Dict
from pydantic import BaseModel
from ttp import ttp 
import logging
import xml

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')

class TTPLib():
    templates = {}

    templates['l2BD'] = """
<group name="l2BD*" containsall="name, accEncap">
vlan {{ id | DIGIT }}
  name {{ name }}
  vn-segment {{ accEncap }}
</group>
"""

    templates['sviIf'] = """
<group name="sviIf*">
interface {{ id | contains('Vlan') | resub(old = '^Vlan', new = '') }} 
  description {{ description | default("none") }}
  no shutdown {{ state | set("Up") }}
  shutdown {{ state | set("AdminDown") | default("unknown")}}
  mtu {{ mtu | default("default")}}  
  vrf member {{ vrf | default("default") }}  
  no ip redirects {{ ipv4Redirect | set("False") }}
  ip redirects {{ ipv4Redirect | set("True") }}
  ip address {{ ipv4Addr | is_ip | default("none") }} tag {{ tag | DIGIT | default("None") }} 
  ip forward {{ ipForward | set("True") | default("False") }}
  fabric forwarding mode anycast-gateway {{ agw | set("True") | default("False") }}
</group>
"""

    templates['rtctrlBDEvi'] = """
<group name="rtctrlBDEvi*">   
  vni {{ id | DIGIT }} l2
    rd {{ rd }}
    route-target import {{ rtImport }}
    route-target export {{ rtExport }}
</group>
"""

    templates['nvoNw_L3'] = """
interface nve1
<group name="nvoNw*">   
  member vni {{ id | DIGIT }} associate-vrf
  {{ mode | set("L3VNI") }} 
</group>
"""

    templates['nvoNw_L2'] = """
interface nve1
<group name="nvoNw*">   
  member vni {{ id | DIGIT }}
  {{ mode | set("L2VNI") }} 
    supress-arp {{ supressArp | set("True") | default("False") }}
    mcast-group {{ mcastGroup | is_ip | let("replicationMethod", "PIM") | default("none") }}
    ingress-replication protocol bgp {{ replicationMethod | set("IR") }}
</group>
"""

    templates['l3Inst'] = """
<group name="l3Inst*">
vrf context {{ id }}
  vni {{ vnid | DIGIT }}
  rd {{ rd }}   
  <group name="ipv4Afi**" >
  address-family ipv4 unicast {{ _start_ }}{{ _exact_ }}
    route-target import {{ rtImport }}
    route-target export {{ rtExport }}
    route-target import {{ rtImportEvpn }} evpn
    route-target export {{ rtExportEvpn }} evpn
    route-target both auto {{ rtImport | set("auto") }} {{ rtExport | set("auto") }}
    route-target both auto evpn {{ rtImportEvpn | set("auto") }} {{ rtExportEvpn | set("auto") }}
  </group>
</group>
"""

    templates['bgp'] = """
<group name="bgp">
router bgp {{ asn | DIGIT }}
  router-id {{ routerID }}
  <group name="bgpIpv4Unicast">
  address-family ipv4 unicast {{ enabled | set("True") }}
  </group>
  <group name="bgpL2vpnEvpn">
  address-family l2vpn evpn {{ enabled | set("True") }}
    nexthop trigger-delay critical {{ delayCritical | DIGIT | default("default")}} non-critical {{ delayNonCritical | DIGIT | default("default")}}
    advertise-pip {{ advertisePip | set("True") | default("False")}}
  </group>
  <group name="templates">
  template peer {{ id }}
    bfd {{ bfd | set("True") | default("False") }}
    <group name="templatesIpv4Unicast">
    address-family ipv4 unicast {{ enabled | set("True") }} {{ _exact_ }}
      route-map {{ rmapIn }} in
      route-map {{ rmapOut }} out
      maximum-prefix {{ maxPrefix | DIGIT }} {{ maxPrefixAction }}
     </group>
    <group name="templatesL2vpnEvpn">
    address-family l2vpn evpn {{ enabled | set("True") }} {{ _exact_ }}
      route-map {{ rmapIn }} in
      route-map {{ rmapOut }} out
      maximum-prefix {{ maxPrefixValue | DIGIT }} {{ maxPrefixAction }}
     </group>
  </group>
  <group name="neighbors">
  neighbor {{ id | is_ip }}
    inherit peer {{ template }}
  </group>
  <group name="vrfLite*">
  vrf {{ id }}
    router-id {{ routerId | default("none") }}
    graceful-restart stalepath-time {{ stalePathTime | DIGIT | default("default") }}
    bestpath as-path multipath-relax {{ multipathRelax | set("True") | default("False") }}
    <group name="vrfIpv4Unicast">
    address-family ipv4 unicast {{ enabled | set("True") }}
      redistribute direct route-map {{ redistributeDirectRMap }}
      redistribute static route-map {{ redistributeStaticRMap }}
      maximum-paths ibgp {{ ibgpMaxPath | DIGIT | default("default") }}
    </group>
    <group name="neighbors">
    neighbor {{ id | is_ip }}
      inherit peer {{ template }}
      <group name="neighborsIpv4Unicast">
      address-family ipv4 unicast {{ enabled | set("True") }}
        route-map {{ rmapIn }} in
        route-map {{ rmapOut }} out
      </group>
    </group>
  </group>
</group>
"""

    templates['routeMap'] = """
<group name="routeMap*">
route-map {{ id }} permit {{ seq }} 
  {{ deny | set("False") }}
  {{ permit | set("True") }}
  match ip address prefix-list {{ matchPrefixList}}
  match tag {{ matchTag }}
</group>

<group name="routeMap*">
route-map {{ id }} deny {{ seq }}
  {{ deny | set("True") }}
  {{ permit | set("False") }}
  match ip address prefix-list {{ prefixList}}
  match tag {{ tag }}
</group>
"""


    @classmethod
    def getCombinedTemplate(cls, chunkNames):
        template = ""
    
        for chunk in chunkNames:
            try:
                template += cls.templates[chunk]
            except KeyError:
                logging.error(f"chunk {chunk} does not exist in TTPLib. Please check definitions.")
                exit()

        return template
    
    @classmethod
    def parser(cls, data, chunkNames):
          template = cls.getCombinedTemplate(chunkNames)
          try:
              parser = ttp(data=data,template=template)
              parser.parse()
              return parser.result(format='raw')[0][0]
          except xml.etree.ElementTree.ParseError as e:
              logging.error(f"incorrect ttp-template\n{e}\nplease check combined template: {template}")
              exit()
      

