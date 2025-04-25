import React, { createContext, useContext, useState } from 'react'

// Create a context to store the total re-render count
const RenderCountContext = createContext()

// Custom hook to access the render count context
export const useRenderCountContext = () => useContext(RenderCountContext)

// RenderCountProvider component to wrap your app
export const RenderCountProvider = ({ children }) => {
  const [totalRenderCount, setTotalRenderCount] = useState(0)

  // Function to increment the total render count
  const incrementRenderCount = () => {
    setTotalRenderCount((prevCount) => prevCount + 1)
  }

  return <RenderCountContext.Provider value={{ totalRenderCount, incrementRenderCount }}>{children}</RenderCountContext.Provider>
}
