import { useEffect, useState } from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'
// import './App.css'
import Navbar from "./Navbar"
import DisplayPage from "./DisplayPage"
import LandingPage from "./LandingPage"
import ConfirmationPage from "./ConfirmationPage"
import { BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import Cookies from "js-cookie";
import SenderDisplay from "./SenderDisplay"

function App() {

 
  const BACKEND_URL = import.meta.env.VITE_BACKEND_HOST
   
  
  
 
  
 
  const handleLogin =  () => {
    // console.log(BACKEND_URL)
    // setTimeout(5)
    // window.location.href =  "http://127.0.0.1:5000/login"
    window.location.href = BACKEND_URL + "login"
  }

 document.title = "Email Viewer"

  return (
    
    <Router>
        <title>Email Viewer</title>
        <div className ="d-flex flex-column vw-100 vh-100 bg-dark text-white"> 
            <Navbar />
            <div className="d-flex flex-column  justify-content-center align-items-center" >
                <Routes>
                  <Route path = "/display" element = {
                    <DisplayPage />
                  
                  } />
                  

                  <Route path = "/login" element = {
                    <>
                    <button onClick={handleLogin}>Log in with Google</button>
                    <button onClick={() => console.log(Cookies.get("userHash"))}>check Cookie</button>
                    </>
                  } />
                  <Route exact path = "/" element = {

                    <LandingPage />
                  } />
                  <Route path = "/confirmation" element = {<ConfirmationPage />} />
                  
                  <Route path = "/overview" element = {<SenderDisplay />}/>
                    
                 
                </Routes>
                
                
              </div >
          </div>

    </Router>
    
  
  )

}
export default App
