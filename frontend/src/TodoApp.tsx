import TodoList from "./TodoList";
import TodoForm from "./TodoForm";

import { BrowserRouter, Routes, Route } from 'react-router-dom';

export default function TodoApp() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path='/' element={<TodoList />}></Route>
                <Route path='/todos/:id' element={<TodoForm />}></Route>
                <Route path='*' element={<TodoList />}></Route>
            </Routes>
        </BrowserRouter>
    );
}