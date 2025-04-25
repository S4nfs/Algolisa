import React, { Component } from 'react'

export class MouseClass extends Component {
    constructor(props) {
        super(props)

        this.state = {
            x: 0,
            y: 0
        }
    }

    logmouseposition = (e) => {
        this.setState({ x: e.clientX, y: e.clientY })
    }
    componentDidMount() {
        window.addEventListener('mousemove', this.logmouseposition)
    }
    render() {
        return (
            <div>X- {this.state.x} Y- {this.state.y}</div>
        )
    }
}

export default MouseClass