import { useState,useEffect } from "react";
import Cookies from "js-cookie"
import { useNavigate } from "react-router-dom";
import { Modal, Button } from "react-bootstrap"

function SenderDisplay(props) {
    //senders will contain a array of objects {sender : [emails]}
      // useEffect(() => {
        //   fetch("http://127.0.0.1:5000/api/data")
        //   .then(response => response.json())
        //   .then(data => {
        //     console.log(data)
            
        //     setEmailData(data)
        //   })
        
        //   .catch(error => {
        //     console.error("error fetching", error)
        //     setTimeout(getData, 500)
        //   })
            
        // }, [])
    
    const [topFive, setTopFive] = useState([])
    const [senderAnalysis, setAnalysis] = useState("")
    // const [currentSender, setSender] = useState("")
    const [showPopup, setPopupStatus] = useState(false)
    const [senders, setSenders] = useState([])
    const BACKEND_URL = import.meta.env.VITE_BACKEND_HOST
    
    const navigate = useNavigate()
    if (Cookies.get("userHash") == undefined) {
        return navigate("/login")
    }
    // pop the topFive (if there are 5 from the senders)
    let initAttempts = 0
    let max = 5

   
    const getSenders = () => {
        fetch(BACKEND_URL+ "overview", 
            {
                method:"POST",
                headers : {"Content-Type" : "application/json"},
                body : JSON.stringify({"userHash":Cookies.get("userHash")})
            }
        )
        .then(response => response.json())
        .then(data=> {
            console.log(data)
            const fetchedSenders = data['senders']
            setSenders(fetchedSenders)
            setTopFive(fetchedSenders.slice(0,5))

        }).catch(error => {
            console.log("error fetching", error)
            setTimeout(getSenders,5000)
        })
    }
    // can cause crashes
    // useEffect( () => getSenders(), [])
    
    //each element of firstFive is a list of email objects
    
    const formatText = (text) => {
            const replacements = [
                { regex: /\*\*(.*?)\*\*/g, replacement: '<strong>$1</strong>' },
                { regex: /\*(.*?)\*/g, replacement: '<em>$1</em>' },
                { regex: /([0-9]+)\./g, replacement: '<h3>$1.</h3>' },
                { regex: /\n/g, replacement: '<br />' },
                { regex: /•/g, replacement: '<li>' },
        ];
        let formattedText = text;

        replacements.forEach(({ regex, replacement }) => {
          formattedText = formattedText.replace(regex, replacement);
        });
      
        return formattedText;
    };
    const requestAnalysis = async (emails) => {
        console.log("requesting for ")
        console.log("emails")
        const result = await fetch( BACKEND_URL + "analysis",
        {
            method: "POST",
            headers : {
                'Content-Type' : 'application/json'
            },
            body: JSON.stringify({"emails" : emails, "userHash" : Cookies.get("userHash")})

        })
        const data = await result.json()
        if (result.status == 400) {
            console.log(data.error)
        }

        setAnalysis(formatText(data['analysis']))
        setPopupStatus(true)

    }

    const handleClose = () => {
        setAnalysis("")
        setPopupStatus(false)
    }

    return (
        <>
            <table className = "table">
                <Modal show = {showPopup} onHide = {handleClose}>
                    <Modal.Header closeButton>
                        <Modal.Title>Analysis</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <div dangerouslySetInnerHTML = {{ __html: senderAnalysis}}></div>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant = "primary" onClick = {handleClose}>Do Something</Button>
                    </Modal.Footer>
                </Modal>
                <thead>
                    <tr>
                        <th scope = "col">Rank</th>
                        <th scope = "col">Sender</th>
                        <th scope = "col">Count</th>
                        <th scope = "col">Analysis</th>
                    </tr>
                </thead>
                <tbody>
                    {topFive.map((obj, index) => {
                        return (
                            <tr key = {obj['sender']}>
                                <td>{index}</td>
                                <td>{obj['sender']}</td>
                                <td>No. of emails {obj['emails'].length}</td>
                                <td><button onClick={() => requestAnalysis(obj['emails'])}>Get analysis</button></td>
                            </tr>
                        )
                    })}
                    
                </tbody>
            </table>
            <button onClick ={getSenders}>Get Senders</button>
        </>
        
    )
    

}

export default SenderDisplay