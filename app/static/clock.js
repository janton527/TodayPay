function updateClock(){
    const now = new Date();

    const time = now.toLocaleTimeString();

    document.getElementById("clock").textContent = time;
}

updateClock();
setInterval(updateClock, 1000);
