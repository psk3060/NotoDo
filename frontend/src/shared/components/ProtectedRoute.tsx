
import localAuthStore from "@/features/auth/stores/authStore";
import {  ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { ROUTES } from "@/shared/constants";

interface ProtectedRouteProps {
    children : ReactNode;
}

export default function ProtectedRoute({children}:ProtectedRouteProps) {

    const isAuthenticated = localAuthStore((state) => state.isAuthenticated);

    if( !isAuthenticated ) {
        return <Navigate to={ROUTES.LOGIN} replace />;
    }
    
    return children;
    
}