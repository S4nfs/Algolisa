import React, { Component } from 'react'
export class PersonA extends Component {
    state = {
        marks: 0
    }

    marksIncrease = () => {
        this.setState({ marks: this.state.marks + 1 })
    }
    render() {
        return (
            <div>
                <div></div>
                <h3 onMouseOver={this.marksIncrease}>Person A marks is {this.state.marks}</h3>
            </div>
        )
    }
}

export default PersonA