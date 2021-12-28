import DiffItem from './DiffItem';
import { Text, StyleSheet } from 'react-native';
import JSONPretty from 'react-json-pretty';
import 'react-json-pretty/themes/monikai.css';

function TableItem(props) {
    var JSONPrettyMon = require('react-json-pretty/dist/monikai');
    return (
        <tr>
            <td>
            <Text style={styles.baseText}>{props.keyID}</Text>
            </td>
            <td>
            <Text style={styles.baseText}>{props.deviceName}</Text>
            </td>
            <td>
            <JSONPretty id="json-pretty" data={props.footprint}></JSONPretty>
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

