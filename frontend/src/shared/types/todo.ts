export interface Todo {
    todoId : string;
    title : string;
    status : string;
    registDate? : string;
    deadline : string;
    description : string;
    priority?:string;
    comments?: TodoComment[];
}

export interface TodoListItem {
    todoId : string;
    title : string; 
    registDate : string;
    status : string;
    deadline : string;
    priority?:string;
}

export interface TodoFormValues {
    title : string;
    deadline : string;
    registDate? : string;
    status : string;
    description : string;
    priority:string;
}

export interface CreateTodoPayload {
    title: string;
    status: string;
    deadline: string;
    description: string;
    priority:string;
}

export interface TodoComment {
    commentId? : string;
    todoId : string;
    author : string;
    commentText : string;
    lastModified? : string;
}

export interface UpdateTodoPayload extends Todo {}

export interface FrequentlyCondition {
    conditionId?:string;
    title? : string;
    priority? : string;
    status? : string;
}