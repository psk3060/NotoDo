import { ROUTES, TOAST_MESSAGES } from "@/shared/constants";
import { useApiWithAuth } from "@/shared/hooks/useApiWithAuth";
import { useCallback, useEffect, useState } from "react";
import { toast } from "react-toastify";
import * as todoService from '@/features/todo/services/todoService';
import { CreateTodoPayload, Todo, TodoComment, UpdateTodoPayload } from "@/shared/types";
import { useNavigate } from "react-router-dom";


export function useTodoList() {

    const [todos, setTodos] = useState<Todo[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const {executeWithAuth} = useApiWithAuth();

    const fetchTodos = useCallback(async() => {
        setIsLoading(true);

        try {
            const data = await executeWithAuth(() => todoService.getAllTodos());

            if (data) {
                setTodos(data);
            }

        }
        catch(error) {
            console.error('Failed to fetch todos : ', error);
            toast.error(TOAST_MESSAGES.TODO.FETCH_ALL_FAIL);
        }
        finally {
            setIsLoading(false);
        }

    }, [executeWithAuth] );

    const deleteTodo = useCallback(async(id : string) => {
        try {
            await executeWithAuth(() => todoService.deleteTodo(id));
            toast.success(TOAST_MESSAGES.TODO.DELETE_SUCCESS);
            await fetchTodos();
        } catch(error) {
            console.error('Failed to delete todos : ', error);
            toast.error(TOAST_MESSAGES.TODO.DELETE_FAIL);
        }
    },[executeWithAuth, fetchTodos] )

    useEffect(() => { fetchTodos();}, [fetchTodos]);

    return {
        todos,
        isLoading,
        fetchTodos,
        deleteTodo
    }

}

export function useTodoDetail(id : string) {
    const [todo, setTodo] = useState<Todo | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const {executeWithAuth} = useApiWithAuth();
    const navigate = useNavigate();

    const fetchTodo = useCallback(async () => {
        if(id === '') {
            setTodo(null);
            return;
        }

        setIsLoading(true);

        try {
            const data = await executeWithAuth(() => todoService.getTodoById(id));

            if(data) {
                setTodo(data);
            }
        }
        catch(error) {
            console.error('Failed to fetch todo : ', error);
            toast.error(TOAST_MESSAGES.TODO.FETCH_FAIL);
        }
        finally {
            setIsLoading(false);
        }

    }, [id, executeWithAuth]);

    const createTodo = useCallback(
        async (payload : CreateTodoPayload) => {

            setIsLoading(true);

            try {
                await executeWithAuth(() => todoService.createTodo(payload));
                toast.success(TOAST_MESSAGES.TODO.CREATE_SUCCESS);
                navigate(ROUTES.TODOS);
            }
            catch(error) {
                console.error('Failed to create todo : ', error);
                toast.error(TOAST_MESSAGES.TODO.CREATE_FAIL);
                throw error;
            }
            finally {
                setIsLoading(false);
            }
        }
        , [executeWithAuth, navigate]
    );

    const updateTodo = useCallback(
        async(payload : UpdateTodoPayload) => {

            setIsLoading(true);

            try {
                await executeWithAuth(() => todoService.updateTodo(id, payload));
                toast.success(TOAST_MESSAGES.TODO.UPDATE_SUCCESS);
                navigate(ROUTES.TODOS);
            }
            catch(error) {
                console.error('Failed to update todo : ', error);
                toast.error(TOAST_MESSAGES.TODO.UPDATE_FAIL);
                throw error;
            }
            finally {
                setIsLoading(false);
            }

        }, [id, executeWithAuth, navigate]);
    
    const createComment = useCallback( 
        async (payload : TodoComment) => {

            setIsLoading(true);

            try {
                await executeWithAuth(() => todoService.createTodoComment(payload));
                toast.success(TOAST_MESSAGES.TODO.CREATE_COMMENT_SUCCESS);
                navigate(ROUTES.TODOS);
            }
            catch(error) {
                console.error('Failed to create todo : ', error);
                toast.error(TOAST_MESSAGES.TODO.CREATE_COMMENT_FAIL);
                throw error;
            }
            finally {
                setIsLoading(false);
            }
        }
        , [executeWithAuth, navigate]
    );
    
    useEffect(() => {fetchTodo(); }, [fetchTodo]);

    return {
        todo,
        isLoading,
        createComment,
        createTodo,
        updateTodo,
    }

}