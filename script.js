function playSong() {
    let song = document.getElementById("songInput").value;
    if (!song) return alert("Please enter a song name!");

    fetch('/play', {
        method: "POST",
        body: JSON.stringify({ song: song }),
        headers: { "Content-Type": "application/json" }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "playing") {
            document.getElementById("status").innerText = `🎵 Playing: ${song}`;
        } else {
            alert("Error: " + data.message);
        }
    });
}

function pauseSong() {
    fetch('/pause', { method: "POST" })
    .then(res => res.json())
    .then(data => {
        if (data.status === "paused") {
            document.getElementById("status").innerText = "⏸️ Paused";
        }
    });
}

function resumeSong() {
    fetch('/resume', { method: "POST" })
    .then(res => res.json())
    .then(data => {
        if (data.status === "resumed") {
            document.getElementById("status").innerText = "▶️ Resumed";
        }
    });
}

function stopSong() {
    fetch('/stop', { method: "POST" })
    .then(res => res.json())
    .then(data => {
        if (data.status === "stopped") {
            document.getElementById("status").innerText = "⏹️ Stopped";
        }
    });
}
