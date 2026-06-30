import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus, faPenToSquare, faTrash, faSearch, faDatabase} from '@fortawesome/free-solid-svg-icons'

import {useTodoListWithHook} from '@/features/todo/hooks/useTodo';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ROUTES, TODO_PRIORITY, TODO_PRIORITY_LABEL, TODO_STATUS, TODO_STATUS_LABEL } from '@/shared/constants';
import FrequentlyWordModal from './FrequentlyConditionModal';

export default function TodoListPaging() {

    const [isOpen, setIsOpen] = useState(false);

    const navigate = useNavigate();

    const [pageSize, setPageSize] = useState(10);

    const { todos, isLoading, deleteTodo, currentPage, totalPages, setCurrentPage, searchParam, setSearchParam, applySearch, resetSearch } = useTodoListWithHook(pageSize);

    const handleCreate = () => {
        navigate(`${ROUTES.TODOS}/create`);
    }

    const handleEdit = async (todoId : string) => {
        navigate(`/todos/${todoId}`);
    }

    const deleteHandle = async (todoId : string) => {
        if(confirm('정말 삭제하시겠습니까?')) {
            await deleteTodo(todoId);
        }
    }

    const getPageRange = (current: number, total: number) => {
        const delta = 2;
        const start = Math.max(1, current - delta);
        const end = Math.min(total, current + delta);
        return Array.from({ length: end - start + 1 }, (_, i) => start + i);
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
    else {
        
        return (
            <div className="container todo-list w-75">
                <h2 className="text-center my-4">My Todo List</h2>

                {/* 검색 영역 */}
                <div className="row g-2 mb-3">
                    <div className="col-auto">
                        <input 
                            type="text" 
                            className='form-control'
                            placeholder='Title 검색'
                            value={searchParam.title}
                            onChange={(e) => setSearchParam(prev => ({...prev, title : e.target.value}))}
                            onKeyDown={(e) => e.key === 'Enter' && applySearch()}
                        />
                    </div>

                    <div className="col-auto">
                        <select
                            className='form-control'
                            value={searchParam.priority}
                            onChange={(e) => setSearchParam(prev => ({...prev, priority : e.target.value}))}
                        >
                            <option value="">전체 Priority</option>
                            {Object.values(TODO_PRIORITY).map((p) => (
                                <option key={p} value={p}>
                                    {TODO_PRIORITY_LABEL[p]}
                                </option>
                            ))}

                        </select>
                    </div>
                    
                    <div className="col-auto">
                        <select
                            className='form-control'
                            value={searchParam.status}
                            onChange={(e) => setSearchParam(prev => ({...prev, status : e.target.value}))}
                        >
                            <option value="">전체 Status</option>
                            {Object.values(TODO_STATUS).map((p) => (
                                <option key={p} value={p}>
                                    {TODO_STATUS_LABEL[p]}
                                </option>
                            ))}
                        </select>
                    </div>
                    
                    <div className="col-auto">
                        <button className="btn" onClick = {() => setIsOpen(true)}>
                        <FontAwesomeIcon icon={faDatabase} /> 저장된 조건 조회
                        </button>
                    </div>

                    <div className="col-auto ms-auto">
                        <button className="btn btn-primary" onClick={applySearch}>
                        <FontAwesomeIcon icon={faSearch} /> 검색
                        </button>
                    </div>

                    <div className="col-auto">
                        <button className="btn btn-outline-secondary" onClick={resetSearch}>
                        초기화
                        </button>
                    </div>

                </div>
                {/* 검색 영역 */}


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
                                <tr key={todo.todoId} style={{ height: '20px' }} className="align-middle">
                                    <td>{(currentPage - 1) * pageSize + index + 1}</td>
                                    <td>{todo.priority}</td>
                                    <td>{todo.title}</td>
                                    <td>{todo.status}</td>          
                                    <td>{todo.deadline}</td>
                                    <td>
                                        <button className="btn btn-sm btn-outline-warning me-2" onClick={() => handleEdit(todo.todoId)}><FontAwesomeIcon icon={faPenToSquare} /> Edit</button>
                                        <button className="btn btn-sm btn-outline-danger" onClick={() => deleteHandle(todo.todoId)}><FontAwesomeIcon icon={faTrash} />Delete</button>
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

                { todos.length > 0 && 
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
                }
                <div className="text-end mt-4 me-3">
                    <button className="btn btn-primary" onClick={handleCreate}><FontAwesomeIcon icon={faPlus} />New Todo</button>
                </div>
                
                <FrequentlyWordModal 
                        isOpen={isOpen} 
                        onClose={() => setIsOpen(false)} 
                        onApply={(condition) => { setSearchParam(condition); }} 
                    />

            </div>
        )
    }

}