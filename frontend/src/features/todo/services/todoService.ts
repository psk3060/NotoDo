import { CreateTodoPayload, Todo, TodoComment, UpdateTodoPayload, FrequentlyConditionDeleteRequest } from "@/shared/types";
import todoStore from "@/features/todo/stores/todoStore";
import { getCurrentTimestamp } from "@/shared/utils/date";
import { ENV } from "@/config/env";
import { API_ENDPOINTS } from "@/shared/constants";
import { apiClient } from "@/config/apiClient";
import {generateId} from "@/shared/utils/string";
import type {FrequentlyCondition, FrequentlyConditionResponse, PagedResponse, SearchParam} from '@/shared/types'

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


export async function deleteTodo(todoId : string) : Promise<void> {
    if(ENV.IS_DEV) {
        return mockDeleteTodo(todoId);
    }

    await apiClient.delete(API_ENDPOINTS.TODOS.BY_ID(todoId));
}

export async function getTodoById(todoId : string) : Promise <Todo | null> {
    if(ENV.IS_DEV) {
        return mockGetTodoById(todoId);

    }

    const response = await apiClient.get<Todo>(API_ENDPOINTS.TODOS.BY_ID(todoId));
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

export async function updateTodo(todoId:string, payload : UpdateTodoPayload) : Promise<void> {
    if( ENV.IS_DEV ) {
        return mockUpdateTodo(todoId, payload);
        
    }

    await apiClient.put(API_ENDPOINTS.TODOS.BY_ID(todoId), payload);
}

export async function createTodoComment(comment : TodoComment) : Promise<void> {

    if(ENV.IS_DEV) {
        mockCreateTodoComment(comment);
    }

    await apiClient.post(API_ENDPOINTS.TODOS.COMMENT(comment.todoId), comment);
}


export async function getFrequentlyUsedConditions() : Promise<FrequentlyConditionResponse<FrequentlyCondition>> {

    // TODO DEV 연동 
    
    if (ENV.IS_DEV) {
        return {
            data : mockGetAllConditionList()   
        }
    }
    
    const response = await apiClient.get<FrequentlyConditionResponse<FrequentlyCondition>>(API_ENDPOINTS.CONDITIONS.BASE);
    return response.data;

}

export async function deleteCondition(selectedIds : Set<string>) : Promise<void> {

    /*
    DEV 추가
    */

    await apiClient.delete(API_ENDPOINTS.CONDITIONS.BASE, {
        data: {
            ids: Array.from(selectedIds)
        }
    });
}


function mockGetAllConditionList() {
    return []
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

function mockGetTodoById(todoId : string) : Todo | null {
    return todoStore.getState().selectById(todoId) || null;
}

function mockCreateTodo(payload : CreateTodoPayload) : void {
    const store = todoStore.getState();
    
    const newTodo : Todo = {
        todoId: generateId(),
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


function mockUpdateTodo(todoId : string, payload : UpdateTodoPayload) : void {
    const store = todoStore.getState();
    const todo = store.selectById(todoId);

    if(todo) {
        const updatedTodo : Todo = {
            ...todo,
            ...payload,
        };

        store.updateTodo(updatedTodo);
    }
}

function mockDeleteTodo(todoId : string) : void {
    todoStore.getState().deleteById(todoId);
}


