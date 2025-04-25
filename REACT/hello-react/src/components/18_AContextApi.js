import React, { Component } from 'react'
import BContextApi from './18_BContextApi';
import CContextApi from './18_CContextApi';
import { Mycontext } from './18_Context';

//WHY context API?
//pass data down to other component without using props, Here Context API helps to avoid prop drilling
export class AContextApi extends Component {
    state = {
        name: "Sagar Verma",
        roll: 28
    }
    handleClickContext = () => {
        this.setState({
            roll: this.state.roll + 1
        })
    }
    render() {
        const payload = {
            data: this.state,
            handlecheck: this.handleClickContext
        }
        return (
            <div>
                <Mycontext.Provider value={payload}>
                    <BContextApi />
                    <CContextApi />
                </Mycontext.Provider>
            </div>
        )
    }
}

export default AContextApi