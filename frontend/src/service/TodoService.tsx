import { Todo } from "../model/Todo";
import {ENV} from '../config/env';

import { mockResponse } from './mock';

import localTodoStore from "../store/localTodoStore";

import { apiClient } from "../config/ApiClient";
import { toast } from "react-toastify";

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


export async function withTokenCheck<T>(apiCall: () => Promise<T>, logout?: () => void): Promise<T | undefined> {
    
    try {
        return await apiCall();
    } catch (error: any) {
        const data = error.response?.data;
        if (!data) throw error;

        switch (data.code) {
            case "expired":
                try {
                    // 쿠키 기반 refresh token 요청
                    await apiClient.post('/auth/refresh');

                    // access token 재발급 후 원래 API 재시도
                    return await apiCall();
                } catch (refreshError) {
                    toast.error("재로그인이 필요합니다.");
                    if (logout) setTimeout(() => logout(), 100);
                }
                break;
            case "invalid":
            case "empty_token":
                toast.error("토큰이 유효하지 않거나 비어 있습니다. 재로그인 해주세요");
                if (logout) setTimeout(() => logout(), 100);
                break;

            default:
                throw error;
        }
    }
}