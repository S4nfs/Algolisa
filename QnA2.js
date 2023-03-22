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