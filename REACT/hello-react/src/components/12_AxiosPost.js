import React, { Component } from 'react'
import axios from 'axios'
export class PostAxios extends Component {
    constructor(props) {
        super(props)

        this.state = {
            userid: '',
            title: '',
            description: ''
        }
    }
    changeHandler = (e) => {
        this.setState({ [e.target.name]: e.target.value })
    }
    handleSubmit = (e) => {
        e.preventDefault();
        console.log(this.state);
        axios.post('https://jsonplaceholder.typicode.com/posts', this.state)
            .then(res => {
                this.setState({
                    post: res.data
                })
                console.log(res)
            }).catch(err => {
                this.setState({
                    error: 'Unable to post data :('
                })
                console.log(err)
            })
    }
    render() {
        const { userid, title, description } = this.state
        return (
            <div>
                POST using Axios
                <form onSubmit={this.handleSubmit}>
                    <div>
                        <label>UserID </label>
                        <input type="text" name="userid" id="" value={userid} onChange={this.changeHandler} />
                    </div>
                    <div>
                        <label>Password </label>
                        <input type="text" name="title" id="" value={title} onChange={this.changeHandler} />
                    </div>
                    <div>
                        <label>Description </label>
                        <input type="text" name="description" id="" value={description} onChange={this.changeHandler} />
                    </div>
                    <button type="submit">Submit</button>
                </form>
            </div>
        )
    }
}

export default PostAxios