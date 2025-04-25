import React, { Component } from 'react'
import { Mycontext } from './18_Context'


export class CContextApi extends Component {
    render() {
        return (
            <div>
                <h1>ContextAPI using class component</h1>
                <Mycontext.Consumer>
                    {
                        ({ data }) => <h3>{data.roll}</h3>
                    }
                </Mycontext.Consumer>
            </div>
        )
    }
}

export default CContextApi