function getByName(name) {
    return document.getElementsByName(name)[0];
}

function checkWheels() {
    var i, j;
    var wheels = [];
    for (i = 1; i < 5; i++)
        wheels.push(getByName("w" + i).value)
    for (i = 0; i < 4; i++)
        for (j = i + 1; j < 5; j++)
            if (wheels[i] === wheels[j]) {
                alert("Wheels must have different values!");
                return
            }
}

function checkPlugBoard(plug) {
    plug.value = plug.value.toUpperCase();
    getByName(plug.value).value = plug.name;

    var p;
    for (var i = 0; i < 26; i++) {
        p = getByName((i + 10).toString(36).toUpperCase());
        if (p.value === "") {
            alert("Plug board cannot be empty!");
            return;
        }
        if (getByName(p.value).value !== p.name) {
            alert("Invalid plug board setting!\nCharacters should be swapped pairwise.");
            return;
        }
    }
}

