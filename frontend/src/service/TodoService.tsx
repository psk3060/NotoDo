import { Todo } from "../model/Todo";
import {ENV} from '../config/env';

import { mockResponse } from './mock';

import localTodoStore from "../store/localTodoStore";

import { apiClient } from "../config/ApiClient";

export async function retrieveAllTodos() {

    let result: any;
    
    if( ENV.IS_DEV ) {
        const todos = localTodoStore.getState().selectAll();

        result = mockResponse([...todos]);
    }
    else {
        // Server Retrieve
        result = apiClient.get('/todos');
    }
    
    

    return result;
}

export async function retrieveTodoById(id: number) : Promise<Todo | undefined> {

    let todo : any;
    
    if( ENV.IS_DEV ) {
        todo = mockResponse(localTodoStore.getState().selectById(id));
    }
    else {
        todo = apiClient.get(`/todos/${id}`);
        
    }

    return todo;
    
}

export async function createTodo(title: string, status: string, deadline: string, description : string) {

    let today = new Date();
        let registDate = today.getFullYear() + "-"
            + String(today.getMonth() + 1).padStart(2, '0') + "-"
            + String(today.getDate()).padStart(2, '0') + " "
            + String(today.getHours()).padStart(2, '0') + ":"
            + String(today.getMinutes()).padStart(2, '0');

    if( ENV.IS_DEV ) {
        
        // id = MaxID + 1
        let maxId = localTodoStore.getState().todos.reduce( (max, todo) => todo.id! > max ? todo.id! : max , 0) + 1;
        localTodoStore.getState().addTodo( new Todo(maxId, title, status, registDate, deadline, description) );
        
    }
    else {
        const todo = {
            id : 0
            , title
            , status
            , registDate
            , deadline
            , description
        };

        // Server Create
        apiClient.post(`/todos`, todo);
        
    }
    

    return mockResponse(true);
}

export async function deleteTodoById(id: number) {

    if( ENV.IS_DEV ) {
        localTodoStore.getState().deleteById(id);
    }
    else {
        apiClient.delete(`/todos/${id}`);
    }

    return mockResponse(true);
}   

export async function updateTodo(id: number, newTodo: Todo) {

    if( ENV.IS_DEV ) {
        // find by id and update
        const todo = localTodoStore.getState().selectById(id);

        todo!.title = newTodo.title;
        todo!.status = newTodo.status;
        todo!.deadline = newTodo.deadline;
        todo!.description = newTodo.description;

        localTodoStore.getState().updateTodo(todo!);
        
    }
    else {
        // Server Modify
        apiClient.put(`/todos/${id}`, newTodo);
        
    }
    
    return mockResponse(true);

}

