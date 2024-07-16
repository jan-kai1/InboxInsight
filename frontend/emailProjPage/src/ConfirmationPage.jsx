import React from "react";
import Cookies from "js-cookie"
import {  useNavigate, useLocation } from "react-router-dom"
import { useEffect,useState } from "react";


function ConfirmationPage() {
    const navigate = useNavigate()
    const [userHash, setUserHash] = useState(null)

    const storeUserHash = (newHash) => {
        setUserHash(newHash)
        Cookies.set("userHash", newHash, { expires : 5, sameSite: "lax" })
    }
    useEffect(() => {
        const queryParams = new URLSearchParams(location.search)
        
        
        let newHash = queryParams.get('userHash')
        if (newHash) {
            storeUserHash(newHash)
         
            navigate("/display")
        }

        

    }, [location])
    return (
        <>
            <h1>Retrieving Data</h1>
            {userHash ? <div>Data Found, Redirecting</div> : <div></div>}
        </>
    )

}

export default ConfirmationPage