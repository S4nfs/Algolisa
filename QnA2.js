//===================================================================================================================
/* Q1. Parking Lot -  Implement the ParkingLot class that manages a parking lot with a number of slots or spaces. The class has the following constructor and methods:

    The constructor ParkingLot(slots) where parameter slots is the size of the parking lot. Slots are numbered consecutively from 1 to slots, [1, 2, 3, ..., slots].

    The method park(carId) - Parks the car with the given carId at the unoccupied slot with the lowest number and returns true.If all slots are occupied, the car is not parked and it returns false.

    The method getSlots() - Returns an array of all the parking slots where the ith element is the id of the car parked there, or null if the slot is unoccupied.

    The method remove(carId) - Frees the parking slot where the car is parked and returns true.It returns false if a car with the given carId is not found.

The locked stub code validates the correctness of the ParkingLot class implementation by performing the following operations:
    Park carId: If the return value of the call is true, it prints 'Parking Started: <carId>'.Otherwise, it prints 'Parking Full: <carId>'.
    Remove carId: If the return value is true, it prints 'Car id <carId> removed from parking'.Otherwise, it prints 'Car: <carId> not found'.
    GetSlots: For an occupied slot, it prints 'Parked at slot <slotNumber>: <carId>'.For an unoccupied slot, it prints 'Slot <slotNumber> is empty'.

*///=================================================================================================================


class ParkingLot {
    slots = [];
    constructor(parkingSize) {
        this.slots = new Array(parkingSize).fill(null)
    }

    park(carId) {
        console.log(`Parking car: ${carId}`)
        if (this.slots.every((slot) => slot !== null)) return false

        for (let i = 0; i < this.slots.length; i++) {
            if (this.slots[i] === null) {
                this.slots[i] = carId
                return true
            }
        }
    }

    remove(carId) {
        console.log(`Leaving car: ${carId}`);
        if (this.slots.every((slot) => slot !== carId)) {
            return false;
        }

        for (let i = 0; i < this.slots.length; i++) {
            if (this.slots[i] === null) {
                this.slots[i] = carId
                return true
            }
        }
    }

    getSlots() {
        console.log(`Parking slots: ${this.slots}`);
        return this.slots
    }
    getSize() {
        console.log(`Parking size is: ${this.slots.length}`);
        return this.slots.length;
    }

    getAvailable() {
        const availableSlots = this.slots.filter((s) => s === null).length;
        console.log(`Available parking slots: ${availableSlots}`);
        return availableSlots;
    }

    isFull() {
        return this.getAvailable() === 0;
    }
}
const parking = new ParkingLot(5);
console.log(parking.getSlots())
console.log(parking.park("Car-10"))
console.log(parking.getSize())
console.log(parking.getAvailable())

//===================================================================================================================
/* Q2. Who Is The Oldest ?
This function will receive an array of objects. Each object will represent a person
with a name and an age property. The function should return the name of the
person who is oldest.

If the array is empty, the function should return "no people found"
Note: all people will have different ages.

Examples:
findOldestPerson ([
{ name: 'Liam', age: 28 },
{ name:
'Eli', age: 37 },
{ name:
'Poonam', age: 22 },
{ name:
'Cameron', age: 32 }
]);
Should return 'Eli'
findOldestPerson ([]);
Should return 'no people found'
*///=================================================================================================================

function findOldest(persons) {
    let a = 0; let result = ''
    if (persons.length == 0) console.log("EMPTY")
    else {
        persons.forEach((person) => {
            if (person.age > a) {
                result = person.name
                a = person.age
            }
        })
        console.log("MAXIMUM AGED", result)
    }
    // let oldest = persons.reduce(function (prev, current) {
    //     return (prev.age > current.age) ? prev : current
    // })
    // return oldest.name
}


console.log(findOldest([{ name: "liam", age: 22 },
{ name: "sagar", age: 24 },
{ name: "vishal", age: 20 },
{ name: "arnish", age: 29 },
{ name: "brian", age: 18 }]))




/*===================================================================================================================
 __  __      _       _
|  \/  |__ _| |_ _ _(_)__ ___ ___
| |\/| / _` |  _| '_| / _/ -_|_-<
|_|  |_\__,_|\__|_| |_\__\___/__/

/* Q3. Write a method that returns the frequency of the max integer in the matrix after increament by 1 within matrix operations? In the below example, it would be 1(since 2 shows up just once).

Input:
m=4
n=4
operations = [[1,1],[2,2]]

Output= 1

Explaination:
[[1, 0, 0, 0],
 [0, 0, 0, 0],
 [0, 0, 0, 0]]

[[2, 1, 0, 0],
 [1, 1, 0, 0],
 [0, 0, 0, 0]]  //max is 2 which occurs 1 times after overlapping
*///=================================================================================================================
function maxFromOps(m, n, operations) {
    var minCol = m;
    var minRow = n;

    for (let op of operations) {
        minCol = Math.min(minCol, op[0]);
        minRow = Math.min(minRow, op[1]);
    }
    return minCol * minRow;
}

console.log(maxFromOps(4, 4, [
    [1, 1],
    [2, 2],
]));


//===================================================================================================================
/* Q4. Given an integer array coins[ ] of size N representing different denominations of currency and an integer sum, find the number of ways you can make sum by using different combinations from coins[ ].  
Note: Assume that you have an infinite supply of each type of coin. 

Input:
sum = 4 , 
N = 3
coins[] = {1,2,3}

Output: 4
Explanation: Four Possible ways are:
{1,1,1,1},{1,1,2},{2,2},{1,3}.
*///=================================================================================================================


//===================================================================================================================
/* Q5. In a town, there are N people labelled from 1 to N.  There is a rumor that one of these people is secretly the town judge.If the town judge exists, then:1. The town judge trusts nobody.
2. Everybody (except for the town judge) trusts the town judge.
3. There is exactly one person that satisfies properties 1 and 2.You are given trust, an array of pairs trust[i] = [a, b] representing that the person labelled a trusts the person labelled b.If the town judge exists and can be identified, return the label of the town judge.  Otherwise, return -1.


Example 1:

Input: N = 2, trust = [[1,2]]
Output: 2

Example 2:

Input: N = 3, trust = [[1,3],[2,3]]
Output: 3

Example 3:

Input: N = 3, trust = [[1,3],[2,3],[3,1]]
Output: -1

Example 4:

Input: N = 3, trust = [[1,2],[2,3]]
Output: -1

Example 5:

Input: N = 4, trust = [[1,3],[1,4],[2,3],[2,4],[4,3]]
Output: 3
*///=============================================================================================================================


function findTownJudge(N, trust) {
    // Create an array of counters to keep track of how many people trust each person
    const trustCounts = new Array(N + 1).fill(0);

    // Iterate over the trust pairs and update the counters
    for (const [a, b] of trust) {
        // console.log([a]) //[ 1 ][ 1 ][ 2 ][ 2 ][ 4 ]
        console.log([a, b])
        trustCounts[a]--;
        trustCounts[b]++;
    }
    // Find the person with N-1 trusts (everyone trusts except the judge)
    for (let i = 1; i <= N; i++) {
        if (trustCounts[i] === N - 1) {
            return i;
        }
    }
    // No town judge found
    return -1;
}
console.log(findTownJudge(4, [[1, 3], [1, 4], [2, 3], [2, 4], [4, 3]]))