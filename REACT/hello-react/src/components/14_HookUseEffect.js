import React, { useState, useEffect } from 'react'
import { useRenderCountContext } from '../renderCounter'

function HookUseEffect() {
  const renderCount = useRenderCountContext()

  //classic approach
  // const startup = useState("Facebook")
  // const clickIt = () => {
  //     startup[1]("Meta")
  // }

  //modern approach, huh!😒 it's just normal destructuring
  const [startup, newstartup] = useState('Facebook') //second index is the function name----.
  const clickIt = () => {
    //                                     |
    newstartup('Meta') //       <<---------------------------'
  }

  const [investors, addinvestors] = useState(0)
  const [founders, addfounders] = useState(0)
  const [shareprice, termsheet] = useState(0)

  const Increment = () => {
    addinvestors(investors + 1)
  }
  const Decrement = () => {
    console.log(founders) //u'll see previous values
    addfounders(founders - 1)
  }

  const ShareIncr = () => {
    for (let i = 0; i < 10; i++) {
      termsheet((shareprice) => shareprice + 1) //useState with previous state a.k.a retain values and increment by 10
    }
  }

  useEffect(() => {
    //useEffect is similer to componentDidUpdate as it renders the updated
    console.log(`Founders has been changed to ${founders}`)
  }, [founders]) //you might not want to run the effect on every change taking place in DOM, so array parameter tells which component you want to hit after update, empty array == componentDidMount

  return (
    <div>
      {startup}
      <button onClick={clickIt}> Change Startup Name?</button>
      <button onClick={Increment}> Investors {investors}</button>
      <button onClick={Decrement}> Founders {founders}</button>
      <button onClick={ShareIncr}> Share Price {shareprice}</button>
    </div>
  )
}

export default HookUseEffect
