import '@/styles/todoform.css'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSave, faListOl } from '@fortawesome/free-solid-svg-icons'

import { useNavigate } from 'react-router-dom';
import { ErrorMessage, Field, Form, Formik } from "formik";

import { TodoFormValues } from '@/shared/types';
import { isValidDate, toKSTString } from '@/shared/utils/date';
import { useStringParam } from '@/shared/hooks/useUrlParams';

import { useTodoDetail } from '../hooks/useTodo';
import { DEFAULT_TODO_PRIORITY, DEFAULT_TODO_STATUS, ROUTES, TODO_PRIORITY, TODO_PRIORITY_LABEL, TODO_STATUS, TODO_STATUS_LABEL } from '@/shared/constants';
import TodoReplyRegist from './TodoReplyRegist';
import TodoReplyList from './TodoReplyList';
import { toast } from 'react-toastify';


function validateTodoForm(values : TodoFormValues) {
  const errors: Partial<Record<keyof TodoFormValues, string | Date>> = {};

    if( !values.title.trim() ) {
      errors.title = "title is required.";
    }

    if( values.deadline && !isValidDate(values.deadline) ) {
      errors.deadline = "Enter a deadline date.";
    }

    return errors;
}

/**
 * Todo 생성 / 수정 폼 컴포넌트
 * @returns 
 */
export default function TodoForm() {

  let navigate = useNavigate();
  const id = useStringParam('id');
  const {todo, isLoading, createTodo, updateTodo, createComment} = useTodoDetail(id);
  
  const initialValues : TodoFormValues = {
    title : todo?.title || '',
    deadline : todo?.deadline || '',
    registDate : todo?.registDate || toKSTString(new Date()),
    status : todo?.status || DEFAULT_TODO_STATUS,
    description : todo?.description || '',
    priority : todo?.priority || DEFAULT_TODO_PRIORITY
  }

  const handleReplyRegist = async (author : string, commentText : string) => {

      try {
        if (id === 'create' || !todo) {
            throw Error('잘못된 접근입니다.');
        }

        await createComment({
          author : author,
          todoId : todo.id,
          commentText : commentText
        });

      }
      catch(error) {
        const message = error instanceof Error ? error.message : 'Unknown Error';
        toast.error(message); // alert → toast로 교체
      }
    };

  const handleCancel = () => {
    navigate(ROUTES.TODOS);
  }
  
  const handleSubmit = async (values : TodoFormValues) => {
    try {
      if(id === 'create') {
        await createTodo({
          title : values.title,
          status : values.status,
          deadline : values.deadline,
          description : values.description,
          priority:values.priority
        });
      }
      else {
        await updateTodo({
          id,
          title : values.title,
          status : values.status,
          registDate : values.registDate,
          deadline : values.deadline,
          description : values.description,
          priority:values.priority
        });
      }
    }
    catch(error) {
      console.error('Form submission error : ', error);
    }
  }

  if ( isLoading ) {
    return (
      <div className='container text-center mt-5'>
        <div className='spinner-border' role='status'>
          <span className='visually-hidden'>Loading...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <h2 className="text-center my-4">{id === 'create' ? 'Create Todo' : 'Edit Todo'}</h2>

      <Formik<TodoFormValues>
        initialValues={initialValues}
        enableReinitialize={true}
        onSubmit={handleSubmit}
        validate={validateTodoForm}  
        validateOnChange={false}
        validateOnBlur={false}
      >
        {({isSubmitting}) => (
          <Form>
            <ErrorMessage 
              name="title" 
              component="div" 
              className="alert alert-warning" 
            />
            <ErrorMessage 
              name="deadline" 
              component="div" 
              className="alert alert-warning" 
            />
            <ErrorMessage 
              name="status" 
              component="div" 
              className="alert alert-warning" 
            />
            
            <fieldset className="form-group">
              <label htmlFor="todoTitle">Todo Title</label>
              <Field 
                type="text" 
                className="form-control" 
                id="todoTitle" 
                name="title" 
                placeholder="Enter todo title" />
            </fieldset>

            <fieldset className="form-group">
              <label htmlFor="todoPriority">Todo Priority</label>
              <Field as="select" className="form-control" id="todoPriority" name="priority">
                {Object.values(TODO_PRIORITY).map((p) => (
                  <option key={p} value={p}>
                    {TODO_PRIORITY_LABEL[p]}
                  </option>
                ))}
              </Field>
            </fieldset>

            <fieldset className="form-group">
              <label htmlFor="todoDeadline">Todo Deadline</label>
              <Field 
                type="date" 
                className="form-control" 
                id="todoDeadline" 
                name="deadline" 
                placeholder="Enter todo deadline" />
            </fieldset>

            <fieldset className="form-group">
              <label htmlFor="todoStatus">Todo Status</label>
              <Field as="select" className="form-control" id="todoStatus" name="status">
                {Object.values(TODO_STATUS).map((p) => (
                  <option key={p} value={p}>
                    {TODO_STATUS_LABEL[p]}
                  </option>
                ))}
              </Field>
            </fieldset>

            <fieldset className="form-group">
              <label htmlFor="todoDeadline">Todo Regist Date</label>
              <Field 
                type="text" 
                className="form-control" 
                id="todoRegDate" 
                name="registDate" 
                readOnly />
            </fieldset>
          
            <fieldset className="form-group">   
              <label htmlFor="todoDescription">Todo Description</label>
              <Field 
                as="textarea" 
                className="form-control" 
                id="todoDescription" 
                name="description" 
                rows={3} 
                placeholder="Enter todo description" />
            </fieldset>
            
            <div className="text-end mt-4 me-3">
              <button 
                type="submit" 
                className="btn btn-primary me-2" 
                disabled={isSubmitting}>
                  <FontAwesomeIcon icon={faSave} /> Save Todo
              </button>
              <button 
                type="button" 
                className="btn btn-outline-secondary" 
                onClick={handleCancel} 
                disabled={isSubmitting}>
                  <FontAwesomeIcon icon={faListOl} /> List Todo
              </button>
            </div>

          </Form>
        )}

      </Formik>
      
      { (todo && todo.comments) && <TodoReplyList comments={todo.comments} /> }
      
      { todo && <TodoReplyRegist onRegist={handleReplyRegist} /> }
      
    </div>

  );
}