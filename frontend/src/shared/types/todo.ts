export interface Todo {
    id : number;
    title : string;
    status : string;
    registDate? : string;
    deadline : string;
    description : string;
}

export interface TodoListItem {
    id : number;
    title : string; 
    registDate : string;
    status : string;
    deadline : string;
}

export interface TodoFormValues {
    title : string;
    deadline : string;
    registDate? : string;
    status : string;
    description : string;
}

export interface UpdateTodoPayload extends Todo {}