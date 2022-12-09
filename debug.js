// class Node {
//     constructor(value) {
//         this.value = value
//         this.next = null
//     }
// }

// class LinkedList {
//     constructor() {
//         this.head = null
//         this.size = 0
//     }

//     isEmpty() {
//         return this.size === 0
//     }

//     getSize() {
//         return this.size
//     }
//     //O(1)
//     prepend(value) {
//         const node = new Node(value)
//         if (this.isEmpty()) {
//             this.head = node
//         } else {
//             node.next = this.head       //shifting head to next and new value to head
//             this.head = node
//         }
//         this.size++
//     }

//     print() {
//         if (this.isEmpty()) {
//             console.log('List is Empty')
//         } else {
//             let curr = this.head
//             let list = ''
//             while (curr) {
//                 list += `${curr.value} `
//                 curr = curr.next
//             }
//             console.log(list)
//         }
//     }
//     O(n)
//     append(value) {
//         const node = new Node(value)
//         if (this.isEmpty()) {
//             this.head = node
//         } else {
//             let prev = this.head
//             while (prev.next) {
//                 prev = prev.next
//             }
//             prev.next = node
//         }
//         this.size++
//     }
// }

// let linkedlist = new LinkedList()
// console.log(linkedlist.isEmpty())
// linkedlist.prepend(10)
// linkedlist.prepend(20)
// linkedlist.prepend(30)
// linkedlist.print()


function num(num = num + 1) {
    return num;
}
console.log(num(5))