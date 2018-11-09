$(document).foundation()

function refresh_data(string){
    var headers = new Headers();
    fetch('/api/read', { 'method': 'POST', 'headers': headers, 'body': JSON.stringify({ 'search_string': string }) })
        .then(function(response) {
            return response.json();
        })
        .then(function(myJson) {
            build_list(myJson);
        });
}

function delete_entry(id){
    console.log(id);
    var headers = new Headers();
    fetch('/api/delete', { 'method': 'POST', 'headers': headers, 'body': JSON.stringify({ 'target_id': id }) })
        .then(function(response) {
            return response.json();
        })
        .then(function(myJson) {
            build_list(myJson);
        });
}
