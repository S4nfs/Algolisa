import React, { Component } from 'react'

//check LifeCycle B flow using console.log-------------------------------------------------------------------------------------
export class LifeCycleB extends Component {
    constructor(props) {
        super(props)
        this.state = {
            name: 'Sagar'
        }
        console.log("LifeCycleB: constructor")

    }
    //getDerivedStateFromProps reflets changes to vDOM before actual DOM
    static getDerivedStateFromProps(props, state) {
        console.log("LifeCycleB: getDerivedStateFromProps")
        return null;
    }
    //componentDidMount is called after render method to reflects actual changes
    componentDidMount() {
        console.log("LifeCycleB: componentDidMount")
    }
    render() {
        console.log("LifeCycleB: render")
        return (
            <div>LifeCycleB</div>
        )
    }
}

export default LifeCycleB