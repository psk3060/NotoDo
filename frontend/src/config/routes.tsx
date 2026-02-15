
import TodoList from "@/features//todo/components/TodoList";
import Login from "@/features/auth/components/Login";
import TodoForm from "@/features/todo/components/TodoForm";
import ProtectedRoute from "@/shared/components/ProtectedRoute";
import { ROUTES } from "@/shared/constants";
import { ReactElement } from "react";


interface RouteConfig {
  path: string;
  element: ReactElement;
}

export const routes : RouteConfig[] = [
    { path : ROUTES.HOME, element : <Login /> }
    , { path : ROUTES.LOGIN, element : <Login /> }
    , { path : ROUTES.TODOS, element : (
        <ProtectedRoute>
            <TodoList />
        </ProtectedRoute>
    )}
    , { path : `${ROUTES.TODOS}/:id`, element : (
        <ProtectedRoute>
            <TodoForm />
        </ProtectedRoute>
    )}
]