import Cookies from "js-cookie"
import { useState, useEffect  } from "react"
import { useNavigate } from "react-router-dom"

function Navbar(props){
    const [cookie, setCookie] = useState(false)
    const navigate = useNavigate()
    // const CookieWatcher = ({ cookieName, children }) => {
    //     const [cookieValue, setCookieValue] = useState(Cookies.get(cookieName) || '');
      
    //     useEffect(() => {
    //       const checkCookieChange = () => {
    //         const newValue = Cookies.get(cookieName) || '';
    //         if (newValue !== cookieValue) {
    //           setCookieValue(newValue);
    //         }
    //       };
      
    //       const intervalId = setInterval(checkCookieChange, 1000);
      
    //       return () => clearInterval(intervalId);
    //     }, [cookieValue, cookieName]);
    useEffect( ()=> {
        let userCookie = Cookies.get("userHash")
        userCookie == undefined ? setCookie(false) : setCookie(true)


    }, [])
    const logoutUser = () => {
        Cookies.remove("userHash")
        setCookie(false)
    }
    return (
        <nav className = "navbar navbar-expand-lg text-white mb-4 mx-4 border-bottom d-flex justify-content-start">

            <div className = "d-flex align-items-center flex-grow-1">
                <a className ="navbar-brand text-white" href="#">Emailer</a>
                {cookie == false ? <a className="navbar-brand text-white">Not Logged in</a> 

                    :<>
                        <a className="navbar-brand text-white">Logged in</a>
                        <button onClick = {() => navigate("/display")}>Display Page</button>
                        <button onClick = {() => navigate("/overview")}>Sender Overview</button>
                    </>
                }
            </div>
            

            {cookie ? <div className = "ml-auto"> <button className ="navbar-brand text-white" onClick = {() => logoutUser()}>Logout</button></div> : <></>}
        </nav>
    )
    
}
export default Navbar