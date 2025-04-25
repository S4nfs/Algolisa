//container job is to join react to redux 
/*Flow = action-->reducer-->store
*/
import { connect } from 'react-redux'
import Redux from '../components/21_Redux'
import { addToCart, removeToCart } from '../services/actions/action'

const mapStateToProps = (state) => ({    //button events
    data: state.cartItems
})

const mapDispatchToProps = (dispatch) => ({
    addToCartHandler: (data) => dispatch(addToCart(data)),
    removeToCartHandler: (data) => dispatch(removeToCart(data))
})

export default connect(mapStateToProps, mapDispatchToProps)(Redux);