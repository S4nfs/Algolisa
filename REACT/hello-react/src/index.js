import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import App from './App'
import reportWebVitals from './reportWebVitals'
import { applyMiddleware, legacy_createStore as createStore } from 'redux'
import { Provider } from 'react-redux' //flows the data to whole application
import rootReducer from './services/reducers'
import logger from 'redux-logger'
import { RenderCountProvider } from './renderCounter'
// import { configureStore } from '@reduxjs/toolkit'

//get rootreducer data
const store = createStore(rootReducer, applyMiddleware(logger))
window.store = store

// console.warn(`store data : ${store}`)
const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
  <Provider store={store}>
    <RenderCountProvider>
      <App />
    </RenderCountProvider>
  </Provider>
)

reportWebVitals()
