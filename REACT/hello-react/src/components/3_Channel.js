import React from 'react';

class Channel extends React.Component {
    constructor() {
        super();        //super keywork to call parent constructor which is react.component
        this.state = {
            msg: 'Hit the buttom to play React podcast on channel 55 using ✏️state'
        }
    }

    //create new state for eventlistener method playReactPodcast
    playReactPodcast() {
        this.setState({
            msg: 'Now playing...'
        })
    }

    render() {
        return (
            <div>
                <h4>{this.state.msg}</h4>
                <button onClick={() => { this.playReactPodcast() }}>Go Live</button>
            </div>

        )
    }
}
export default Channel;