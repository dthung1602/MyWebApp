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
