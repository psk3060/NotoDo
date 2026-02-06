import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSave, faListOl } from '@fortawesome/free-solid-svg-icons'

import { useNavigate } from 'react-router-dom';

export default function TodoForm() {

  let navigate = useNavigate();

  function moveListPage() {
    navigate(`/todos`);
  } 

  return (
    <div className="container">
      <h2 className="text-center my-4">Todo Edit</h2>
      <form>
        <div className="form-group">
          <label htmlFor="todoTitle">Todo Title</label>
          <input type="text" className="form-control" id="todoTitle" placeholder="Enter todo title" />
        </div>

        <div className="form-group">
          <label htmlFor="todoDeadline">Todo Deadline</label>
          <input type="date" className="form-control" id="todoDeadline" placeholder="Enter todo deadline" />
        </div>

        <div className="form-group">
          <label htmlFor="todoStatus">Todo Status</label>
          <select className="form-control" id="todoStatus">
            <option value="Pending">Pending</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="todoDeadline">Todo Regist Date</label>
          <span className="form-control" id="todoRegDate">2025년 02월 06일 오후 9:10</span>
        </div>

        <div className="form-group">
          <label htmlFor="todoDescription">Todo Description</label>
          <textarea className="form-control" id="todoDescription" rows={3} placeholder="Enter todo description"></textarea>
        </div>
      
    </form>

      <div className="text-end mt-4 me-3">
        <button type="button" className="btn btn-primary me-2"><FontAwesomeIcon icon={faSave} /> Save Todo</button>
        <button type="button" className="btn btn-outline-secondary" onClick={moveListPage}><FontAwesomeIcon icon={faListOl} /> List Todo</button>
      </div>

    </div>

  );
}