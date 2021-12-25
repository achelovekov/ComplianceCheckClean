import React from "react";
import ReactDiffViewer from "react-diff-viewer";
import Prism from "prismjs";


export default function DiffItem(props) {
  return (
    <div className="App">
      <ReactDiffViewer
        oldValue={props.oldCode}
        newValue={props.newCode}
        splitView={false}
        compareMethod="diffWords"
      />
    </div>
  );
}