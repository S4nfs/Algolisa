import React from 'react';

export const Header = (props) => { //function name should match with the filename
    console.log(props)
    return (
        <div>
            <h4>Hello React By {props.name} From ✏️ Functional Component</h4>
            {props.children}
        </div>
    )
}

// export default Header;