import { CreateTodoPayload, Todo, TodoComment, UpdateTodoPayload } from "@/shared/types";
import todoStore from "@/features/todo/stores/todoStore";
import { getCurrentTimestamp } from "@/shared/utils/date";
import { ENV } from "@/config/env";
import { API_ENDPOINTS } from "@/shared/constants";
import { apiClient } from "@/config/apiClient";
import {generateId} from "@/shared/utils/string";
import type {PagedResponse, SearchParam} from '@/shared/types'

export async function getAllTodos() : Promise<Todo[]> {
    if(ENV.IS_DEV) {
        return mockGetAllTodos();
    }

    const response = await apiClient.get<Todo[]>(API_ENDPOINTS.TODOS.BASE);
    return response.data;
}

export async function getAllTodosWithPaging(currentPage : number, pageSize : number, searchParam : SearchParam) : Promise<PagedResponse<Todo>> {
    if(ENV.IS_DEV) {
        return mockGetAllTodosWithPaging(currentPage, pageSize, searchParam);
    }

    const response = await apiClient.get<PagedResponse<Todo>>(API_ENDPOINTS.TODOS.BASE, {
        params: { pageSize, currentPage, ...searchParam }
    });

    return response.data;
}


export async function deleteTodo(id : string) : Promise<void> {
    if(ENV.IS_DEV) {
        return mockDeleteTodo(id);
    }

    await apiClient.delete(API_ENDPOINTS.TODOS.BY_ID(id));
}

export async function getTodoById(id : string) : Promise <Todo | null> {
    if(ENV.IS_DEV) {
        return mockGetTodoById(id);

    }

    const response = await apiClient.get<Todo>(API_ENDPOINTS.TODOS.BY_ID(id));
    return response.data;
}

export async function createTodo(payload : CreateTodoPayload) : Promise<void> {
    if(ENV.IS_DEV) {
        return mockCreateTodo(payload);
    }

    const todoData = {
        id : "",
        ...payload,
        registDate : getCurrentTimestamp(),
    };

    await apiClient.post(API_ENDPOINTS.TODOS.BASE, todoData);

}

export async function updateTodo(id:string, payload : UpdateTodoPayload) : Promise<void> {
    if( ENV.IS_DEV ) {
        return mockUpdateTodo(id, payload);
        
    }

    await apiClient.put(API_ENDPOINTS.TODOS.BY_ID(id), payload);
}

export async function createTodoComment(comment : TodoComment) : Promise<void> {

    if(ENV.IS_DEV) {
        mockCreateTodoComment(comment);
    }

    await apiClient.post(API_ENDPOINTS.TODOS.COMMENT(comment.todoId), comment);
}


function mockGetAllTodos() : Todo[] {
    return todoStore.getState().selectAll();
}

function mockGetAllTodosWithPaging(page : number, pageSize : number, searchParam : SearchParam) : PagedResponse<Todo> {
    let todos = todoStore.getState().selectAll();

    if(searchParam.title) {
        todos = todos.filter(todo => todo.title.includes(searchParam.title));
    }

    if(searchParam.priority) {
        todos = todos.filter(todo => todo.priority === searchParam.priority);
    }

    if(searchParam.status) {
        todos = todos.filter(todo => todo.status === searchParam.status);
    }

    const start = (page - 1) * pageSize;
    
    return {
        data: todos.slice(start, start + pageSize),
        total: todos.length,
        totalPages : Math.ceil((todos.length ?? 0) / pageSize)
    };
}

function mockGetTodoById(id : string) : Todo | null {
    return todoStore.getState().selectById(id) || null;
}

function mockCreateTodo(payload : CreateTodoPayload) : void {
    const store = todoStore.getState();
    
    const newTodo : Todo = {
        id: generateId(),
        ...payload,
        registDate : getCurrentTimestamp()
    };

    store.addTodo(newTodo);
}

function mockCreateTodoComment(comment : TodoComment) : void {
    const store = todoStore.getState();

    const newComment : TodoComment = {
        commentId : generateId(),
        todoId : comment.todoId,
        author : 'demo',
        commentText : comment.commentText,
        lastModified : getCurrentTimestamp()
    }

    store.addComment(newComment);
}


function mockUpdateTodo(id : string, payload : UpdateTodoPayload) : void {
    const store = todoStore.getState();
    const todo = store.selectById(id);

    if(todo) {
        const updatedTodo : Todo = {
            ...todo,
            ...payload,
        };

        store.updateTodo(updatedTodo);
    }
}

function mockDeleteTodo(id : string) : void {
    todoStore.getState().deleteById(id);
}