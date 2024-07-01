import { useEffect, useState } from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'
// import './App.css'
import Navbar from "./Navbar"
import DisplayEmail from "./DisplayEmail"

function App() {

  const [emailData, setEmailData] = useState([])
  const [pg, setPgNumber] = useState(0)
  const [pgMax, setPgMax] = useState(0)
  //gets email data on loadup
  // useEffect(() => {
  //   getEmailDataBasic()
  // }, [])
  const setEmailDataWrap = (data) => {
    console.log("setting")
    setEmailData(data)
    setPgMax(Math.ceil(data.length / 5) -1)
    console.log(pgMax)
  }
  const getTestData = () => {
    fetch("http://127.0.0.1:5000/test/nothing")
    .then(response => response.json())
    .then(data => {
      console.log("received")
      console.log(data)
      console.log("test ok")
      setEmailData(data)
    }).catch(error => {
      console.log("error fetching", error)
      setTimeout(getTestData, 500)
    })
  }
  
  
  let emailTest = []
  for (let i = 0; i < 49; i++){

    emailTest[i] = {"sender" : i % 5 == 0 ? "fiver " + i/5  : "saas", "date" : "0204-3", "subject" : "sases", 
      "snippet" :"snippet"
     }
  }
  const setEmailDataDemo = () => {
    setEmailDataWrap(emailTest)
  }
  
  const getEmailDataBasic = () => {
    fetch("http://127.0.0.1:5000/plain/data")
    .then(response => response.json())
    .then(data => {
      console.log("received")
      console.log(data)
      setEmailDataWrap(data)
    }).catch(error => {
      console.log("error fetching", error)
      setTimeout(getEmailDataBasic, 500)
    })
  }

  let isLoading = false

  

  return (
    <div className ="d-flex flex-column vh-100 bg-dark text-white"> 
      <Navbar />
      <div className="d-flex flex-column  justify-content-center align-items-center" >
          
          <div>
            <ul className = "pagination">
                {pg > 0 ? <li onClick = {() => setPgNumber(pg - 1)} className = "page-item"><a className = "page-link" href ="#">Previous</a></li> : <li  className = "page-item disabled"><a className = "page-link" href ="#">Previous</a></li>}
                {pg > 0 ? <li onClick = {() => setPgNumber(pg - 1)} className = "page-item"><a className = "page-link" href ="#">{pg}</a></li> : <></>} 
                <li className = "page-item active"><a className = "page-link" href ="#">{pg + 1}</a></li>
                {pg < pgMax ? <li onClick = {() => setPgNumber(pg + 1)} className = "page-item"><a className = "page-link" href ="#">{pg + 2}</a></li> : <></>}
                {pg < pgMax ? <li onClick = {() => setPgNumber(pg + 1)} className = "page-item"><a className = "page-link" href ="#">Next</a></li> : <li  className = "page-item"><a className = "page-link disabled" href ="#">Next</a></li>}
            </ul>
            {emailData ? <DisplayEmail emailData = {emailData} pg = {pg}/> : <p>Not received</p>}
            
            
            {isLoading ? <p>Loading</p> : <p>not loading</p>}
            <button className = "btn btn-primary" onClick = {setEmailDataDemo}>testButton</button>
            <button className = "btn btn-primary" onClick = {getEmailDataBasic}>getData</button>
            <button className ="btn btn-primary" onClick = {() => setLoading(!isLoading)}>Display Email</button>
          </div>
          
        </div >
    </div>
  
  )
}

export default App
