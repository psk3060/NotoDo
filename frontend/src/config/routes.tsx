import Login from "@/features/auth/components/Login";
import TodoForm from "@/features/todo/components/TodoForm";
import TodoListPaging from "@/features/todo/components/TodoListPaging";
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
            <TodoListPaging />
        </ProtectedRoute>
    )}
    , { path : `${ROUTES.TODOS}/:id`, element : (
        <ProtectedRoute>
            <TodoForm />
        </ProtectedRoute>
    )}
]