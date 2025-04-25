import React, { useState } from 'react'

function HookUseState() {
  //classic approach
  // const startup = useState("Facebook")
  // const clickIt = () => {
  //     startup[1]("Meta")
  // }

  //modern approach, huh! it's just normal destructuring
  const [startup, newstartup] = useState('Facebook') //second index is the function name----.
  const clickIt = () => {
    //                                     |
    newstartup('Meta') //       <<---------------------------'
  }

  return (
    <div>
      {startup}
      <button onClick={clickIt}> Change Startup Name?</button>
    </div>
  )
}

export default HookUseState
