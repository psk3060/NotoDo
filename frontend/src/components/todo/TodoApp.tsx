import TodoList from "./TodoList";
import TodoForm from "./TodoForm";

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';


import { type PropsWithChildren } from "react";
import localAuthStore from "@/store/authStore";
import AuthProvider from "@/components/auth/AuthProvider";
import Header from "@/components/Header";
import Login from "@/components/auth/Login";

function AuthenticatedRoute({children}:PropsWithChildren) {

    const authStore = localAuthStore();
    
    if( authStore.isAuthenticated ) 
        return children;

    return <Navigate to="/" />;
}

export default function TodoApp() {

    return (
        <AuthProvider>
            <BrowserRouter>
                <Header />
                <Routes>
                    <Route path='/' element={ <Login /> }></Route>
                    <Route path='/login' element={<Login />}></Route>
                    <Route path='/todos' element={
                        <AuthenticatedRoute>
                            <TodoList />
                        </AuthenticatedRoute>}></Route>
                    <Route path='/todos/:id' element={
                        <AuthenticatedRoute>
                            <TodoForm />
                        </AuthenticatedRoute>}>
                    </Route>
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}