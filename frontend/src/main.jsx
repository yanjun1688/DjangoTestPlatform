import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
// Remove Bootstrap CSS import
// import 'bootstrap/dist/css/bootstrap.min.css'
// Add Ant Design CSS import
import 'antd/dist/reset.css'; // Use reset.css for modern projects

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
