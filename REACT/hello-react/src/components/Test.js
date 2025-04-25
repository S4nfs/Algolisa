import React, { useState } from 'react'


function Test() {
    const [speed, trigger] = useState(0);
    const [counter, setcounter] = useState(0);

    const speedincrease = () => {
        console.log(speed)
        trigger(speed + 10)
    }
    return (
        <div>
            <h1>{speed}</h1>
            <button onClick={speedincrease}>Click</button>
            <button onClick={() => setcounter(counter + 1)}>Counter: {counter}</button>
        </div>
    )
}

export default Test