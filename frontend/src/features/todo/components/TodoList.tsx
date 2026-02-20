import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus, faPenToSquare, faTrash} from '@fortawesome/free-solid-svg-icons'

import { useNavigate } from 'react-router-dom';

import {useTodoList} from '@/features/todo/hooks/useTodo';
import { ROUTES } from '@/shared/constants';


export default function TodoList() {
    let navigate = useNavigate();
    const { todos, isLoading, deleteTodo } = useTodoList();

    const handleEdit = (id : string) => {
        navigate(`${ROUTES.TODOS}/${id}`);
    };

    const handleCreate = () => {
        navigate(`${ROUTES.TODOS}/create`);
    }

    const deleteHandle = async (id : string) => {
        if(confirm('정말 삭제하시겠습니까?')) {
            await deleteTodo(id);
        }
    }
    
    if (isLoading) {
        return (
        <div className="container text-center mt-5">
            <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
            </div>
        </div>
        );
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
                    {todos.length === 0 ? (
                        <tr>
                            <td colSpan={6} className="text-center">
                                등록된 Todo가 없습니다.
                            </td>
                        </tr>
                    ) : (
                        todos.map((todo, index) => (
                            <tr key={todo.id}>
                                <td>{index + 1}</td>
                                <td>{todo.title}</td>
                                <td>{todo.registDate}</td>
                                <td>{todo.status}</td>          
                                <td>{todo.deadline}</td>
                                <td>
                                    <button className="btn btn-sm btn-outline-warning me-2" onClick={() => handleEdit(todo.id)}><FontAwesomeIcon icon={faPenToSquare} /> Edit</button>
                                    <button className="btn btn-sm btn-outline-danger" onClick={() => deleteHandle(todo.id)}><FontAwesomeIcon icon={faTrash} />Delete</button>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
            
            <div className="text-end mt-4 me-3">
                <button className="btn btn-primary" onClick={handleCreate}><FontAwesomeIcon icon={faPlus} />New Todo</button>
            </div>
            
        </div>
    );
}