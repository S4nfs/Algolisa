function migratoryBirds(arr) {
    arr = arr.sort((a, b) => a - b);
    const l = arr.length;
    let result = [0, 0]; // [0] => type, [1] => count birds
    for (let i = 0; i < l; i++) {
        let count = 1;
        for (let j = i + 1; j < l; j++) {
            if (arr[i] === arr[j]) {
                count += 1;
            }
        }
        if (count > result[1]) {
            result[1] = count;
            result[0] = arr[i];
        }
    }
    return result[0];
}

console.log(migratoryBirds([1, 2, 3, 4, 5, 4, 3, 2, 1, 3, 4]))
