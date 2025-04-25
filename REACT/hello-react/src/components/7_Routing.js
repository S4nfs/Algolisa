import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
function Routing() {
    return (
        <Router>
            <div>
                <nav>
                    <ul>
                        <li>
                            <Link to='/'>Home</Link>
                        </li>
                        <li>
                            <Link to='/about'>About</Link>
                        </li>
                        <li>
                            <Link to='/users'>Users</Link>
                        </li>
                    </ul>
                </nav>
            </div>

            <Routes>
                <Route path="/about" element={<About />} />
                <Route path="/users" element={<Users />} />
                <Route path="/home" element={<Home />} />
            </Routes>
        </Router>


    )
}
//child components to be called from Routes
function Home() {
    return <h1>Welcome to Home route</h1>
}

function About() {
    return <h1>Welcome to About route</h1>
}

function Users() {
    return <h1>Welcome to Users route</h1>
}
export default Routing