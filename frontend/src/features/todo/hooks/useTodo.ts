import { ROUTES, TOAST_MESSAGES } from "@/shared/constants";
import { useApiWithAuth } from "@/shared/hooks/useApiWithAuth";
import { useCallback, useEffect, useState } from "react";
import { toast } from "react-toastify";
import * as todoService from '@/features/todo/services/todoService';
import { CreateTodoPayload, PagedResponse, Todo, TodoComment, UpdateTodoPayload } from "@/shared/types";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";


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

    // 컴포넌트 마운트 할 때마다 fetch
    useEffect(() => { fetchTodos();}, [fetchTodos]);

    return {
        todos,
        isLoading,
        deleteTodo
    }

}


export function useTodoListWithHook(pageSize : number) {

    const [currentPage, setCurrentPage] = useState(1);

    const {executeWithAuth} = useApiWithAuth();
    const queryClient = useQueryClient();

    // pageSize 바뀌면 1페이지로 초기화
    useEffect(() => { setCurrentPage(1);}, [pageSize]);

    const {data, isLoading : isFetching} = useQuery({
        queryKey : ['todos', currentPage, pageSize],
        queryFn: () => executeWithAuth(() => todoService.getAllTodosWithPaging(currentPage, pageSize)),
        throwOnError: () => {
            toast.error(TOAST_MESSAGES.TODO.FETCH_ALL_FAIL);
            return false;
        },
        placeholderData : (prev) => prev,
        refetchOnWindowFocus: false,
    });

    const todos = data?.data ?? [];
    const totalPages = data?.totalPages ?? 0;

    const {mutate : deleteTodo, isPending: isDeleting} = useMutation({
        mutationFn : (id : string) => executeWithAuth(() => todoService.deleteTodo(id)),
        // Error Boundry
        throwOnError: true,
        onSuccess : () => {
            toast.success(TOAST_MESSAGES.TODO.DELETE_SUCCESS);
            
            queryClient.invalidateQueries({ queryKey: ['todos'] }); 
            // 삭제 시 첫 번째 페이지
            setCurrentPage(1);

        },
        onError : (_) => {
            toast.error(TOAST_MESSAGES.TODO.DELETE_FAIL);
        }
    });

    const isLoading = isFetching || isDeleting;

    return {
        todos,
        isLoading,
        currentPage,
        setCurrentPage,
        totalPages,
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
                console.error('Failed to create comment : ', error);
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


export function useTodoDetailHook(id : string) {
    const queryClient = useQueryClient();
    
    const {executeWithAuth} = useApiWithAuth();
    const navigate = useNavigate();

    const [isCommenting, setIsCommenting] = useState(false);

    const { data : todo, isLoading: isFetching } = useQuery({
        queryKey : ['todo', id],
        queryFn : () => executeWithAuth(() => todoService.getTodoById(id)),
        staleTime: 0,
        refetchOnMount: true,
        refetchOnWindowFocus: false,
    });

    const {mutate : createTodo, isPending : isCreating}  = useMutation({
        mutationFn : (payload : CreateTodoPayload) => executeWithAuth(() => todoService.createTodo(payload)),
        throwOnError: true,
        onSuccess : () => {
            toast.success(TOAST_MESSAGES.TODO.CREATE_SUCCESS);
            queryClient.invalidateQueries({ queryKey: ['todos'] });
            navigate(ROUTES.TODOS);
        },
        onError : (_) => {
            toast.error(TOAST_MESSAGES.TODO.CREATE_FAIL);
        }
    });

    const {mutate : updateTodo, isPending : isUpdating} = useMutation({
        mutationFn : (payload : UpdateTodoPayload) => executeWithAuth(() => todoService.updateTodo(id, payload)),
        throwOnError: true,
        onSuccess : () => {
            toast.success(TOAST_MESSAGES.TODO.UPDATE_SUCCESS);
            queryClient.invalidateQueries({ queryKey: ['todos'] });
            navigate(ROUTES.TODOS);
        },
        onError : (_) => {
            toast.error(TOAST_MESSAGES.TODO.UPDATE_FAIL);
        }

    });

    const createComment = useCallback(
        async (payload : TodoComment) => {
            setIsCommenting(true);

            try {
                await executeWithAuth(() => todoService.createTodoComment(payload));
                toast.success(TOAST_MESSAGES.TODO.CREATE_COMMENT_SUCCESS);
                navigate(ROUTES.TODOS);
            }
            catch(error) {
                console.error('Failed to create comment : ', error);
                toast.error(TOAST_MESSAGES.TODO.CREATE_COMMENT_FAIL);
                throw error;
            }
            finally {
                setIsCommenting(false);
            }

        }
    , [executeWithAuth, navigate]);

    const isLoading = isFetching || isCreating || isUpdating || isCommenting;
    
    return {
        todo,
        isLoading,
        createTodo,
        updateTodo,
        createComment
    }
    

}