import { useState,useEffect } from "react";
import Cookies from "js-cookie"
import DisplayEmail from "./DisplayEmail"
import { useNavigate } from "react-router-dom";



const BACKEND_URL = import.meta.env.VITE_BACKEND_HOST

function DisplayPage(props) {
    let navigate = useNavigate()
    const [emailData, setEmailData] = useState([])
    const [pg, setPgNumber] = useState(0)
    const [pgMax, setPgMax] = useState(0)
    const [isLoading, setLoading] = useState(false)
    const [currentEmail, setCurrentEmail] = useState("")
    //TEST DATA FOR EMAIL
    let emailTest = []
    for (let i = 0; i < 49; i++){

        emailTest[i] = {"sender" : i % 5 == 0 ? "fiver " + i/5  : "saas", "date" : "0204-3", "subject" : "sases", 
        "snippet" :"snippet"
        }
    }

    const setEmailDataDemo = () => {
        setEmailDataWrap(emailTest)
    }
    // sets the data into pages
    const setEmailDataWrap = (data) => {
        console.log("setting")
        setEmailData(data['emails'])
        setCurrentEmail(data['userEmail'])
        setPgMax(Math.ceil(data['emails'].length / 5) -1)
        console.log(pgMax)
    }


    
      
    

    const getEmailWithHash = () =>{
        console.log("userhash is " + Cookies.get("userHash"))
        if (Cookies.get("userHash") == undefined) {
            return navigate("/login")
        }
        else{
            // console.log("data type" + typeof(Cookies.get("userHash")))
            // console.log("hash is " + Cookies.get('userHash'))
            setLoading(true)
            // console.log(Cookies.get("userHash").raw)
            let attempts = 0

            const attemptFetch = () => {
                fetch(`${BACKEND_URL}/emails/secure`, 
                    {   method : 'POST', 
                    body : JSON.stringify({"userHash" : Cookies.get("userHash")}),
                    headers: { "Content-Type" : "application/json"}})
                    .then(response => response.json())
                    .then(data => {
                        // setEmailDataWrap(data)

                        console.log(data)
                        if (data['emails'].length > 0) {
                            setEmailDataWrap(data)
                            setLoading(false)
                        } else {
                            throw new Error("No data Received")
                        }
                       
                    }).catch( error => {
                        console.log("fetch error: ", error)
                        attempts++
                        if (attempts < 5) {
                            setTimeout(attemptFetch, 5000)
                        } else {
                            console.log("max retry reached, fail")
                            setLoading(false)
                        }
                    })
            }
            
            attemptFetch()
        }
        
                
    
    }

    return (
        <>
            {currentEmail != "" ? <div>Displaying Email for {currentEmail} </div> : <div></div>}
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
            <button className = "btn btn-primary" onClick = {getEmailWithHash}>Reload Emails</button>
        </>
    )

}

export default DisplayPage