import React, { Component } from 'react'
import { legacy_createStore as createStore } from 'redux'


export class ReduxClassComponent extends Component {
    render() {

        //Step 2: reducer - state n action
        const reducer = function (state, action) {
            if (action.type === "Law 1") {
                return action.payload;
            }
            if (action.type === "Law 2") {
                return action.payload;
            }
            return state;               //else return initial state
        }

        //Step 1: Store - reducer n state
        const store = createStore(reducer, "Old Law");

        //Step 3: Subscribe
        store.subscribe(() => {
            console.log("Store value is :", store.getState());
        })

        //Step 4: Dispatch action
        store.dispatch({ type: "Law 1", payload: "No cursing allowed" })
        store.dispatch({ type: "Law 2", payload: "No buying cars and RVs on Sundays" })

        return (
            <h1>
                Redux Class Component
            </h1>
        )
    }
}

export default ReduxClassComponent