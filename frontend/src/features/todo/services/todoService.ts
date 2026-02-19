import { CreateTodoPayload, Todo, UpdateTodoPayload } from "@/shared/types";
import todoStore from "@/features/todo/stores/todoStore";
import { getCurrentTimestamp } from "@/shared/utils/date";
import { ENV } from "@/config/env";
import { API_ENDPOINTS } from "@/shared/constants";
import { apiClient } from "@/config/apiClient";

export async function getAllTodos() : Promise<Todo[]> {
    if(ENV.IS_DEV) {
        return mockGetAllTodos();
    }

    const response = await apiClient.get<Todo[]>(API_ENDPOINTS.TODOS.BASE);
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
        id : 0,
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

function mockGetAllTodos() : Todo[] {
    return todoStore.getState().selectAll();
}

function mockGetTodoById(id : string) : Todo | null {
    return todoStore.getState().selectById(id) || null;
}

function mockCreateTodo(payload : CreateTodoPayload) : void {
    const store = todoStore.getState();
    const maxId = store.todos.reduce((max, todo) => Math.max(max, todo.id), 0);

    const newTodo : Todo = {
        id : maxId + 1,
        ...payload,
        registDate : getCurrentTimestamp()
    };

    store.addTodo(newTodo);
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