import React, { useContext } from 'react'
import { Mycontext } from '../Context/ContextFunctional'

function FunctionContextB() {
    const { count, increaseCount, decreaseCount } = useContext(Mycontext)

    return (
        <div style={{ backgroundColor: 'wheat' }}>
            <h1>ContextAPI using function component</h1>
            <p>Count: {count}</p>
            <button onClick={increaseCount}>Increase</button>
            <button onClick={decreaseCount}>Decrease</button>
        </div>
    )
}

export default FunctionContextB