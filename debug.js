

function migratoryBirds(arr) {
    arr = arr.sort((a, b) => a - b);
    let result = [0, 0];
    for (let i = 0; i < arr.length; i++) {
        let count = 1
        for (let j = i + 1; j < arr.length; j++) {
            if (arr[i] == arr[j]) {
                count += 1
            }
        }

        if (count > result[0]) {
            result[0] = count;
            result[1] = arr[i]
        }

    }
    return result[1]

}

console.log(migratoryBirds([1, 2, 3, 4, 5, 4, 3, 2, 1, 3, 4]))

// [1, 4 ,4 ,4 ,5 ,3]