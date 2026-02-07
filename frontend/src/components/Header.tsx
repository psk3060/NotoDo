import { Link } from "react-router-dom";
import { useAuth } from "./auth/useAuth";
import localAuthStore from "../store/authStore";

export default function Header() {

    const authContext = useAuth();

    const authStore = localAuthStore();

    const {isAuthenticated} = authStore;

    return (
        <header className="border-bottom border-light border-5 mb-5 p-2 w-75">
            <div className="row">
                    <nav className="navbar navbar-expand-lg">
                        <div className="collapse navbar-collapse ">
                            <ul className="navbar-nav">
                                {
                                    isAuthenticated 
                                        && <li className="nav-item fs-5"><Link className="nav-link" to="/todos">Todos</Link></li> 
                                }
                            </ul>
                        </div>
                        <ul className="navbar-nav">
                            {
                                !isAuthenticated 
                                    && <li className="nav-item fs-5"><Link className="nav-link " to="/login">Login</Link></li> 
                            }
                            {
                                isAuthenticated 
                                    && <li className="nav-item fs-5"><Link className="nav-link" to="/logout" onClick={authContext.logout}>Logout</Link></li> 
                            }
                        </ul>
                    </nav>

                </div>
        </header>
    );
}