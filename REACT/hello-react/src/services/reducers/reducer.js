//reducer
const initialState = {
    cartData: []
}
export default function cartItems(state = [], action) {
    switch (action.type) {
        case "ADD_TO_CART":
            // console.warn("Redux reducer data: ", action)

            return [
                ...state,
                { cartData: action.data }
            ]
        case "REMOVE_TO_CART":
            // console.warn("Redux reducer data: ", action)
            state.pop()
            return [
                ...state,
            ]
        default:
            return state            //else return initialstate

    }
}