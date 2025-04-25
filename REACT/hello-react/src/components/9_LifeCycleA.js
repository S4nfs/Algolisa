import React, { Component } from 'react'
import LifeCycleB from './9_LifeCycleB';

/*credits: https://projects.wojtekmaj.pl/react-lifecycle-methods-diagram/
check LifeCycle flow using console.log-------------------------------------------------------------------------------------*/
export class LifeCycleA extends Component {
    constructor(props) {
        super(props)
        this.state = {
            name: 'Sagar'
        }
        console.log("LifeCycleA: constructor")

    }
    //getDerivedStateFromProps reflets changes to vDOM before actual DOM
    static getDerivedStateFromProps(props, state) {
        console.log("LifeCycleA: getDerivedStateFromProps")
        return null;
    }
    //componentDidMount is called after render method to reflects actual changes
    componentDidMount() {
        console.log("LifeCycleA: componentDidMount")
    }
    render() {
        console.log("LifeCycleA: render")
        return (
            <div>
                <div>LifeCycleA</div>
                <LifeCycleB></LifeCycleB>
            </div>
        )
    }
}

export default LifeCycleA