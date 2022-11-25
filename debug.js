
const mergeSort = (arr) => {
    if (arr.length < 2)
        return arr

    const mid = Math.floor(arr.length / 2)
    const left = arr.slice(0, mid);
    const right = arr.slice(mid);
    return merge(mergeSort(left), mergeSort(right))
}

function merge(left, right) {
    const sortedArr = [];
    while (left.length && right.length) {       //upto not empty
        if (left[0] <= right[0]) {
            sortedArr.push(left.shift())        //use shift() as to delete from previous position
        } else {
            sortedArr.push(right.shift())
        }
    }
    return [...sortedArr, ...left, ...right]    //merge leftover subarray elements
}

console.log(mergeSort([-6, 20, 8, -2, 4]));