import React from 'react'
import ContextFunctional from '../Context/ContextFunctional'
import FunctionContextB from './19_FunctionContextB'
import FunctionContextC from './19_FunctionContextC'

function FunctionContextA() {
    return (
        <div>
            <ContextFunctional>
                <FunctionContextB />
                <FunctionContextC />
            </ContextFunctional>
        </div>
    )
}

export default FunctionContextA