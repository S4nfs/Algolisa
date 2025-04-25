import React, { useState, useTransition } from 'react'

const UseTransition = () => {
  const nameList = [
    { id: 1, name: 'Sagar' },
    { id: 2, name: 'Vinamra' },
    { id: 3, name: 'Rakshit' },
    { id: 4, name: 'John' },
    { id: 5, name: 'Doe' },
    { id: 6, name: 'Alpha' },
    { id: 7, name: 'Bravo' },
  ]
  const [isPending, startTransition] = useTransition() // best use case for fetching APIs
  const [list, setList] = useState(nameList)
  const [name, setName] = useState('')

  // console.log(isPending)          //false
  function handleChange(e) {
    setName(e.target.value)
    startTransition(async () => {
      //lower priorty state, here list
      // console.log(isPending)  //true
      await new Promise((resolve) => setTimeout(resolve, 1000))
      if (e.target.value === '') setList(nameList)
      else {
        setList(list.filter((item) => item.name.toLowerCase().includes(e.target.value.toLowerCase())))
      }
    })
  }
  return (
    <>
      <h1>UseTransition Hook (search my name)</h1>
      <input type='text' onChange={handleChange} value={name} />
      {isPending ? <div>Searching...</div> : list.map((item) => <div key={item.id}>{item.name}</div>)}
    </>
  )
}

export default UseTransition
