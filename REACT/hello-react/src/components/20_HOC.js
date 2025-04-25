import React, { Component } from 'react'

// A higher-order component (HOC) is an advanced technique in React for reusing component logic, here we are adding extra functionalities in PersonB's component
const subjects = (STUDENT) => {
    class Subject extends Component {
        render() {
            return (
                <STUDENT hocsub="GoLang"></STUDENT>
            )
        }
    }
    return Subject
}
export default subjects