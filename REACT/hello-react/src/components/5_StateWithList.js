import React, { Component } from 'react'
import Testing from './5_Testing'

export class StateWithList extends Component {

    state = {   //state without constructor
        users: [
            { id: 1, name: "brian", class: "A" },
            { id: 2, name: "micky", class: "F" },
        ]
    }
    render() {
        //use of keys(must be unique and single attribute in only one page) in lists and also exporting value to component Testing.js
        return (
            this.state.users.map((users) => {
                return (
                    <div>
                        <h3 key={users.id}>{users.id} ---- {users.name}</h3>
                        <Testing value={users.id}></Testing>
                    </div>)
            })
        )
    }
}

export default StateWithList