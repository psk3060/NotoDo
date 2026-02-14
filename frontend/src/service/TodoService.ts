import { toast } from "react-toastify";

import {API_ENDPOINTS, ERROR_CODES, TOAST_MESSAGES} from '@/shared/constants';
import { ENV } from "@/config/env";
import localTodoStore from "@/store/todoStore";
import { mockResponse } from "./mock";
import { apiClient } from "@/config/ApiClient";

import { Todo, UpdateTodoPayload } from "@/shared/types";

export async function retrieveAllTodos() {
    let result: any;
    
    if( ENV.IS_DEV ) {
        const todos = localTodoStore.getState().selectAll();

        result = mockResponse([...todos]);
    }
    else {
        // Server Retrieve
        result = apiClient.get(API_ENDPOINTS.TODOS.BASE);
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
        localTodoStore.getState().addTodo( 
                                            {
                                                id : maxId
                                                , title
                                                , status
                                                , registDate
                                                , deadline
                                                , description
                                            }
        );
        
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
        apiClient.post(API_ENDPOINTS.TODOS.BASE, todo);
        
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

export async function updateTodo(id: number, newTodo: UpdateTodoPayload) {

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


export async function withTokenCheck<T>(fn: () => Promise<T>, logout: () => void): Promise<T | undefined> {
    
    try {
        return await fn();
    } catch (error: any) {
        const data = error.response?.data;
        if (!data) throw error;

        switch (data.code) {
            case ERROR_CODES.AUTH.TOKEN_EXPIRED:
                try {
                    // refresh token 갱신 요청
                    await apiClient.post(API_ENDPOINTS.AUTH.REFRESH);

                    // access token 재발급 후 원래 API 재시도
                    return await fn();
                } catch (refreshError) {
                    toast.error(TOAST_MESSAGES.AUTH.LOGIN_REQUIRED);
                    if (logout) {
                        try {
                            await logout();  // async 함수라면 await 필요
                        } catch(e) {
                            console.error("logout error:", e);
                        }
                    }
                }
                break;
            case ERROR_CODES.AUTH.TOKEN_INVALID:
            case ERROR_CODES.AUTH.TOKEN_EMPTY:
                toast.error(TOAST_MESSAGES.AUTH.INVALID_TOKEN);
                
                if (logout) {
                    try {
                        await logout();  // async 함수라면 await 필요
                    } catch(e) {
                        console.error("logout error:", e);
                    }
                }
                break;

            default:
                throw error;
        }
    }
}