import React, { useState } from 'react'

//changing objects in functional component with useState
function HookObject() {
    const [name, trigger] = useState({
        firstname: '',
        lastname: ''
    })
    return (
        <div>
            <form >
                <div>
                    <label htmlFor="">Firstname </label>
                    <input type="text" name="" id="" value={name.firstname} onChange={e => { trigger({ ...name, firstname: e.target.value }) }} />
                </div>
                <div>
                    <label htmlFor="">Lastname </label>
                    <input type="text" name="" id="" value={name.lastname} onChange={e => { trigger({ ...name, lastname: e.target.value }) }} />
                </div>
                {name.firstname}
                {name.lastname}
                <button type="submit">Submit</button>
            </form>
        </div>
    )
}

export default HookObject