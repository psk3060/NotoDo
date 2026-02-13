import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSave, faListOl } from '@fortawesome/free-solid-svg-icons'

import { useNavigate } from 'react-router-dom';

import {retrieveTodoById, updateTodo, withTokenCheck} from '../../service/TodoService';

import { ErrorMessage, Field, Form, Formik } from "formik";

import { useNumberParam } from '../../util/useNumberParam';

import {useEffect, useState} from 'react';
import { dateToString } from '../../util/useDateParam';

import { Todo } from '../../model/Todo';

import { createTodo } from '../../service/TodoService';

import moment from "moment";
import type TodoFormValues from '../../model/TodoFormValues';
import { useAuth } from '../auth/useAuth';

export default function TodoForm() {

  const { logout } = useAuth();

  let navigate = useNavigate();

  function moveListPage() {
    navigate(`/todos`);
  } 

  const [title, setTitle] = useState('');
  const [deadline, setDeadline] = useState('');
  const [status, setStatus] = useState('Pending');
  const [description, setDescription] = useState('');
  const [registDate, setRegistDate] = useState(new Date());
  
  const id = useNumberParam("id");

  useEffect( () => { retriegveTodo() }, [id]);

  
  function retriegveTodo() {
    if(id > 0) {
      retrieveTodoById(id)
        .then(
          (response: any) => {
            setTitle(response.data.title);
            setDeadline(response.data.deadline);
            setStatus(response.data.status);
            setDescription(response.data.description);
            setRegistDate(new Date(response.data.registDate));
            
          }
        )
        .catch( (error) => console.error(error) );
    }
    else {
      setRegistDate(new Date());
    }
    
  }
  

  let registDateStr = dateToString(registDate);
  
  function validate(values: TodoFormValues) {

    const errors: Partial<Record<keyof TodoFormValues, string | Date>> = {};

    if( values.title.length === 0 ) {
      errors.title = "title is required.";
    }

    if( values.deadline !== null && values.deadline !== '' ) {
      if( !moment(values.deadline).isValid() ) {
        errors.deadline = "Enter a deadline date";
      }

    }

    return errors;
  }


  async function onSubmit(values: TodoFormValues) {
    if( id === 0 ) {
      await withTokenCheck(
                  () => createTodo(
                          values.title
                          , values.status
                          , values.deadline
                          , values.description
                        ).then(() => { moveListPage();}).catch((error) => console.error(error)), 
                  () => ({ logout })
      )
    }
    else {
      await withTokenCheck(
                  () => updateTodo(id, new Todo(id, values.title, values.status, registDateStr, values.deadline, values.description))
                              .then(() => { moveListPage();})
                              .catch((error) => console.error(error))
                  , () => ({ logout })
      )
    }
  }




  return (
    <div className="container">
      <h2 className="text-center my-4">Todo Edit</h2>

      <Formik<TodoFormValues>
        initialValues={{ title, deadline, registDate : registDateStr, status, description }}
        enableReinitialize={true}
        onSubmit={onSubmit}
        validate={validate}  
        validateOnChange={false}
        validateOnBlur={false}
      >
        {(_) => (
          <Form>
            <ErrorMessage name="title" component="div" className="alert alert-warning" />
            <ErrorMessage name="deadline" component="div" className="alert alert-warning" />
            <ErrorMessage name="status" component="div" className="alert alert-warning" />
            
            <fieldset className="form-group">
              <label htmlFor="todoTitle">Todo Title</label>
              <Field type="text" className="form-control" id="todoTitle" name="title" placeholder="Enter todo title" />
            </fieldset>
            <fieldset className="form-group">
              <label htmlFor="todoDeadline">Todo Deadline</label>
              <Field type="date" className="form-control" id="todoDeadline" name="deadline" placeholder="Enter todo deadline" />
            </fieldset>

            <fieldset className="form-group">
              <label htmlFor="todoStatus">Todo Status</label>
              <Field as="select" className="form-control" id="todoStatus" name="status">
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
              </Field>
            </fieldset>

            <fieldset className="form-group">
              <label htmlFor="todoDeadline">Todo Regist Date</label>
              <Field type="text" className="form-control" id="todoRegDate" name="registDate" value={registDateStr} readOnly />
            </fieldset>
          
            <fieldset className="form-group">   
              <label htmlFor="todoDescription">Todo Description</label>
              <Field as="textarea" className="form-control" id="todoDescription" name="description" rows={3} placeholder="Enter todo description" />
            </fieldset>
            
            <div className="text-end mt-4 me-3">
              <button type="submit" className="btn btn-primary me-2"><FontAwesomeIcon icon={faSave} /> Save Todo</button>
              <button type="button" className="btn btn-outline-secondary" onClick={moveListPage}><FontAwesomeIcon icon={faListOl} /> List Todo</button>
            </div>

          </Form>
        )}
      </Formik>

    </div>

  );
}