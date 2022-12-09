


function angryProfessor(k, a) {
    return a.filter((elem) => elem <= 0).length >= k ? "Yes" : "No"
}
console.log(angryProfessor(2, [0, -1, 2, 1])) 