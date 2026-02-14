import {create} from 'zustand';
import {createJSONStorage, persist} from 'zustand/middleware';

import {STORAGE_KEYS} from '@/shared/constants'
import { Todo } from '@/model/Todo';

interface TodoStore {
    todos: Todo[];
    selectById: (id: number) => Todo | undefined;
    addTodo: (todo: Todo) => void;
    updateTodo : (todo: Todo) => void;
    deleteById : (id: number) => void;
    selectAll : () => Todo[];
}

const initialValues: Todo[] = [
    new Todo(1, "Sample Todo", "Pending", "2025-02-06 17:30", "2025-02-10", "This is a sample"),       
    new Todo(2, "Another Todo", "Pending", "2025-02-06 18:00", "2025-02-14", "This is another sample"),
    new Todo(3, "Yet Another Todo", "Pending", "2025-02-06 21:35", "2025-02-10", "This is yet another sample")
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