import React, { useRef } from 'react'

const UseRefHook = () => {
    const count = useRef(0)
    const divStyling = useRef();

    const handleCount = () => {
        count.current++
        console.log(`UseRef clicked ${count.current} times`)
        divStyling.current.style.backgroundImage = "linear-gradient(to right, #84fab0 0%, #8fd3f4 51%, #84fab0 100%)"
        /*Updating references restriction LOL:
        
                The function scope of the functional component should either calculate the output or invoke hooks.
                
                That's why updating a reference (as well as updating state) shouldn't be performed inside the immediate scope of the component's function.The reference must be updated either inside a useEffect() callback or inside handlers (event handlers, timer handlers, etc).
        */
    }
    console.log("I am not re-rendering because of useRef() updating the persisted value's 'reference'")
    return (
        <div>
            <h1>UseRef Hook</h1>
            <button onClick={() => handleCount(count + 1)} ref={divStyling}> UseRef Magic </button>
        </div>)
}

export default UseRefHook