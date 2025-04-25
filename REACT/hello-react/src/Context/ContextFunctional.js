import { useState, createContext } from 'react'
export const Mycontext = createContext()

function ContextFunctional(props) {
    const [count, setcount] = useState(0)
    function increaseCount() {
        setcount(count + 1)
    }
    function decreaseCount() {
        setcount(count - 1)
    }

    const values = { count, increaseCount, decreaseCount }    //the function which can be used anywhere
    return (
        <Mycontext.Provider value={values}>
            {props.children}
        </Mycontext.Provider>
    )
}

export default ContextFunctional