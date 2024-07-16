import { useState } from "react";
import Cookies from "js-cookie"
import {BrowserRouter as Router, Route, Routes} from "react-router-dom"
import { useNavigate } from "react-router-dom";
import 'bootstrap/dist/css/bootstrap.min.css'
import { redirect } from "react-router-dom";

function LandingPage() {
    
    let navigate = useNavigate()
   
    const routeChange = (path) =>{ 
         
        navigate(path);
    }
    const testCook = () => {
        console.log(Cookies.get("sigma"))
        console.log(Cookies.get("sigma") == undefined)
    }
    return (
        <>
            <div>Welcome</div>
            <button onClick = {() => routeChange("/login")}>Login</button>
            <button onClick = {() => routeChange("/display")}> Display Email</button>
            <button onClick = {() => testCook()}>Check default cookie value</button>
        </>
        
    )
    
}
export default LandingPage