function gradingStudents(grades) {
    let num = []
    for (let g = 0; g < grades.length; g++) {
        let nextNum = Math.ceil(grades[g] / 5) * 5
        if ((grades[g] >= 38) && ((nextNum - grades[g]) < 3)) {
            num[num.length] = nextNum //or num = [...num, nextNum]  or num.splice(num, 0 , nextNum)
        } else {
            num[num.length] = grades[g]
        }
    }
    return num

}

console.log(gradingStudents([73, 67, 38, 33]))