import React, { Component } from 'react'
import { Mycontext } from './18_Context'

// The most common way to access Context from a class component is via the static contextType. If you need the value from Context outside of render, or in a lifecycle method, you'll use it this way.
export class BContextApi extends Component {
  static contextType = Mycontext
  componentDidMount() {
    console.log('helloooooo', this.context.data.name)
  }
  render() {
    return (
      <div>
        <h1>ContextAPI using class component</h1>
        <Mycontext.Consumer>
          {({ data, handlecheck }) => (
            <div>
              <h3>
                {data.name},{data.roll}
              </h3>
              <button onClick={handlecheck}>Change roll no using Context API</button>
            </div>
          )}
        </Mycontext.Consumer>
      </div>
    )
  }
}
export default BContextApi
