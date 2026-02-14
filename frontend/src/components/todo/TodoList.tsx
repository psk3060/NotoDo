import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus, faPenToSquare, faTrash} from '@fortawesome/free-solid-svg-icons'

import { useNavigate } from 'react-router-dom';

import { deleteTodoById, retrieveAllTodos, withTokenCheck } from '../../service/TodoService';

import { useState, useEffect } from 'react';

import { Todo } from '../../model/Todo';
import { useAuth } from '../auth/useAuth';

export default function TodoList() {
    const { logout } = useAuth();
    
    const [todos, setTodos] = useState<Todo[]>([]);

    let navigate = useNavigate();

    function moveFormPage(id : number = 0){
        navigate(`/todos/${id}`);
    }

    useEffect( () => {refreshTodos();}, [] );    

    async function refreshTodos()  { 

        await withTokenCheck(
            () => retrieveAllTodos().then(
                response => {
                    setTodos(response.data);
                }
            ), logout
        )
    }
    
    async function deleteTodo(id: number) {
        await withTokenCheck(
            () => deleteTodoById(id).then( () => {
                refreshTodos();
            })
            , logout
        )

    }

    return(
        <div className="container todo-list w-75">
            <h2 className="text-center my-4">My Todo List</h2>

            <table className="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">Title</th>
                        <th scope="col">RegistDate</th>
                        <th scope="col">Status</th>
                        <th scope="col">Deadline</th>
                        <th scope="col">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {todos.map((todo, index) => (
                        <tr key={todo.id}>
                            <td>{index + 1}</td>
                            <td>{todo.title}</td>
                            <td>{todo.registDate}</td>
                            <td>{todo.status}</td>          
                            <td>{todo.deadline}</td>
                            <td>
                                <button className="btn btn-sm btn-outline-warning me-2" onClick={() => moveFormPage(todo.id)}><FontAwesomeIcon icon={faPenToSquare} /> Edit</button>
                                <button className="btn btn-sm btn-outline-danger" onClick={() => deleteTodo(todo.id)}><FontAwesomeIcon icon={faTrash} />Delete</button>
                            </td>
                        </tr>
                    ))}   
                </tbody>
            </table>
            
            <div className="text-end mt-4 me-3">
                <button className="btn btn-primary" onClick={() => moveFormPage(0)}><FontAwesomeIcon icon={faPlus} />New Todo</button>
            </div>
            
        </div>
    );
}