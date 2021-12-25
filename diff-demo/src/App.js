import DiffItem from './components/DiffItem';
import TableItem from './components/TableItem';
import { Text, StyleSheet } from 'react-native';

function App() {

  const oldCode1 = `
  router bgp 64923
  address-family l2vpn evpn
  nexthop trigger-delay critical 1 non-critical 1
  advertise-pip
  vrf i30Z
  graceful-restart stalepath-time 1800
  bestpath as-path multipath-relax
  address-family ipv4 unicast
      redistribute direct route-map RM-REDIST-SUBNET-i30Z
      maximum-paths ibgp 4
      oldline to be deleted
  `;
  const newCode1 = `
  router bgp 64924
  address-family l2vpn evpn
  nexthop trigger-delay critical 1 non-critical 1
  advertise-pip
  newline added
  vrf i30Z
  graceful-restart stalepath-time 1800
  bestpath as-path multipath-relax
  address-family ipv4 unicast
      redistribute direct route-map RM-REDIST-UNLOCAL-i30Z
      maximum-paths ibgp 4
  `;

  const oldCode2 = `
  router bgp 55555
  address-family l2vpn evpn
  nexthop trigger-delay critical 1 non-critical 1
  advertise-pip
  vrf i30Z
  graceful-restart stalepath-time 1800
  bestpath as-path multipath-relax
  address-family ipv4 unicast
      redistribute direct route-map RM-REDIST-SUBNET-i30Z
      maximum-paths ibgp 4
      oldline to be deleted
  `;
  const newCode2 = `
  router bgp 66666
  address-family l2vpn evpn
  nexthop trigger-delay critical 1 non-critical 1
  advertise-pip
  newline added
  vrf i30Z
  graceful-restart stalepath-time 1800
  bestpath as-path multipath-relax
  address-family ipv4 unicast
      redistribute direct route-map RM-REDIST-UNLOCAL-i30Z
      maximum-paths ibgp 4
  `;

  return (
    <div>
      <table>
        <TableItem oldCode={oldCode1} newCode={newCode1}></TableItem>
        <TableItem oldCode={oldCode2} newCode={newCode2}></TableItem>
      </table>
    </div>
  );
}

export default App;

