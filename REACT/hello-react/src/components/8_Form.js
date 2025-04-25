import React, { Component } from 'react'

export class Form extends Component {
    constructor(props) {
        super(props)
        this.state = {
            username: '',
            password: ''
        }
    }
    handleUsername = (event) => {
        this.setState({
            username: event.target.value
        })
    }
    handlePassword = (event) => {
        this.setState({
            password: event.target.value
        })
    }
    handleSubmit = (event) => {
        alert(`${this.state.username} ${this.state.password}`)
        event.preventDefault();
    }
    render() {
        return (
            <div>
                <form onSubmit={this.handleSubmit}>
                    <div>
                        <label htmlFor="">Username </label>
                        <input type="text" name="" id="" value={this.state.username} onChange={this.handleUsername} />
                    </div>
                    <div>
                        <label htmlFor="">Password </label>
                        <input type="text" name="" id="" value={this.state.password} onChange={this.handlePassword} />
                    </div>
                    <button type="submit">Submit</button>
                </form>
            </div>
        )
    }
}

export default Form