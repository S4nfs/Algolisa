import React, { Component } from 'react'

class ProductA extends Component {
    render() {
        return (
            <Cart></Cart>
        )
    }
}
export default ProductA

class Cart extends ProductA {
    constructor(props) {
        super(props)

        this.state = {
            qty: 0
        }
    }
    updateQty = () => {
        this.setState({
            qty: this.state.qty + 1
        })
    }

    componentDidMount() {
        console.log("Execute after component render")
    }
    componentDidUpdate(prevProps, prevState) {
        console.log("Component updated in actual DOM")
    }

    render() {
        return (
            <div>
                <h1>CART: {this.state.qty}</h1>
                <button onClick={this.updateQty}>Add to Cart</button>
            </div>
        )
    }
}
