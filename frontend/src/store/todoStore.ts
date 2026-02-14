import {create} from 'zustand';
import {createJSONStorage, persist} from 'zustand/middleware';

import {STORAGE_KEYS} from '@/shared/constants'
import { Todo, TodoListItem } from '@/shared/types';

interface TodoStore {
    todos: Todo[];
    selectById: (id: number) => Todo | undefined;
    addTodo: (todo: Todo) => void;
    updateTodo : (todo: Todo) => void;
    deleteById : (id: number) => void;
    selectAll : () => Todo[];
}

const initialValues: Todo[] = [
    { id : 1, title : "Sample Todo", status : "Pending", registDate : "2025-02-06 17:30", deadline : "2025-02-10", description : "This is a sample"}
    , { id : 2, title : "Another Todo", status : "Pending", registDate : "2025-02-06 18:00", deadline : "2025-02-14", description : "This is another sample"}
    , { id : 3, title : "Yet Another Todo", status : "Pending", registDate : "2025-02-06 21:35", deadline : "2025-02-10", description : "This is yet another sample"}
];

const localTodoStore = create<TodoStore>()(
    persist(
        (set, get) => ({
            todos : initialValues,
            selectById : (id:number) => {
                return get().todos.find( todo => todo.id === id );
            },
            addTodo: (todo: Todo) => set( (state) => ({ todos: [...state.todos, todo] }) ),
            updateTodo : (updatedTodo: Todo) => set( (state) => ({
                todos: state.todos.map( todo => todo.id === updatedTodo.id ? updatedTodo : todo )
            }) ),
            deleteById : (id: number) => set( (state) => ({ todos: state.todos.filter( todo => todo.id !== id ) }) ),
            selectAll : () => {
                return get().todos;
            },
            init : () => {
                if( get().todos.length === 0 ) {
                    set( { todos: initialValues } )
                }
            }
        }),
        {
            name: STORAGE_KEYS.LOCAL_TODO
            , storage: createJSONStorage(() => localStorage)
            , version: 1
        }
    )
);

export default localTodoStore;