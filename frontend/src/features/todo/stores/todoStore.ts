import {create} from 'zustand';
import {createJSONStorage, persist} from 'zustand/middleware';

import {STORAGE_KEYS} from '@/shared/constants'
import { Todo } from '@/shared/types';
import { TodoComment } from '../../../shared/types/todo';

interface TodoStore {
    todos: Todo[];
    addTodo: (todo: Todo) => void;
    updateTodo : (todo: Todo) => void;
    deleteById : (id: string) => void;
    selectAll : () => Todo[];
    selectById: (id: string) => Todo | undefined;
    addComment : (comment : TodoComment) => void;
}

const initialValues: Todo[] = [
    { id : "1", title : "Sample Todo", status : "Pending", registDate : "2025-02-06 17:30", deadline : "2025-02-10", description : "This is a sample", comments : []}
    , { id : "2", title : "Another Todo", status : "Pending", registDate : "2025-02-06 18:00", deadline : "2025-02-14", description : "This is another sample", comments : []}
    , { id : "3", title : "Yet Another Todo", status : "Pending", registDate : "2025-02-06 21:35", deadline : "2025-02-10", description : "This is yet another sample", comments : []}
];

/**
 * Todo 상태 관리 스토어(개발 모드 전용)
 */
const localTodoStore = create<TodoStore>()(
    persist(
        (set, get) => ({
            todos : initialValues,
            addTodo: (todo: Todo) => {
                set((state) => ({ 
                    todos: [...state.todos, todo] 
                }));
            },

            updateTodo : (todo: Todo) => {
                set( (state) => ({
                    todos: state.todos.map( (t) => t.id === todo.id ? todo : t ),
                }));
            },
            
            deleteById : (id: string) => {
                set( (state) => ({ 
                    todos: state.todos.filter( (todo) => todo.id !== id ) 
                }));
            },
            selectAll : () => {
                return get().todos;
            },

            selectById : (id:string) => {
                return get().todos.find( (todo) => todo.id === id );
            }, 
            addComment : (comment : TodoComment ) => {
                set((state) => ({
                    
                }))
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