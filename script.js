document.getElementById('top-tracks').onclick = function() {
    document.getElementById('results').innerHTML = '<h2>Analyzing All Songs...</h2>';
};

document.getElementById('playlist').onclick = function() {
    document.getElementById('results').innerHTML = '<h2>Analyzing by Playlist...</h2>';
};
