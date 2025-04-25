import React, { useState } from 'react'

function HookArray() {
    const [items, trigger] = useState([]);
    const addItem = () => {
        trigger([...items, {
            id: items.length,
            value: Math.floor(Math.random() * 10)
        }])
    }
    return (
        <div>
            <button onClick={addItem}>Add a Random Number</button>
            <ul>
                {items.map(item => (<li key={item.value}> {item.value}</li>))}
            </ul>
        </div>
    )
}

export default HookArray