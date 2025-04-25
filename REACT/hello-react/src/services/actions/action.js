
export const addToCart = (data) => {
    // console.warn(`Redux Cart Data: ${data}`)
    return {
        type: "ADD_TO_CART",
        data: data
    }
}

export const removeToCart = () => {
    return {
        type: "REMOVE_TO_CART",
    }
}
