import React from 'react'
import sc from './shopping-cart.png'

function Redux(props) {
    console.warn("Redux prop data: ", props.data)
    // window.store = props
    return (
        <div>
            <h1>Redux Component</h1>
            <div className="add-to-cart">
                <span>{props.data.length}</span>
                <img src={sc} alt="" set="" />
            </div>
            <div className="cart-wrapper">
                <div className="img-wrapper item">
                    <img src="https://www.tesla.com/sites/default/files/images/roadster/roadster-social.jpg" alt="" srcset="" />
                </div>
                <div className="text-wrapper item">
                    <span>
                        Roadster
                    </span>
                    <span>
                        Price: $50000
                    </span>
                </div>
                <div className="btn-wrapper item">
                    <button onClick={() => props.addToCartHandler({ price: 80000, name: "TeslaModel S" })}>Add to Cart</button>
                    <button onClick={() => props.removeToCartHandler()} style={{ backgroundColor: "red", marginTop: "8px" }}>Remove to Cart</button>
                </div>
            </div>
        </div>
    )
}

export default Redux