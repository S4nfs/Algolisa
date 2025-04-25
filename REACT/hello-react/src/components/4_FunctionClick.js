import React from 'react'

function clickme() {
    alert("you just click me");
}
function FunctionClick() {
    return (
        <div>
            <button onClick={clickme}>Click me ! I am a function event listener</button>
        </div>
    )
}

export default FunctionClick