import DiffItem from './components/DiffItem';
import TableItem from './components/TableItem';
import { Text, StyleSheet } from 'react-native';

function App() {

  const result = [{
    "key": "eAZ",
    "footprint": "{\"l3Inst\": {\"id\": \"eAZ\", \"vnid\": \"2010000\", \"ipv4Afi\": {\"rtExport\": \"62000:2010000\", \"rtImport\": \"62000:2010000\", \"rtExportEvpn\": \"62000:2010000\", \"rtImportEvpn\": \"62000:2010000\"}}, \"nvoNw\": {\"id\": \"2010000\", \"mode\": \"L3VNI\"}, \"l2BD\": {\"accEncap\": \"2010000\", \"id\": \"3901\", \"name\": \"VRF_eAZ\"}, \"sviIf\": {\"agw\": \"False\", \"ipForward\": \"True\", \"vrf\": \"eAZ\", \"id\": \"3901\", \"tag\": \"None\", \"description\": \"L3_VNI_FOR_eAZ_2010000\"}, \"bgp\": {\"vrfLite\": {\"id\": \"eAZ\", \"multipathRelax\": \"True\", \"stalePathTime\": \"1800\", \"vrfIpv4Unicast\": {\"enabled\": \"True\", \"ibgpMaxPath\": \"4\", \"redistributeDirectRMap\": \"RM-REDIST-SUBNET-eAZ\"}}}}",
    "original": "vlan 3901\n  name VRF_eAZ\n  vn-segment 2010000\nvrf context eAZ\n  vni 2010000\n  rd auto\n  address-family ipv4 unicast\n    route-target import 62000:2010000\n    route-target import 62000:2010000 evpn\n    route-target export 62000:2010000\n    route-target export 62000:2010000 evpn\nrouter bgp 65514\n  router-id 172.17.117.111\n  graceful-restart stalepath-time 1800\n  bestpath as-path multipath-relax\n  address-family ipv4 unicast\n    redistribute direct route-map RM-REDIST-SUBNET-eAZ\n    maximum-paths ibgp 4",
    "templated": "\nvlan 3901\n  name VRF_eAZ\n  vn-segment 2010000\nvrf context eAZ\n  vni 2010000\n  rd auto\n  address-family ipv4 unicast\n    route-target import 65514:2010000\n    route-target import 65514:2010000 evpn\n    route-target export 65514:2010000\n    route-target export 65514:2010000 evpn\nrouter bgp 65514\n  graceful-restart stalepath-time 1800\n  address-family ipv4 unicast\n    redistribute direct route-map RM-REDIST-SUBNET-eAZ\n    maximum-paths ibgp 4",
    "deviceName": "SKO-DATA-AC-014-J22-01-EXT"
  },
  {
    "key": "eAZ",
    "footprint": "{}",
    "original": "",
    "templated": "\nvlan 3901\n  name VRF_eAZ\n  vn-segment 2010000\nvrf context eAZ\n  vni 2010000\n  rd auto\n  address-family ipv4 unicast\n    route-target import 65514:2010000\n    route-target import 65514:2010000 evpn\n    route-target export 65514:2010000\n    route-target export 65514:2010000 evpn\nrouter bgp 65514\n  graceful-restart stalepath-time 1800\n  address-family ipv4 unicast\n    redistribute direct route-map RM-REDIST-SUBNET-eAZ\n    maximum-paths ibgp 4",
    "deviceName": "SKO-DATA-AC-014-Q27-01-EXT"
  },
  {
    "key": "eAZ",
    "footprint": "{}",
    "original": "",
    "templated": "\nvlan 3901\n  name VRF_eAZ\n  vn-segment 2010000\nvrf context eAZ\n  vni 2010000\n  rd auto\n  address-family ipv4 unicast\n    route-target import 65514:2010000\n    route-target import 65514:2010000 evpn\n    route-target export 65514:2010000\n    route-target export 65514:2010000 evpn\nrouter bgp 65514\n  graceful-restart stalepath-time 1800\n  address-family ipv4 unicast\n    redistribute direct route-map RM-REDIST-SUBNET-eAZ\n    maximum-paths ibgp 4",
    "deviceName": "SKO-DATA-AC-014-O13-01-EXT"
  },
  {
    "key": "eAZ",
    "footprint": "{\"l3Inst\": {\"id\": \"eAZ\", \"vnid\": \"2010000\", \"ipv4Afi\": {\"rtExport\": \"62000:2010000\", \"rtImport\": \"62000:2010000\", \"rtExportEvpn\": \"62000:2010000\", \"rtImportEvpn\": \"62000:2010000\"}}, \"nvoNw\": {\"id\": \"2010000\", \"mode\": \"L3VNI\"}, \"l2BD\": {\"accEncap\": \"2010000\", \"id\": \"3901\", \"name\": \"eAZ\"}, \"sviIf\": {\"agw\": \"False\", \"ipForward\": \"True\", \"vrf\": \"eAZ\", \"id\": \"3901\", \"tag\": \"None\", \"description\": \"VRF_eAZ\"}, \"bgp\": {\"vrfLite\": {\"id\": \"eAZ\", \"multipathRelax\": \"True\", \"stalePathTime\": \"1800\", \"vrfIpv4Unicast\": {\"enabled\": \"True\", \"ibgpMaxPath\": \"16\", \"redistributeDirectRMap\": \"RM-REDIST-DIRECT-eAZ\"}}}}",
    "original": "vlan 3901\n  name eAZ\n  vn-segment 2010000\nvrf context eAZ\n  vni 2010000\n  rd auto\n  address-family ipv4 unicast\n    route-target import 62000:2010000\n    route-target import 62000:2010000 evpn\n    route-target export 62000:2010000\n    route-target export 62000:2010000 evpn\nrouter bgp 65514\n  graceful-restart stalepath-time 1800\n  bestpath as-path multipath-relax\n  address-family ipv4 unicast\n    redistribute direct route-map RM-REDIST-DIRECT-eAZ\n    maximum-paths 16\n    maximum-paths ibgp 16",
    "templated": "\nvlan 3901\n  name VRF_eAZ\n  vn-segment 2010000\nvrf context eAZ\n  vni 2010000\n  rd auto\n  address-family ipv4 unicast\n    route-target import 65514:2010000\n    route-target import 65514:2010000 evpn\n    route-target export 65514:2010000\n    route-target export 65514:2010000 evpn\nrouter bgp 65514\n  graceful-restart stalepath-time 1800\n  address-family ipv4 unicast\n    redistribute direct route-map RM-REDIST-SUBNET-eAZ\n    maximum-paths ibgp 4",
    "deviceName": "SKO-DATA-AG-014-G04-01-EXT"
  }]
  const tableItems = []

  result.forEach((item) => {
    if (item.footprint !== "{}") {
      tableItems.push(<TableItem keyID={item.keyID} footprint={item.footprint} deviceName={item.deviceName} oldCode={item.original} newCode={item.templated}></TableItem>)
    }
  })

  return (
    <div>
      <table>
        {tableItems}
      </table>
    </div>
  );
}

export default App;

