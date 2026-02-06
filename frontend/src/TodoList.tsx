import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus, faPenToSquare, faTrash} from '@fortawesome/free-solid-svg-icons'

import { useNavigate } from 'react-router-dom';

export default function TodoList() {

    // TODO : Python으로부터 실제 데이터 받아오기
    const todos = [
        { id: 1, title: "Sample Todo", registDate: "2025-02-06", status: "Pending", deadline: "2025-02-10", description : "This is a sample"},
        { id: 2, title: "Another Todo", registDate: "2025-02-06", status: "Completed", deadline: "2025-02-14", description : "This is another sample"},
        { id: 3, title: "Yet Another Todo", registDate: "2025-02-06", status: "In Progress", deadline: "2025-02-15", description : "This is yet another sample"},
    ];
    
    let navigate = useNavigate();

    function moveFormPage(id : number = 0){
        navigate(`/todos/${id}`);
    }

    return(
        <div className="container todo-list">
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
                                <button className="btn btn-sm btn-outline-danger"><FontAwesomeIcon icon={faTrash} />Delete</button>
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