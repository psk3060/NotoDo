export interface Todo {
    id : string;
    title : string;
    status : string;
    registDate? : string;
    deadline : string;
    description : string;
    priority:string;
}

export interface TodoListItem {
    id : string;
    title : string; 
    registDate : string;
    status : string;
    deadline : string;
    priority:string;
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

export interface UpdateTodoPayload extends Todo {}