import React from 'react'
import logo from './logo.svg'
import './App.css'
import { Header } from './components/1_Header'
import CHeader from './components/2_ClassHeader'
import Channel from './components/3_Channel'
import FunctionClick from './components/4_FunctionClick'
import CFunctionClick from './components/4_ClassFunctionClick'
import StateWithList from './components/5_StateWithList'
import Stylesheet from './components/6_Stylesheet'
import styles from './components/waiting.module.css' //css module (important filename)
import Form from './components/8_Form'
import Routing from './components/7_Routing'
import LifeCycleA from './components/9_LifeCycleA'
import ProductA from './components/10_ProductA'
import ProductB from './components/10_ProductB'
import GetAxios from './components/12_AxiosPost'
import PostAxios from './components/11_AxiosGet'
import HookUseState from './components/13_HookUseState'
import HookUseEffect from './components/14_HookUseEffect'
import HookObject from './components/15_HookObject'
import HookArray from './components/16_HookArray'
import MouseClass from './components/17_MouseClass'
import MouseFunction from './components/17_MouseFunction'
import AContextApi from './components/18_AContextApi'
import BContextApi from './components/18_BContextApi'
import CContextApi from './components/18_CContextApi'
import PersonA from './components/20_PersonA'
import PersonB from './components/20_PersonB'
import Test from './components/Test'
import FunctionContextA from './components/19_FunctionContextA'
import ReduxContainer from './containers/ReduxContainer'
import ReduxClassComponent from './components/22_ReduxClassComponent'
import UseMemoUseCallback from './components/23_UseMemo&UseCallback'
import UseRefHook from './components/24_UseRef'
import UseImperativeHandle from './components/25_UseImperativeHandle'
import UseTransition from './components/26_UseTransition'
import CustomHook from './components/27_CustomHook'
import { useEffect, useRef } from 'react'
import { useRenderCountContext } from './renderCounter'
import RenderTracker from './trackRerenderHook'
import React19 from './components/28_React19'
import UseOptimistic from './components/29_UseOptimistic'
//Componnets without jsx (Boooooring)
const withoutJSXformat = React.createElement('h1', { className: 'antiJSX' }, 'Complete React Application')
const withoutJSXformat2 = React.createElement('p', { className: 'antiJSXpara' }, 'Note: See console logs or press F12 to get more information')

//function App is itself an example of JSX format 😊
function App() {
  const { totalRenderCount } = useRenderCountContext()

  return (
    <div className='App'>
      {/* Fixed Re-render Widget */}
      <div className='rerender-widget'>
        <p>Total Re-renders: {totalRenderCount}</p>
      </div>
      <header className='App-header'>
        <img src={logo} className='App-logo' alt='logo' />

        {withoutJSXformat}
        {withoutJSXformat2}
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        {/* Functional component */}
        <Header name='Sagar'>
          <p>i am a full stack engineer and this is from children component</p>
        </Header>
        <Header name='Prateek' />
        <Header name='Anjali' />
        <Header name='Sanju' />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        {/* Class component */}
        <CHeader name='ClassSanju' />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>
        <RenderTracker>
          <Channel />
        </RenderTracker>

        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <FunctionClick />
        <CFunctionClick roll='22' />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <StateWithList />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <Stylesheet />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <Routing />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <h2 className={styles.wait}>Waiting .. Done</h2>
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <Form />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <LifeCycleA />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <ProductA />
        <ProductB />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <GetAxios />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <PostAxios />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <HookUseState />
        <HookUseEffect />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <HookObject />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <HookArray />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <MouseClass />
        <MouseFunction />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <AContextApi />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <FunctionContextA />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <PersonA />
        <PersonB />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <Test />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>
        <ReduxContainer />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>
        <ReduxClassComponent />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>
        {/* <TEST></TEST> */}
        <UseMemoUseCallback />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <UseRefHook />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <UseImperativeHandle />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <UseTransition />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <CustomHook />
        <h1 style={{ width: '100%', height: '1px', backgroundColor: 'grey' }}></h1>

        <React19 />
        <UseOptimistic />
        <a className='App-link' href='https://github.com/S4nfs' target='_blank' rel='noopener noreferrer' style={{ marginTop: '5rem' }}>
          Made By S4nfs
        </a>
      </header>
    </div>
  )
}

export default App
