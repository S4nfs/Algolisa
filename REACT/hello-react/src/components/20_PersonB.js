import React, { Component } from 'react'
import subjects from './20_HOC'

export class PersonB extends Component {
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
                <h3 onMouseOver={this.marksIncrease}>Person B marks is {this.state.marks} in {this.props.hocsub}</h3>
            </div>
        )
    }
}

export default subjects(PersonB)