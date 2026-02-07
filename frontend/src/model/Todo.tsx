export class Todo {
    id: number;
    title: string;
    status: string;
    registDate: string;
    deadline: string;
    description : string;

    constructor(id: number, title: string, status: string, registDate: string, deadline: string, description: string) {
        this.id = id;
        this.title = title;
        this.status = status;
        this.registDate = registDate;
        this.deadline = deadline;
        this.description = description;
    }

}
