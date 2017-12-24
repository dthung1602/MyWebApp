function getByName(name) {
    return document.getElementsByName(name)[0];
}

function checkWheels() {
    var i, j;
    var wheels = [];
    for (i = 1; i < 5; i++) {
        wheels.push(getByName("w" + i));
        wheels[wheels.length - 1].style.color = "black";
    }
    for (i = 0; i < 3; i++)
        for (j = i + 1; j < 4; j++)
            if (wheels[i].value === wheels[j].value) {
                wheels[i].style.color = "red";
                wheels[j].style.color = "red";
            }
}

function saveOldValue(plug) {
    plug.oldValue = plug.value
}

function updateValue(plug) {
    if (plug.value === "") {
        if (plug.oldValue !== "")
            getByName(plug.oldValue).value = ""
    } else {
        plug.value = plug.value.toUpperCase();
        if (!/^[A-Z]$/.test(plug.value)) {
            plug.value = ""
        } else {
            var otherPlug = getByName(plug.value);
            if (otherPlug.value === "")
                otherPlug.value = plug.name;
            else if (otherPlug.value !== plug.name) {
                alert("Letter '" + plug.value + "' is used more than once!");
                plug.value = plug.oldValue
            }
        }
        if (plug.value === plug.name)
            plug.value = ""
    }
}


function getRandomItems(list, num) {
    var newList = [];
    while (newList.length < num) {
        var item = list[Math.floor(Math.random() * list.length)];
        if (newList.indexOf(item) < 0)
            newList.push(item)
    }
    return newList;
}

function randomizeSetting() {
    var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

    // reflection wheel
    getByName("rw").value = getRandomItems(["B", "C"], 1);

    // rotator wheels
    var wheels = getRandomItems(["I", "II", "III", "IV", "V", "VI", "VII", "VIII"], 4);
    for (var i = 0; i < 4; i++)
        getByName("w" + (i + 1)).value = wheels[i];

    // init position
    var letters = getRandomItems(alphabet, 4);
    for (i = 0; i < 4; i++)
        getByName("p" + (i + 1)).value = letters[i];

    // plug board
    for (i = 0; i < 26; i++)
        getByName(alphabet[i]).value = "";
    var n = Math.floor(Math.random() * 14);
    letters = getRandomItems(alphabet, n * 2);
    for (i = 0; i < n; i++) {
        var u = letters[2 * i];
        var v = letters[2 * i + 1];
        getByName(u).value = v;
        getByName(v).value = u;
    }
}