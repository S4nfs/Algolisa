import React, { useEffect, useRef } from 'react'
import { useRenderCountContext } from './renderCounter'

const RenderTracker = ({ children }) => {
  const { incrementRenderCount } = useRenderCountContext()
  const hasCountedRef = useRef(false) // Track if the component has already been counted

  // Increment the render count only when the component mounts
  useEffect(() => {
    if (!hasCountedRef.current) {
      incrementRenderCount()
      hasCountedRef.current = true // Mark the component as counted
    }
  }, [incrementRenderCount])

  return <>{children}</>
}

export default RenderTracker
