import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from '@/features/auth/hooks/useAuth';
import { ROUTES } from "@/shared/constants";

export default function Header() {

    const navigate = useNavigate();
    const location = useLocation();
    const {userId, isAuthenticated, logout} = useAuth()

    const handleLogout = async () => {
        await logout();
    }
    
    if( location.pathname === ROUTES.LOGIN || location.pathname === ROUTES.HOME ) {
        return null;

    }

    return (
        <header className="bg-dark text-white py-3 mb-4">
            <div className="container d-flex justify-content-between align-items-center">
                <h1 
                    className="h4 mb-0 cursor-pointer"
                    onClick={() => navigate(ROUTES.TODOS)}
                    style={{ cursor : 'pointer' }}
                    >
                    Todo App
                </h1>

                {
                    isAuthenticated && (
                        <div className="d-flex align-items-center gap-3">
                            <span>Welcome, {userId} !</span>
                            <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
                                Logout
                            </button>
                        </div>
                    )
                }

            </div>
        </header>
    );

}