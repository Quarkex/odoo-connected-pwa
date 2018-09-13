'use strict';

const e = React.createElement;

function build_list(myJson){
    const domContainer = document.querySelector('#react_component');

    var headers = [];
    var items = [];
    for (var i = 0; i < myJson.length; i++){
        var d = myJson[i];

        if (i == 0){
            for (var k in d) {
                if (d.hasOwnProperty(k)) {
                    headers.push(e( 'th', { 'key': k }, k ));
                }
            }
            headers = [ e( 'tr', { 'key': 0 }, headers ) ];
        }

        var td = [];

        for (var k in d) {
            if (d.hasOwnProperty(k)) {
                td.push(e( 'td', { 'key': k }, d[k] ));
            }
        }
        var tr = e( 'tr', { 'key': i }, td );

        items.push(tr);
    }
    var thead = e( 'thead', null, headers );
    var tbody = e( 'tbody', null, items );
    var table = e( 'table', null, thead, tbody );

    ReactDOM.render(table, domContainer);
}

