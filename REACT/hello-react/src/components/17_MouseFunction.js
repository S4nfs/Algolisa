import React, { useEffect, useState } from 'react'

function MouseFunction() {
    const [x, setX] = useState(0);
    const [y, setY] = useState(0);

    const logmouseposition = (e) => {
        setX(e.clientX)
        setY(e.clientY)
    }
    useEffect(() => {
        window.addEventListener('mousemove', logmouseposition)
    })

    return (
        <div>X- {x} Y- {y}</div>
    )
}

export default MouseFunction