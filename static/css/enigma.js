function check_wheels() {
    var count = 0
    var i, j
    var wheels = []
    for (i = 1; i < 5; i++) {
        wheels.push(document.getElementsByName("w" + i)[0].value)
    }
    for (i = 0; i < 4; i++)
        for (j = i + 1; j < 5; j++)
            if (wheels[i] == wheels[j]) {
                alert("Wheels must have different values!")
                return
            }
}