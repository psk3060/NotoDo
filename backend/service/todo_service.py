import math
import uuid

from dotenv import load_dotenv
from abc import ABC, abstractmethod
from service.notion_service import NotionService
from utils.notion_convert_utils import from_notion_status_id, from_notion_priority_id, to_notion_status_id, to_notion_priority_id, sync_notion_status, sync_notion_priority
from repository.todo_repository import TodoRepository
from model import TodoListRequest, TodoListResponse
from model import Todo, TodoComment
from model import notion_state
from datetime import datetime, timezone, timedelta

from utils.notion_utils import get_date_time, get_date, get_select, get_select_name, get_status, get_status_name, get_text

load_dotenv()

class TodoService(ABC):
    @abstractmethod
    def read_todos(listRequest : TodoListRequest) -> TodoListResponse:
        pass
    
    @abstractmethod
    def read_todo_detail(todo_id: str, user_id : str):
        pass
        
    @abstractmethod
    def create_todo(todo : Todo):
        pass

    @abstractmethod
    def delete_todo(todo_id : str, user_id : str) :
        pass
    
    @abstractmethod
    def update_todo(todo_id : str, todo_update: Todo) :
        pass
    
    @abstractmethod
    def create_comment(comment : TodoComment) :
        pass
    

class LocalTodoServiceImpl(TodoService):
    def __init__(self):
        self.todo_list = []
        self.todo_list.append(Todo(id = str(uuid.uuid4()), title = "Sample Todo", status = "Pending", registDate = "2025-02-06 17:30", deadline = "2025-02-10", description = "This is a sample", userId = "demo"))
        self.todo_list.append(Todo(id = str(uuid.uuid4()), title = "Another Todo", status = "Pending", registDate = "2025-02-06 18:00", deadline = "2025-02-14", description = "This is another sample", userId = "demo"))
        self.todo_list.append(Todo(id = str(uuid.uuid4()), title = "Yet Another Todo", status = "Pending", registDate = "2025-02-06 21:35", deadline = "2025-02-10", description = "This is yet another sample", userId = "demo"))
        
    def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
        todos = [x for x in self.todo_list if x.userId == listRequest.userId]
        total = len(todos)
        
        result = None
        
        if listRequest.isPaging :
            start = (listRequest.currentPage - 1) * listRequest.pageSize
            end = start + listRequest.pageSize
            result = TodoListResponse(data = todos[start:end], total= total, totalPages=math.ceil(total / listRequest.pageSize))
        else :
            result = TodoListResponse(data = todos, total= total)
        
        return result
    
    def read_todo_detail(self, todo_id: int, user_id : str) -> Todo: 
        return [x for x in self.todo_list if x.id == todo_id and x.userId == user_id][0]
    
    def create_todo(self, todo : Todo):
        todo.id = str(uuid.uuid4())
        self.todo_list.append(todo)    
        
    def delete_todo(self, todo_id :str, user_id : str) :
        self.todo_list.remove([x for x in self.todo_list if x.id == todo_id and x.userId == user_id][0])

    def update_todo(self, todo_id : str, todo_update: Todo) :
        
        for index, todo in enumerate(self.todo_list):
            
            if todo.id == todo_id and todo.userId == todo_update.userId:
                # 기존 todo를 직접 수정 (순서 유지)
                updated_data = todo.dict()
            
                if todo_update.title is not None:
                    updated_data['title'] = todo_update.title
            
                if todo_update.status is not None:
                    updated_data['status'] = todo_update.status
                
                if todo_update.deadline is not None:
                    updated_data['deadline'] = todo_update.deadline
                
                if todo_update.description is not None:
                    updated_data['description'] = todo_update.description

                self.todo_list[index] = Todo(**updated_data)
    
    def create_comment(self, comment : TodoComment) :
        '''답글 등록 TODO'''
        pass



class NotionTodoServiceImpl(TodoService):
    
    def __init__(self, notion_service: NotionService):
        self.notion_service = notion_service
    
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
        todos = []

        if len(notion_state.data_sources) > 0:
            source = notion_state.data_sources[0]
        
        filter = {}
        
        if listRequest :
            if listRequest.title and listRequest.title != '':
                filter['작업명'] = listRequest.title
            if listRequest.priority and listRequest.priority != '':
                filter['우선순위'] = listRequest.priority
            if listRequest.status and listRequest.status != '':
                filter['상태'] = listRequest.status
        
        result = await self.notion_service.query_datasource(source["id"], filter)
        
        pages = result['pages']
        
        for page in pages:
            props = page["properties"]

            todo = Todo(
                    id=page["id"],
                    title = get_text(props, "작업명"),
                    status = get_status_name(props, "상태"),
                    registDate = get_date_time(page, 'created_time'),
                    deadline = get_date(props, '마감일'),
                    priority = get_select_name(props, "우선순위")
            )
                
            todos.append(todo)
            
        
        total = len(todos)
        
        result = None
        
        if listRequest.isPaging :
            start = (listRequest.currentPage - 1) * listRequest.pageSize
            end = start + listRequest.pageSize
            result = TodoListResponse(data = todos[start:end], total= total, totalPages=math.ceil(total / listRequest.pageSize))
        else :
            result = TodoListResponse(data = todos, total=len(todos))
        
        return result
        
    
    # 상세 조회
    async def read_todo_detail(self, todo_id: str, user_id:str) -> Todo: 
        
        page = await self.notion_service.retrieve_page(todo_id)
        
        todo = None
        
        if page and page['id'] != '':
            
            props = page["properties"]

            todo = Todo(
                id=page["id"],
                title = get_text(props, "작업명"),
                description = get_text(props, "설명"),
                status = from_notion_status_id(get_status(props, "상태")),
                registDate = get_date_time(page, 'created_time'),
                deadline = get_date(props, '마감일'),
                priority = from_notion_priority_id(get_select(props, "우선순위"))
            )
        
        if todo:
            comments = await self.notion_service.retrieve_reply_list(todo.id)
            
            if len(comments) > 0:
                for comment in comments:
                    todo.comments.append(TodoComment(commentId=comment["id"], todoId=todo.id, commentText=comment['body'], author=comment['author'], lastModified=comment['lastModified']))
            
        return todo

    # 작업 추가
    async def create_todo(self, todo : Todo):
        return await self.notion_service.create_page(todo)
        
    # 작업 삭제
    async def delete_todo(self, todo_id :str, user_id:str) :
        await self.notion_service.patch_page(todo_id, None, True)

    # 작업 수정
    async def update_todo(self, todo_id : str, todo_update: Todo) :
        await self.notion_service.patch_page(todo_id, todo_update)
        
    async def create_comment(self, comment : TodoComment) :
        await self.notion_service.create_reply(comment)


class DbTodoServiceImpl(TodoService):
    
    def __init__(self, todo_repository : TodoRepository):
        self.todo_repository = todo_repository
    
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
        temp_result = await self.todo_repository.select_list(listRequest)
        
        converted_data = [
            item.model_copy(update={"status": sync_notion_status(item.status), "priority" : sync_notion_priority(item.priority)})
            for item in temp_result.data
        ]

        return TodoListResponse(
            data=converted_data,
            total=temp_result.total,
            totalPages=temp_result.totalPages
        )

    async def create_todo(self, todo : Todo):
        todo.id = str(uuid.uuid4())
        todo.status = to_notion_status_id(todo.status)
        todo.priority = to_notion_priority_id(todo.priority)
        
        return await self.todo_repository.create_todo(todo)
    
    # 상세 조회
    async def read_todo_detail(self, todo_id: str, user_id : str):
        
        temp_result = await self.todo_repository.select_by_id(todo_id, user_id)
        
        if temp_result:
            temp_result.registDate = temp_result.registDate.astimezone(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M")
            temp_result.status = from_notion_status_id(temp_result.status)
            temp_result.priority = from_notion_priority_id(temp_result.priority)
        
        return temp_result
        
    # 삭제(is_trash를 True로)
    async def delete_todo(self, todo_id : str, user_id : str) :
        await self.todo_repository.delete(Todo(id = todo_id, userId = user_id))
    
    
    # 수정
    async def update_todo(self, todo_id : str, todo_update: Todo) :
        
        todo_update.status = to_notion_status_id(todo_update.status)
        todo_update.priority = to_notion_priority_id(todo_update.priority)
        
        if todo_id == todo_update.id:
            await self.todo_repository.update(todo_id, todo_update)
    
    # 댓글 등록 
    async def create_comment(self, comment : TodoComment) :
        comment.commentId = str(uuid.uuid4())
        comment.isTrash = False
        
        await self.todo_repository.create_todo_comment(comment)



class HybridTodoServiceImpl(TodoService) :
    def __init__(self, notion_service: NotionService, todo_repository : TodoRepository):
        self.notion_service = notion_service
        self.todo_repository = todo_repository
        
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
        '''읽기 : DB'''
        
        temp_result = await self.todo_repository.select_list(listRequest)
        
        converted_data = [
            item.model_copy(update={"status": sync_notion_status(item.status), "priority" : sync_notion_priority(item.priority)})
            for item in temp_result.data
        ]

        return TodoListResponse(
            data=converted_data,
            total=temp_result.total,
            totalPages=temp_result.totalPages
        )
        
    async def create_todo(self, todo : Todo):
        '''등록 : 노션 → DB(메시징큐 미사용)'''
        notion_response = await self.notion_service.create_page(todo)
        
        if notion_response["isSuccess"] and "id" in notion_response and notion_response["id"] != '':
            id = notion_response["id"]
            
            todo.id = id
            
            todo.status = to_notion_status_id(todo.status)
            todo.priority = to_notion_priority_id(todo.priority)
        
            await self.todo_repository.create_todo(todo)
    
    async def read_todo_detail(self, todo_id: str, user_id : str):
        '''읽기 : DB(차후 노션도 추가 검토 - 상세 읽기는 속도 괜찮은 편)'''
        temp_result = await self.todo_repository.select_by_id(todo_id, user_id)
        
        if temp_result:
            temp_result.registDate = temp_result.registDate.astimezone(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M")
            temp_result.status = from_notion_status_id(temp_result.status)
            temp_result.priority = from_notion_priority_id(temp_result.priority)
        
        return temp_result
    
    def delete_todo(self, todo_id : str, user_id : str) :
        '''삭제 : DB → 노션(메시징큐 사용)'''
        pass
    
    def update_todo(self, todo_id : str, todo_update: Todo) :
        '''수정 : DB → 노션(메시징큐 사용)'''
        pass
    
    async def create_comment(self, comment : TodoComment) :
        '''등록 : 노션 → DB(메시징큐 미사용)'''
        notion_response = await self.notion_service.create_reply(comment)
        
        if notion_response["isSuccess"] and "commentId" in notion_response and notion_response["commentId"] != '':
            comment.commentId = notion_response["commentId"]
            comment.isTrash = False    

            await self.todo_repository.create_todo_comment(comment)
            
        