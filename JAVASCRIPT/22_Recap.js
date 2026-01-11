// 🦗 Hoisting in Javascript is a mechanism where variables and functions declarations are moved to the top of their scope before the code executes. (see image b)
//Variable Hoisting
console.log(myName) // OUTPUT-> undefined
var myName
myName = 'Sagar Verma'

//Function Hoisting
hello() // OUTPUT-> Hello World

function hello() {
  console.log('Hello World')
}

konnichiwa() // OUTPUT-> TypeError: konnichiwa is not a function
const konnichiwa = () => {
  console.log('こんにちは')
}

// 🦗 Scope Chain - (see image c)
var a = 'Hello'

function one() {
  var b = 'How are You?'
  console.log(b)
  two()
  function two() {
    var c = 'What are you doing?'
    console.log(a + b + c) //can access parent function + global context
    three()
  }
}
function three() {
  var d = 'Please answer, Bro?'
  console.log(d) //can only access its execution stack + global context (a,d)
}
one()

// 🦗 Stict Mode - (see image d)
;('use strict')
function sum(a, b) {
  add = a + b //add is not defined
  console.log(add)
}
sum(10, 20)

// 🦗 This Keyword - (see image e)
function sum1() {
  add = 2 + 2
  console.log('Sum of two no. is ' + add)
  console.log(this) //return global object which is window
}
sum1()

const bioData = {
  name: 'John',
  age: 30,
  sum: function () {
    add = 2 + 2
    console.log('Sum of two no. is ' + add)
    console.log(this) //return bioData object

    function anotherFunc() {
      var name = 'Sagar'
      console.log('Your name is ' + name)
      console.log(this) //return globar object as it act as a regular func
    }
    anotherFunc()
  },
}
bioData.sum()

/* 🦗 Difference b/w Pass by value || pass by reference (see image f)
JavaScript objects and arrays are reference types. When you assign an object or array to a variable, you're assigning a reference to its memory location, not the actual data.

Primitive types (e.g., string, number, boolean) are stored by value.
Non-primitive types (e.g., object, array, function) are stored by reference.
*/
let a1 = 10
let b1 = a1
b1 += 5
console.log(a1) //10
console.log(b1) //15

let arr1 = [1, 2.3, 4]
let arr2 = arr1
arr2.push(5)
console.log(arr1) //same
console.log(arr2) //same becoz reference data types share same memory

/* 🦗 Shallow copy and deep copy
 - A shallow copy duplicates the top-level properties but references any nested objects or arrays. (FAST)
 - A deep copy creates a new object or array with completely independent copies of the original structure, including all nested levels. (SLOW)
*/

// Shallow Copy with Arrays
const arr = [1, 2, [3, 4]]

const shallowCopy = arr.slice() // or [...arr]

shallowCopy[0] = 100
console.log(arr) // [1, 2, [3, 4]] -> top-level unaffected

shallowCopy[2][0] = 999
console.log(arr) // [1, 2, [999, 4]] -> nested array modified

// Shallow Copy with Objects
const obj = { a: 1, b: { c: 2 } }

const shallowCopyWithObjects = { ...obj }

shallowCopyWithObjects.a = 100
console.log(obj) // { a: 1, b: { c: 2 } } -> top-level unaffected

shallowCopyWithObjects.b.c = 999
console.log(obj) // { a: 1, b: { c: 999 } } -> nested object modified

// Deep Copy with Arrays
const arr3 = [1, 2, [3, 4]]

const deepCopyArrays = structuredClone(arr3)
deepCopyArrays[2][0] = 999

console.log(arr3) // [1, 2, [3, 4]] -> original remains intact
console.log(deepCopyArrays) // [1, 2, [999, 4]]

// Deep Copy with Objects
const obj2 = { a: 1, b: { c: 2 } }

const deepCopyObjects = JSON.parse(JSON.stringify(obj2))
deepCopyObjects.b.c = 999

console.log(obj2) // { a: 1, b: { c: 2 } } -> original intact
console.log(deepCopyObjects) // { a: 1, b: { c: 999 } }

/* Evolution of JAVASCRIPT from ES6 to ES 24
+--------------------------+------------------------------------------+
|                         ESM 6                                       |
+--------------------------+------------------------------------------+
| Feature                  | Description                              |
+--------------------------+------------------------------------------+
| let, const               | Block-scoped variable declarations       |
| Arrow Functions          | Short syntax for functions               |
| Template Literals        | String interpolation                     |
| Default Parameters       | Function parameters with defaults        |
| Destructuring            | Array and object unpacking               |
| Spread/Rest              | ... operator for arrays/objects          |
| Enhanced Objects         | Shorthand properties and methods         |
| Classes                  | Object-oriented programming syntax       |
| Modules (import/export)  | Modular code structure                   |
| Promises                 | Asynchronous operation handling          |
| Symbol                   | Unique identifiers                       |
| Map, Set                 | New data structures for collections      |
| Generators               | Function that yields multiple results    |
| for...of Loop            | Iterating over iterable objects          |
| WeakMap, WeakSet         | Weakly referenced collections            |
+--------------------------+------------------------------------------+

*/
// #1 - Let and const example
let user = 'Mysterio'
const userId = 1908894

if (true) {
  let user = 'Batman'
  console.log(user) // Batman (block-scoped)
}

console.log(user) // Mysterio

// #2 - Arrow functions
const fullname = (firstname, lastname) => firstname + ' ' + lastname
console.log(fullname('Clark', 'Kent')) // Clark Kent

// #3 - Template Literals
const fullnameWithTemplate = (firstname, lastname) => `${firstname} ${lastname}`
console.log(fullnameWithTemplate('Clark', 'Kent')) // Clark Kent

// #4 - Default parameter
const fullnameWithDefaultParams = (firstname = 'Bruce', lastname = 'Wayne') => `${firstname} ${lastname}`
console.log(fullnameWithDefaultParams()) // Bruce Wayne

// #5 - Destructuring
// Array Destructuring
const [uid, uname] = [1, 'Batman']
console.log(uid, uname) // 1 Batman

// - Object Destructuring
const response = { id: 1, username: 'Batman', email: 'bruce@gmail.com' }
const { id, username, email } = response
console.log(id, username, email) // 1 Alice a@b.com

// #6 - Spread and Rest Operators (...)
// Spread
const numbers = [1, 2, 3, 4, 5]
const [first, ...rest] = numbers
console.log(first, rest) // 1 [2, 3, 4, 5]

// Rest
const floatingNumber = [1.1, 2.2, 3.3, 4.4, 5.5]
const floatingAndDecimal = [...floatingNumber, ...numbers]
console.log(floatingAndDecimal) // [1.1, 2.2, 3.3, 4.4, 5.5, 1, 2, 3, 4, 5]

// #7 - Shorthand object literals
const newUser = {
  id,
  username,
  email,
}
console.log(newUser) // { id: 1, username: 'Batman', email: 'bruce@gmail.com' }

// #8 - Classes - Syntactic sugar for prototypes
class SuperHero {
  constructor(heroname) {
    this.heroname = heroname
  }

  speak() {
    console.log(`${this.heroname} have won the battle.`)
  }
}

class Human extends SuperHero {
  isHuman() {
    console.log(`${this.heroname} is a also a human.`)
  }
}

const humanSuperhero = new Human('Batman')
humanSuperhero.isHuman() // Batman is a also a human

// #9 - Import and export modules
// superhero.js
export const superhero = (heroname) => `I am, ${heroname}`

// index.js
import { superhero } from './superhero.js'
console.log(greet('Batman')) // I am Batman

// #10 - Promises
const fetchData = () =>
  new Promise((resolve) => {
    setTimeout(() => resolve('This promise will resolve definitely after 1 second'), 1000)
  })

fetchData()
  .then(console.log) // This promise will resolve definitely after 1 second
  .catch(console.error) // Won't run as the promise is resolved not rejected

// #11 - Symbols
const doomsday1 = Symbol('doomsday')
const doomsday2 = Symbol('doomsday')

console.log(doomsday1 === doomsday2) // false (unique symbols)

// #12 - Map ans Set
// Map
const superHeroMap = new Map()
superHeroMap.set('name', 'Barry Allen')
superHeroMap.set('age', 30)

console.log(superHeroMap.get('name')) // Barry Allen
console.log(superHeroMap.get('age')) // 30

// Set
const superHeroSet = new Set(['Batman', 'Superman', 'Wonder Woman', 'Flash'])
console.log(superHeroSet) // Set(4) { 'Batman', 'Superman', 'Wonder Woman', 'Flash' }

superHeroSet.add('Aquaman')
console.log(superHeroSet) // Set(5) { 'Batman', 'Superman', 'Wonder Woman', 'Flash', 'Aquaman' }

superHeroSet.delete('Superman')
console.log(superHeroSet) // Set(4) { 'Batman', 'Wonder Woman', 'Flash', 'Aquaman' }

console.log(superHeroSet.has('Batman')) // true

// #13 - Iterators and generators
const superHeroIterators = ['Batman', 'Superman', 'Wonder Woman', 'Flash']
const iterator = superHeroIterators[Symbol.iterator]()

console.log(iterator.next()) // { value: 'Batman', done: false }
console.log(iterator.next()) // { value: 'Superman', done: false }
console.log(iterator.next()) // { value: 'Wonder Woman', done: false }
console.log(iterator.next()) // { value: 'Flash', done: false }

function* generateSuperHeroes() {
  yield 'Batman'
  yield 'Superman'
  yield 'Wonder Woman'
}

const generator = generateSuperHeroes()
console.log(generator.next().value) // Batman

// # 14 for...of loop
for (const hero of superHeroIterators) {
  console.log(hero)
} // Batman Superman Wonder Woman Flash

/*
+---------------------------+------------------------------------------------+
|                             ESM 7                                          |
+---------------------------+------------------------------------------------+
| Feature                   | Description                                    |
+-------------------------- +------------------------------------------------+
| Array.prototype.includes  | Check if an array contains a specific value    |
| Exponentiation Operator **| Short syntax for power operations              |
+---------------------------+------------------------------------------------+

*/
// #1 - Array.prototype.includes()
const superheroes = ['Batman', 'Superman', 'Flash']

if (superheroes.includes('Batman')) {
  console.log('Batman is bruce wayne!')
} // will print - Batman is bruce wayne!

// #2 Exponentiation operator
const usingPowerMethod = Math.pow(17, 3)
const usingExponentiationOperator = 17 ** 3

console.log(usingPowerMethod) // 4913
console.log(usingExponentiationOperator) // 4913

/*
+-------------------------------------+---------------------------------------------------------+
|                                    ESM 8                                                      |
+-------------------------------------+---------------------------------------------------------+
| Feature                             | Description                                             |
+-------------------------------------+---------------------------------------------------------+
| async/await                         | Simplified asynchronous programming syntax              |
| Object.values()                     | Returns values of an object as an array                 |
| Object.entries()                    | Returns key-value pairs of an object as an array        |
| Object.getOwnPropertyDescriptors()  | Retrieves all property descriptors of an object         |
| Trailing Commas in Functions        | Supports trailing commas in function arguments and calls|
| SharedArrayBuffer & Atomics         | Enables shared memory and atomic operations for threads |
+-------------------------------------+---------------------------------------------------------+
*/
// #1 - Async/Await - Syntactic sugar for Promises,
const fetchData = async () => {
  try {
    const response = await fetch('https://jsonplaceholder.typicode.com/posts/1')
    const data = await response.json()
    console.log(data)
  } catch (error) {
    console.error('Error:', error)
  }
}

fetchData()
// {
//    userId: 1,
//    id: 1,
//    title: 'sunt aut facere repellat provident occaecati excepturi optio reprehenderit',
//    body: 'quia et suscipit\n' +
//          'suscipit recusandae consequuntur expedita et cum\n' +
//          'reprehenderit molestiae ut ut quas totam\n' +
//          'nostrum rerum est autem sunt rem eveniet architecto'
// }

// #2 - Object.values() - Returns an array of a given object’s own enumerable property values.
const superhero = { id: 9089, name: 'Batman', age: 32 }
console.log(Object.values(superhero)) // [9089, 'Batman', 32]

// #3 - Object.entries() - Returns an array of a given object’s own enumerable property [key, value] pairs.
console.log(Object.entries(superhero)) // [ [ 'id', 9089 ], [ 'name', 'Batman' ], [ 'age', 32 ] ]

// #4 - Object.getOwnPropertyDescriptors() - Returns property descriptors for all properties of an object.
console.log(Object.getOwnPropertyDescriptors(superhero))
/*
{
  id: { value: 9089, writable: true, enumerable: true, configurable: true },
  name: {
    value: 'Batman',
    writable: true,
    enumerable: true,
    configurable: true
  },
  age: { value: 32, writable: true, enumerable: true, configurable: true }
}
*/

/*
+--------------------------------------+-------------------------------------------------------+
|                                     ESM 9                                                    |
+--------------------------------------+-------------------------------------------------------+
| Feature                              | Description                                           |
+--------------------------------------+-------------------------------------------------------+
| Rest/Spread with Objects             | ... syntax for cloning and merging objects            |
| for await...of Loop                  | Asynchronous iteration for streams or async iterables |
| Promise.prototype.finally()          | Runs code after promise resolution or rejection       |
| RegEx: s Flag (dotAll)               | . matches newlines in regex                           |
| RegEx: Named Capture Groups          | Adds names to capture groups for clarity              |
+--------------------------------------+-------------------------------------------------------+
*/
// #1 - Rest/Spread Properties for Objects
const superhero = { id: 9810, name: 'Superman', age: 35 }
const { age, ...rest } = superhero

console.log(rest) // { id: 9809, name: 'Superman' }

const updateSuperHero = { ...superhero, powers: ['flying', 'super strength', 'heat vision'] }
console.log(updateSuperHero) // { id: 9810, name: 'Superman', age: 35, powers: [ 'flying', 'super strength', 'heat vision' ]}

// #2 -  Asynchronous Iteration with (for await...of) loop
async function fetchPosts() {
  const urls = ['https://jsonplaceholder.typicode.com/posts/1', 'https://jsonplaceholder.typicode.com/posts/2']

  for await (const url of urls) {
    const response = await fetch(url)
    const post = await response.json()
    console.log(post.title)
  }
}

fetchPosts()
// sunt aut facere repellat provident occaecati excepturi optio reprehenderit
// qui est esse

// #3 - Promise.prototype.finally() - Executes a callback after a promise is settled (either resolved or rejected).
fetch('https://jsonplaceholder.typicode.com/posts/1')
  .then((response) => response.json())
  .then((data) => console.log(data.userId))
  .catch((error) => console.error('Error:', error))
  .finally(() => console.log('Request completed'))
// 1
// Request completed

// #4 - Regular Expression Improvements
const regex = /bruce.wayne/s // Allows . to match newline characters (\n).
console.log(regex.test('bruce\\wayne')) // true

const dateRegex = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/ // Improves regex readability with named groups.
const match = dateRegex.exec('2025-02-17')

console.log(match.groups) // { year: '2025', month: '02', day: '17' }
console.log(match.groups.year) // 2025

/*
+---------------------------------------+------------------------------------------+
|                                     ESM 10                                       |                   
+---------------------------------------+------------------------------------------+
| Feature                               | Description                              |
+---------------------------------------+------------------------------------------+
| Array.prototype.flat()                | Flattens nested arrays                   |
| Array.prototype.flatMap()             | Maps and flattens arrays in one step     |
| Object.fromEntries()                  | Converts key-value pairs to objects      |
| String.prototype.trimStart()/trimEnd()| Trims spaces from strings                |
| Optional catch Binding                | catch without error parameter            |
| Symbol.description                    | Retrieves symbol descriptions            |
| Function.prototype.toString()         | Returns exact source code                |
| Well-Formed JSON.stringify()          | Properly handles Unicode characters      |
| BigInt (Stage 3)                      | Supports large integers                  |
+--------------------------------------+-------------------------------------------+
*/
// #1 flat and flatMap methods for arrays
const nestedNumbers = [1, [2, [3, [4]]]]

console.log(nestedNumbers.flat()) // 1 level flattening [1, 2, [3, [4]]]
console.log(nestedNumbers.flat(2)) // 2 level flattening [1, 2, 3, [4]]
console.log(nestedNumbers.flat(Infinity)) // infinite flattening [1, 2, 3, 4]

// Combines map() and flat() in one method.
console.log(nestedNumbers.flat(Infinity).flatMap((x) => [x, x * 2])) // [1, 2, 2, 4, 3, 6, 4, 8]

// #2 - Object.fromEntries()
const superHeroArray = [
  ['name', 'Bruce'],
  ['age', 32],
]
const superHeroObject = Object.fromEntries(superHeroArray)

console.log(superHeroObject) // { name: 'Bruce', age: 32 }

// #3 - trimStart and trimEnd
const trimmedSuperHero = '    Superman    '

console.log(trimmedSuperHero.trimStart()) // Superman___
console.log(trimmedSuperHero.trimEnd()) // ___Superman

// #4 - Optional Catch Binding in try...catch
try {
  throw new Error('Superhero not found!')
} catch {
  console.log('An error occurred')
}

// #5 - Symbol.description
const sym = Symbol('Bruce way is batman')
console.log(sym.description) // Bruce way is batman

// #6 - Function.prototype.toString() Revision - Returns the exact function body
function isSuperHero() {
  console.log('Bruce way is batman')
}

console.log(isSuperHero.toString())
// function isSuperHero () {
//    console.log('Bruce way is batman');
// }

// #7 - Well-Formed JSON.stringify() for emojis
console.log(JSON.stringify('\uD83D\uDE00')) // Outputs: '"😀"'

// #8 - BigInt - Supports integers beyond Number.MAX_SAFE_INTEGER
const bigNumber = 123456789012345678901234567890n
console.log(bigNumber + 10n) // 123456789012345678901234567900n

/*
+---------------------------------------+-------------------------------------------------------------------------+
|                                     ESM 11                                                                      |
+---------------------------------------+-------------------------------------------------------------------------+
| Feature                               | Description                                                             |
+---------------------------------------+-------------------------------------------------------------------------+
| BigInt                                | Large integers beyond Number.MAX_SAFE_INTEGER                           |
| Nullish Coalescing (??)               | Returns right-hand operand only if left-hand is null/undefined          |
| Optional Chaining (?.)                | Safely access nested properties without causing errors                  |
| Promise.allSettled()                  | Resolves after all promises are settled (either fulfilled or rejected)  |
| globalThis                            | Standard global object across all JavaScript environments               |
| String.prototype.matchAll()           | Returns an iterator for all matches in a string                         |
| Stable Array.prototype.sort()         | Ensures stable sorting (equal items retain original order)              |
| import.meta                           | Provides metadata about the current module                              |
+---------------------------------------+-------------------------------------------------------------------------+
*/
// #1 - Nullish Coalescing Operator (??) - It returns the right-hand operand when the left-hand operand is null or undefined.
const superhero = null
const userName = superhero ?? 'Batman'
console.log(userName) // 'Batman'

const human = 'Bruce'
const isHuman = human ?? 18
console.log(isHuman) // Bruce

// #2 -  Optional Chaining (?.) -  If any part of the chain is null or undefined, it short-circuits and returns undefined without throwing an error.
const superheroObject = { name: 'Batman', age: 32, human: { name: 'Bruce Wayne' } }

console.log(superheroObject?.name) // 'Batman'
console.log(superheroObject.age) // 32
console.log(superheroObject.human.name.fullName) // undefined (no error)

// #3 - Promise.allSettled() - Returns a promise that resolves when all promises have been settled (either resolved or rejected).
const p1 = Promise.resolve('Batman')
const p2 = Promise.reject('No superhero found')
const p3 = Promise.resolve('Superman')

Promise.allSettled([p1, p2, p3]).then((results) => results.forEach((result) => console.log(result.status)))
// 'fulfilled', 'rejected', 'fulfilled'

// #4 - globalThis - A standard global object that works across all JavaScript environments

// #5 - matchAll() - Returns an iterator for all matches in a string
const regex = /man+/g
const str = 'Superman Batman Flash'

const matches = str.matchAll(regex)

for (const match of matches) {
  console.log(match[0]) // man man
}

// #6 - import.meta
console.log(import.meta.url) // Displays the current module's URL

/*
+--------------------------------------+----------------------------------------------------------------------------------------------+
|                                    ESM 12                                                                                           |
+--------------------------------------+----------------------------------------------------------------------------------------------+
| Feature                              | Description                                                                                  |
+--------------------------------------+----------------------------------------------------------------------------------------------+
| Logical Assignment Operators         | Combines logical operators with assignment (&&=, ||=, ||=)                                   |
| Promise.any()                        | Resolves with the first fulfilled promise in an array of promises                            |
| WeakRefs                             | Allows referencing objects without preventing garbage collection                             |
| String.prototype.replaceAll()        | Replaces all occurrences of a substring in a string                                          |
| Numeric Separators                   | Makes large numbers more readable using underscores (_)                                      |
| Object.hasOwn()                      | Checks if an object has a specific property as its own (more reliable than hasOwnProperty()) |
| Enhanced Array.prototype.sort()      | Numeric sorting now works correctly without a custom comparator                              |
+--------------------------------------+----------------------------------------------------------------------------------------------+
*/
// #1 - Logical Assignment Operators - &&, ||, ??
let x = 1
x &&= 2 // x remains 2, because x was truthy
console.log(x) // 2

let y = 0
y &&= 3 // y remains 0, because y is falsy
console.log(y) // 0

let a = null
a ||= 'default' // a is assigned 'default', because it's falsy
console.log(a) // 'default'

let b = null
b ??= 'fallback' // b is assigned 'fallback', because it's nullish
console.log(b) // 'fallback'

// #2 - Promise.any() - returns the first promise that resolves
const p1 = Promise.reject('Superhero not found')
const p2 = Promise.reject('Human not found')
const p3 = Promise.resolve('Martian found')

Promise.any([p1, p2, p3])
  .then((result) => console.log(result)) // 'Martian found'
  .catch((err) => console.log(err))

// #3 - WeakRefs - allow you to reference objects without preventing them from being garbage collected.
let superhero = { name: 'Batman' }
let weakRef = new WeakRef(superhero)

// Access the object (if it hasn't been garbage collected)
console.log(weakRef.deref()) // { name: 'Batman' }

// After `superhero` is dereferenced, it may be garbage collected
superhero = null // superhero can be garbage collected

// #4 - replaceAll() - replacing all occurrences of a substring in a string
const text = 'Batman has the kryptonite in case superman goes dooms day'
const result = text.replaceAll('o', '0')
console.log(result) // 'Batman has the krypt0nite in case superman g0es d00ms day'

// #5 - Numeric Separators (_) for numbers
const price = 100_000_000
console.log(price) // 100000000

// #6 - Object.hasOwn() to check whether an object has a property
const superheroObject = { name: 'Batman', age: 32 }
console.log(Object.hasOwn(superheroObject, 'name')) // true
console.log(Object.hasOwn(superheroObject, 'human')) // false

// #7 - Numeric sorting improved
const numbers = [10, 1, 21, 2]
numbers.sort() // Default behavior: lexicographic sorting
console.log(numbers) // ['1', '10', '2', '21']

const sortedNumbers = [10, 1, 21, 2]
sortedNumbers.sort((a, b) => a - b) // Numeric sorting
console.log(sortedNumbers) // [1, 2, 10, 21]

/*
+--------------------------------------+------------------------------------------------------------------+
|                                    ESM 13                                                               |
+--------------------------------------+------------------------------------------------------------------+
| Feature                              | Description                                                      |
+--------------------------------------+------------------------------------------------------------------+
| Array.at()                           | Allows accessing array elements with negative indices            |
| Top-Level await                      | Allows await at the top level of modules without async functions |
| WeakRefs with FinalizationRegistry   | Manages resources and cleanup when objects are garbage collected |
| Error.cause                          | Adds a cause property to errors for better error handling        |
| Object.hasOwn()                      | Checks if an object has a property directly (not inherited)      |
| Improved copyWithin()                | Enhancements to copyWithin() method for copying array elements   |
+--------------------------------------+------------------------------------------------------------------+
*/
// #1 - Array at() Method
const superheroes = ['Batman', 'Superman', 'Spiderman', 'Ironman', 'Captain America']

console.log(superheroes.at(1)) // Superman (from the start)
console.log(superheroes.at(-1)) // Captain America (from the end)
console.log(superheroes.at(-2)) // Ironman (from the end)

// #2 - Top-Level await - Allows the use of await at the top level of modules without needing to wrap it in an async function
// In an ES module (e.g., `index.mjs`)
// const response = await fetch('https://jsonplaceholder.typicode.com/posts/1');
// const data = await response.json();
// console.log(data);

// #3 - WeakRefs with FinalizationRegistry
const registry = new FinalizationRegistry((value) => {
  console.log(`Object ${value} has been garbage collected`)
})

let obj = { name: 'Bruce' }
registry.register(obj, 'Bruce')

obj = null // Object will be collected, triggering the callback

// #4 - Error.cause - Provides a way to add a cause to an Error object.

try {
  throw new Error('Something went wrong', { cause: 'Fake API call' })
} catch (err) {
  console.log(err.message) // 'Something went wrong'
  console.log(err.cause) // 'Fake API call'
}

// #5 - Array copyWithin() method
const numbers = [1, 2, 3, 4, 5]
numbers.copyWithin(0, 3) // Copies elements from index 3 to index 0
console.log(numbers) // [4, 5, 3, 4, 5]

/*
+--------------------------------------+------------------------------------------------------------------------------------------------------+
|               ESM 14                 |                                                                                                      |
+--------------------------------------+------------------------------------------------------------------------------------------------------+
| Feature                              | Description                                                                                          |
+--------------------------------------+------------------------------------------------------------------------------------------------------+
| Array.prototype.toSorted()           | Returns a sorted copy of an array, without mutating the original array                               |
| Array.prototype.toReversed()         | Returns a reversed copy of an array, without mutating the original array                             |
| Array.prototype.toSpliced()          | Returns a modified copy of an array with elements removed/added, without mutating the original array |
| Symbol.prototype.description         | A new property that returns the description of a symbol                                              |
| Improved RegExp Features             | Enhanced regex capabilities with flags like d for dotall mode                                        |
| Error Stack Trace Improvements       | More detailed and accurate stack trace information, including async functions                        |
| Object.hasOwn() Improvements         | More reliable and preferred method for checking an object's properties                               |
+--------------------------------------+------------------------------------------------------------------------------------------------------+
*/
// #1 - Array.prototype.toSorted() - creates a sorted copy of an array without mutating the original array.
const superheros = ['Superman', 'Batman', 'Flash']
const sortedSuperheros = superheros.toSorted()
console.log(sortedSuperheros) // [ 'Batman', 'Flash', 'Superman' ]
console.log(superheros) // Original array: [ 'Superman', 'Batman', 'Flash' ]

// #2 - Array.prototype.toReversed() - returns a new array with the elements in reversed order, without changing the original array.
const reversedSuperheros = superheros.toReversed()
console.log(reversedSuperheros) // [ 'Flash', 'Batman', 'Superman' ]
console.log(superheros) // Original array: [ 'Superman', 'Batman', 'Flash' ]

// #3 - Array.prototype.toSpliced() - returns a new array with elements removed and/or added, without mutating the original array
const splicedSuperheros = superheros.toSpliced(1, 1, 'Aquaman')
console.log(splicedSuperheros) // [ 'Superman', 'Aquaman', 'Flash' ]
console.log(superheros) // Original array: [ 'Superman', 'Batman', 'Flash' ]

// #4 - Improved RegExp Features
const regex = /foo.bar/s
const result = regex.test('foo\nbar') // true, because `.` can now match newlines
console.log(result)
