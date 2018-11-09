$(document).foundation()

function refresh_data(string){
    var headers = new Headers();
    fetch('/api', { 'method': 'POST', 'headers': headers, 'body': JSON.stringify({ 'search_string': string }) })
        .then(function(response) {
            return response.json();
        })
        .then(function(myJson) {
            build_list(myJson);
        });
}
