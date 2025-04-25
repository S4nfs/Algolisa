import React, { forwardRef, useImperativeHandle, useRef } from 'react'

const UseImperativeHandle = () => {
    const inputRef = useRef(null)
    return (
        <Child onFocus={() => inputRef.current.focus()} ref={inputRef} />
    )
}


const Child = forwardRef((props, ref) => {         //referencing the below input box
    const input = useRef()

    useImperativeHandle(ref, () => ({
        focus: () => console.log("Input is in focus")
    }))
    return (
        <div>
            <h1>UseImerativeHandle Hook</h1>
            <input type="text" ref={input} {...props} placeholder="See console when focus" />
        </div>
    )
})
export default UseImperativeHandle