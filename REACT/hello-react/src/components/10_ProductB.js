import React, { Component } from 'react'

class ProductB extends Component {
    constructor(props) {
        super(props)

        this.state = {
            ProductID: '',
            qty: 0
        }
    }
    addToCart = (pid) => {
        this.setState({
            ProductID: pid,
            qty: this.state.qty + 1
        })
    }
    render() {
        return (
            <div>
                <button onClick={() => { this.addToCart(1) }}>Add to cart</button>
                <Cart ProductID={this.state.ProductID} qty={this.state.qty}></Cart>
            </div>
        )
    }
}

export default ProductB

class Cart extends Component {
    constructor(props) {
        super(props)
        this.state = {
            qty: this.props.qty
        }
    }
    // updateQty = () => {
    //     this.setState = ({
    //         qty: this.state.qty + 1
    //     })
    // }

    //Executes when a change in state occurs due to props value, In short: state is dependent on props
    static getDerivedStateFromProps(props, state) {
        console.log(props.qty, state.qty)
        if (props.qty !== state.qty) {
            return { qty: props.qty }
        }
        return null;
    }
    // componentDidMount() {
    //     console.log("Execute after component render")
    // }
    // componentDidUpdate(prevProps, prevState) {
    //     console.log("Component updated in actual DOM")
    // }

    render() {
        return (
            <div>
                <h1>CART: {this.state.qty}</h1>
                {/* <button onClick={this.updateQty}>Update Qty</button> */}
            </div>
        )
    }
}
