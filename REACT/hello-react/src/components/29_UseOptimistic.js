import React, { useState, useOptimistic, useTransition } from 'react'

function UseOptimistic() {
  const [name, setName] = useState('')
  const [optimisticName, setOptimisticName] = useOptimistic('', (currentName, newName) => newName)
  const [isPending, startTransition] = useTransition()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setOptimisticName(name) // Optimistically update the name

    // Simulate an async operation (e.g., API call)
    const response = await updateName(name) // Assume this function makes an API call

    if (response.error) {
      console.log(optimisticName)
      // If there's an error, revert to the previous state automatically
      // No need to handle reversion manually, beauty of useOptimistic hook
    } else {
      console.log(optimisticName)

      // Handle success (e.g., update state or redirect)
    }
  }

  // Simulated API call function with failure
  async function updateName(name) {
    startTransition(async () => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ success: 'Failed to update name' }) // Simulate an error response
        }, 2000)
      })
    })
  }

  return (
    <>
      <h1>UseOptimistic Hook</h1>
      {isPending ? <p>Fetching...</p> : <p>Optimistic Value: {optimisticName}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          Name: <input type='text' value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <button type='submit'>Submit</button>
      </form>
    </>
  )
}

export default UseOptimistic
