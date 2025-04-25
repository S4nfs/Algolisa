import React, { useCallback, useState } from 'react'

const CustomHook = () => {
  const [toggle, toggleChange] = useToggle()
  return (
    <>
      <h1>My Custom Hook</h1>
      <button onClick={toggleChange}>Toggle {`${toggle}`}</button>
    </>
  )
}

//Custom Toggle Hook
const useToggle = (initialState = false) => {
  const [toggle, setToggle] = useState(initialState)
  const toggleChange = useCallback(() => {
    setToggle((toggle) => !toggle)
  })
  return [toggle, toggleChange]
}

export default CustomHook
