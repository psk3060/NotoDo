import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus, faPenToSquare, faTrash} from '@fortawesome/free-solid-svg-icons'

import {useTodoList, useTodoListWithHook} from '@/features/todo/hooks/useTodo';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@/shared/constants';

export default function TodoListPaging() {
    
    const navigate = useNavigate();

    const [pageSize, setPageSize] = useState(3);

    const { todos, isLoading, deleteTodo, currentPage, totalPages, setCurrentPage } = useTodoListWithHook(pageSize);

    const handleCreate = () => {
        navigate(`${ROUTES.TODOS}/create`);
    }

    const handleEdit = async (id : string) => {
        navigate(`/todos/${id}`);
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

    const getPageRange = (current: number, total: number) => {
        const delta = 2;
        const start = Math.max(1, current - delta);
        const end = Math.min(total, current + delta);
        return Array.from({ length: end - start + 1 }, (_, i) => start + i);
    }

    return (
        <div className="container todo-list w-75">
            <h2 className="text-center my-4">My Todo List</h2>

            <table className="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">Priority</th>
                        <th scope="col">Title</th>
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
                            <tr key={todo.id} style={{ height: '20px' }} className="align-middle">
                                <td>{(currentPage - 1) * pageSize + index + 1}</td>
                                <td>{todo.priority}</td>
                                <td>{todo.title}</td>
                                <td>{todo.status}</td>          
                                <td>{todo.deadline}</td>
                                <td>
                                    <button className="btn btn-sm btn-outline-warning me-2" onClick={() => handleEdit(todo.id)}><FontAwesomeIcon icon={faPenToSquare} /> Edit</button>
                                    <button className="btn btn-sm btn-outline-danger" onClick={() => deleteHandle(todo.id)}><FontAwesomeIcon icon={faTrash} />Delete</button>
                                </td>
                            </tr>
                        ))
                    )}

                    {/* 빈 행으로 높이 채우기 */}
                    {
                        pageSize > todos.length &&
                            Array.from({ length: pageSize - todos.length }).map((_, i) => (
                                <tr key={`empty-${i}`} style={{ height: '30px', visibility: 'hidden' }} className="border-0">
                                    <td colSpan={6} className="border-0">&nbsp;</td>
                                </tr>
                            ))
                        }
                </tbody>
            </table>
            
            {/* 페이지네이션 */}
            <div className="d-flex justify-content-center mt-3">
                <ul className="pagination">
                    <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                        <button className="page-link" onClick={() => setCurrentPage(1)}>처음</button>
                    </li>
                    <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                        <button className="page-link" onClick={() => setCurrentPage(p => p - 1)}>이전</button>
                    </li>

                    {/* 앞 생략 */}
                    {getPageRange(currentPage, totalPages)[0] > 1 && (
                        <li className="page-item disabled">
                            <span className="page-link">...</span>
                        </li>
                    )}

                    {getPageRange(currentPage, totalPages).map(page => (
                        <li key={page} className={`page-item ${currentPage === page ? 'active' : ''}`}>
                            <button className="page-link" onClick={() => setCurrentPage(page)}>{page}</button>
                        </li>
                    ))}

                    {/* 뒤 생략 */}
                    {getPageRange(currentPage, totalPages).at(-1)! < totalPages && (
                        <li className="page-item disabled">
                            <span className="page-link">...</span>
                        </li>
                    )}

                    <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                        <button className="page-link" onClick={() => setCurrentPage(p => p + 1)}>다음</button>
                    </li>
                    <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                        <button className="page-link" onClick={() => setCurrentPage(totalPages)}>마지막</button>
                    </li>
                </ul>
            </div>

            <div className="text-end mt-4 me-3">
                <button className="btn btn-primary" onClick={handleCreate}><FontAwesomeIcon icon={faPlus} />New Todo</button>
            </div>
            
        </div>
    )
}