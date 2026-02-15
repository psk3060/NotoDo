import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AuthProvider from "@/components/auth/AuthProvider";

import Header from "@/shared/components/Header";
import ProtectedRoute from "@/shared/components/ProtectedRoute";
import Login from "@/features/auth/components/Login";
import TodoList from "@/features/todo/components/TodoList";
import TodoForm from "@/features/todo/components/TodoForm";


export default function TodoApp() {

    return (
        <AuthProvider>
            <BrowserRouter>
                <Header />
                <Routes>
                    <Route path='/' element={ <Login /> }></Route>
                    <Route path='/login' element={<Login />}></Route>
                    <Route path='/todos' element={
                        <ProtectedRoute>
                            <TodoList />
                        </ProtectedRoute>}></Route>
                    <Route path='/todos/:id' element={
                        <ProtectedRoute>
                            <TodoForm />
                        </ProtectedRoute>}>
                    </Route>
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}