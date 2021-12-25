import DiffItem from './DiffItem';
import { Text, StyleSheet } from 'react-native';

function TableItem(props) {

    return (
        <tr>
            <td>
            <Text style={styles.baseText}>vnid: vrf:</Text>
            </td>
            <td>
            <Text style={styles.baseText}>DeviceList:</Text>
            </td>
            <td>
            <Text style={styles.baseText}>{props.oldCode}</Text>
            </td>
            <td>
            <Text style={styles.baseText}>{props.newCode}</Text>
            </td>
            <td>
            <DiffItem oldCode={props.oldCode} newCode={props.newCode}></DiffItem>
            </td>
        </tr>
    );
}

const styles = StyleSheet.create({
  baseText: {
    fontFamily: 'Courier New'
  },
  titleText: {
    fontSize: 20,
    fontWeight: "bold"
  }
});

export default TableItem;

