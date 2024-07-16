import { useEffect, useState } from "react"
import 'bootstrap/dist/css/bootstrap.min.css';
import { Modal, Button } from "react-bootstrap"
function DisplayEmail({emailData, pg = 0}) {
    //each page is 5 emails
    
    const BACKEND_URL = import.meta.env.VITE_BACKEND_HOST

    const [summaryText, setSummaryText] = useState("")
    const [showPopup, setPopupStatus] = useState(false)
    const handleClose = () => {
        setSummaryText("")
        setPopupStatus(false)
    }

    
    let toDisplay = emailData.slice(pg * 5, pg*5 + 5)
    
    const getSummary = async (text) => {
        if (text == null) {
            setSummaryText("Summary not available for this email")
            setPopupStatus(true)
            return 
        }
        console.log(text)
        const res = await fetch( BACKEND_URL + "summary/get" ,{
            method : "POST",
            headers : {
                'Content-Type' : 'application/json'
            },
            body: JSON.stringify({"text" :  text})
        })
        const data = await res.json()
        if (res.status == 400) {
            console.log(data.error)
        }
        
        console.log(data.summary)
        setSummaryText(data.summary)
        setPopupStatus(true)

    }
    return (
        <table className = "table">
            <Modal show={summaryText} onHide={handleClose}>
                <Modal.Header closeButton>
                <Modal.Title>Summary</Modal.Title>
                </Modal.Header>
                <Modal.Body>{summaryText}</Modal.Body>
                <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    Close
                </Button>
                <Button variant="primary" onClick={handleClose}>
                    Write A Reply
                </Button>
                </Modal.Footer>
            </Modal>
            <thead>
                <tr>
                    <th scope ="col">From</th>
                    <th scope = "col">Date</th>
                    <th scope = "col">Subject</th>
                    <th scope = "col">Preview</th>
                    <th scope = "col">Summary</th>
                </tr>
            </thead>
            <tbody>
                {toDisplay.map(email =>(
                
                    <tr key = {email.sender + email.date}>
                        <td>{email.sender}</td>
                        <td>{email.date}</td>
                        <td>{email.subject}</td>
                        <td>{email.snippet}</td>
                        <td><button onClick = {() => getSummary(email.plain)}>Get Summary</button></td>
                    </tr>
                    
                    )

                )}
            </tbody>
        </table>

    )
}

export default DisplayEmail