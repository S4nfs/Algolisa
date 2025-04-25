// import React, { Component } from 'react'
// import axios from 'axios'
// export class GetAxios extends Component {
//     constructor(props) {
//         super(props)

//         this.state = {
//             user: [],
//             searchField: '',
//             error: ''
//         }
//     }
//     componentDidMount() {
//         axios.get('https://jsonplaceholder.typicode.com/users')
//             .then(res => {
//                 this.setState({
//                     user: res.data
//                 })
//                 console.log(res)
//             }).catch(err => {
//                 this.setState({
//                     error: 'Unable to fetch data :('
//                 })
//                 console.log(err)
//             })
//     }
//     onSearchChange = (e) => {
//         const searchField = e.target.value.toLocaleLowerCase();

//         this.setState(() => {
//             return { searchField: searchField }
//         })
//     }
//     render() {
//         const { user, error, searchField } = this.state
//         //[{name:"sagar"},{ name:"antony"}]
//         const filteredSearch = user.filter(elem => elem.name.toLocaleLowerCase().includes(searchField))
//         return (
//             <div>
//                 GET using Axios<br></br>

//                 <input type="search" name="" id="" placeholder='Search by name' onChange={this.onSearchChange} />
//                 <table>
//                     <tr>
//                         <th>Name</th>
//                         <th>Username</th>
//                         <th>Email</th>
//                     </tr>
//                     {
//                         filteredSearch.length ? filteredSearch.map(users =>
//                             <tr key={users.id}>
//                                 <td> {users.name}</td>
//                                 <td>{users.username}</td>
//                                 <td>{users.email}</td>
//                             </tr>) : null
//                     }
//                 </table>
//                 {
//                     error ? <div>{error}</div> : null
//                 }
//             </div>
//         )
//     }
// }

// export default GetAxios

//---------------------------------------------------With Functional Component-----------------------------------------------

import React, { useEffect, useState } from 'react'
import axios from 'axios'

const GetAxios = () => {
    const [user, setuser] = useState([])
    const [error, setError] = useState('')
    const [searchField, setSearchField] = useState('')
    const [filteredSearch, setfilteredSearch] = useState(user)

    useEffect(() => {
        axios.get('https://jsonplaceholder.typicode.com/users')
            .then(res => {
                setuser(res.data)
            }).catch(err => {
                setError('Unable to fetch data :(')
            })
    }, [])
    const onSearchChange = (e) => {
        const searchField = e.target.value.toLocaleLowerCase();
        setSearchField(searchField)
    }
    useEffect(() => {
        const newfilteredSearch = user.filter(elem => elem.name.toLocaleLowerCase().includes(searchField))
        setfilteredSearch(newfilteredSearch)
    }, [user, searchField])


    return (
        <div>
            GET using Axios<br></br>

            <input type="search" name="" id="" placeholder='Search by name' onChange={onSearchChange} />
            <table>
                <tr>
                    <th>Name</th>
                    <th>Username</th>
                    <th>Email</th>
                </tr>
                {
                    filteredSearch.length ? filteredSearch.map(users =>
                        <tr key={users.id}>
                            <td> {users.name}</td>
                            <td>{users.username}</td>
                            <td>{users.email}</td>
                        </tr>) : null
                }
            </table>
            {
                error ? <div>{error}</div> : null
            }
        </div>
    )
}


export default GetAxios