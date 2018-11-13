$(document).foundation()

var session_token = null;

function login(username, password){
    var headers = new Headers();
    fetch('/api/login', { 'method': 'POST', 'headers': headers, 'body': JSON.stringify({ 'username': username, 'password': password }) })
        .then(function(response) {
            return response.json();
        })
        .then(function(myJson) {
            session_token = myJson['session_token'];
        });
}
login('dev','dev');

function refresh_data(string){
    var headers = new Headers();
    fetch('/api/read', { 'method': 'POST', 'headers': headers, 'body': JSON.stringify({ 'session_token': session_token, 'search_string': string }) })
        .then(function(response) {
            return response.json();
        })
        .then(function(myJson) {
            build_list(myJson['result']);
        });
}

function delete_entry(id){
    console.log(id);
    var headers = new Headers();
    fetch('/api/delete', { 'method': 'POST', 'headers': headers, 'body': JSON.stringify({ 'session_token': session_token, 'target_id': id }) })
        .then(function(response) {
            return response.json();
        })
        .then(function(myJson) {
            build_list(myJson);
        });
}
