import math
import uuid, json

from tasks.celery_app import celery
from dotenv import load_dotenv
from abc import ABC, abstractmethod

from utils.token_utils import decodeAccessToken
from service.notion_service import NotionService
from model.todo.todo_outbox_model import TodoCommentOutboxDTO, TodoOutboxDTO
from utils.notion_convert_utils import from_notion_status_id, from_notion_priority_id, to_notion_status_id, to_notion_priority_id, sync_notion_status, sync_notion_priority, to_notion_status_value, to_notion_priority_value
from repository import TodoRepository, TodoOutboxRepository
from model import TodoListRequest, TodoListResponse
from model import Todo, TodoComment
from model import notion_state
from datetime import timezone, timedelta

from utils.notion_utils import get_date_time, get_date, get_select, get_select_name, get_status, get_status_name, get_text

load_dotenv()

class TodoService(ABC):
    @abstractmethod
    def read_todos(listRequest : TodoListRequest) -> TodoListResponse:
        pass
    
    @abstractmethod
    def read_todo_detail(todo_id: str, user_id : str = None):
        pass
        
    @abstractmethod
    def create_todo(todo : Todo, access_token : str = None):
        pass

    @abstractmethod
    def delete_todo(todo_id : str, user_id : str = None, access_token : str = None) :
        pass
    
    @abstractmethod
    def update_todo(todo_id : str, todo_update: Todo, access_token : str = None) :
        pass
    
    @abstractmethod
    def create_comment(comment : TodoComment, access_token : str = None) :
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
        todo.todoId = str(uuid.uuid4())
        self.todo_list.append(todo)    
        
    def delete_todo(self, todo_id :str, user_id : str) :
        self.todo_list.remove([x for x in self.todo_list if x.id == todo_id and x.userId == user_id][0])

    def update_todo(self, todo_id : str, todo_update: Todo) :
        
        for index, todo in enumerate(self.todo_list):
            
            if todo.todoId == todo_id and todo.userId == todo_update.userId:
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
            comments = await self.notion_service.retrieve_reply_list(todo.todoId)
            
            if len(comments) > 0:
                for comment in comments:
                    todo.comments.append(TodoComment(commentId=comment["commentId"], todoId=todo.todoId, commentText=comment['body'], author=comment['author'], lastModified=comment['lastModified']))
            
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
        todo.todoId = str(uuid.uuid4())
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
    def __init__(self, notion_service: NotionService, todo_repository : TodoRepository, outbox_repository : TodoOutboxRepository):
        self.notion_service = notion_service
        self.todo_repository = todo_repository
        self.outbox_repository = outbox_repository
        
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
        total = 0
        totalPages = 0
        converted_data = []
        
        try :
            '''읽기 : DB'''
            temp_result = await self.todo_repository.select_list(listRequest)
            
            converted_data = [
                item.model_copy(update={"status": to_notion_status_value(item.status), "priority" : to_notion_priority_value(item.priority)})
                for item in temp_result.data
            ]
            
            total = temp_result.total
            totalPages =temp_result.totalPages
            
        except Exception as e:
            print(e)
            
        
        return TodoListResponse(
                data=converted_data,
                total=total,
                totalPages=totalPages
            )
        
    async def create_todo(self, todo : Todo, access_token : str = None):
        '''등록 : 노션 → DB(메시징큐 미사용)'''
        
        try :
            
            if not access_token:
                raise Exception("접근 권한이 없습니다.")

            access_token_payload = json.loads(decodeAccessToken(access_token))
            
            if "jti" not in access_token_payload :
                raise Exception("노션 등록에 실패하였습니다.")
            
            notion_response = await self.notion_service.create_page(todo)

            if not notion_response["isSuccess"]:
                raise Exception("노션 등록에 실패하였습니다.")
            
            if "id" not in notion_response:
                raise Exception("노션 등록에 실패하였습니다.")
            
            if notion_response["id"] == '':
                raise Exception("노션 등록에 실패하였습니다.")
            
            todo.todoId = notion_response["id"]
            
            created_entity = await self.todo_repository.create_todo(todo)
            
            if created_entity.id <= 0 :
                raise Exception("일정 등록에 실패하였습니다.")
            
            await self.outbox_repository.insert(
                dto = TodoOutboxDTO(
                    db_id = created_entity.id, 
                    todo_id = created_entity.todoId, 
                    event_type = 'created', 
                    user_id = created_entity.userId, 
                    token_jti = access_token_payload["jti"], 
                    payload = {
                        "before": None,
                        "after":  self.todo_repository.to_dict(created_entity)
                    }
                ), 
                processed = True
            )
            
            await self.todo_repository.commit()
        except Exception as e:
            print(e)
            await self.todo_repository.rollback()
            
            # 노션에서 삭제
            await self.notion_service.patch_page(todo.todoId, todo, True)
            
            # TODO 실패 시 outbox 처리
            
            
    
    async def read_todo_detail(self, todo_id: str, user_id : str):
        '''읽기 : DB(차후 노션도 추가 검토 - 상세 읽기는 속도 괜찮은 편)'''
        return await self.todo_repository.select_by_id(todo_id, user_id)
    
    async def update_todo(self, todo_id : str, todo_update: Todo, access_token : str = None) :
        '''수정 : DB → 노션(메시징큐 사용)'''
        
        try :
            
            if not access_token:
                raise Exception("접근 권한이 없습니다.")

            access_token_payload = json.loads(decodeAccessToken(access_token))
            
            if "jti" not in access_token_payload :
                raise Exception("노션 등록에 실패하였습니다.")
            
            before_entity = await self.todo_repository.select_by_id(todo_id, todo_update.userId)
            
            if before_entity is None:
                raise Exception("조회된 데이터가 없습니다.")
            
            # 수정 후 Entity
            updated_entity = await self.todo_repository.update(todo_id, todo_update)
            
            # outbox 등록
            outbox = await self.outbox_repository.insert(
                dto = TodoOutboxDTO(
                    db_id = updated_entity.id,
                    todo_id = updated_entity.todoId, 
                    event_type = 'updated', 
                    user_id = updated_entity.userId, 
                    token_jti = access_token_payload["jti"], 
                    payload = {
                        "before": self.todo_repository.to_dict(before_entity),
                        "after":  self.todo_repository.to_dict(updated_entity)
                    }
                ), 
                processed = False
            )
            
            await self.todo_repository.commit()
            
            celery.send_task("tasks.tasks.sync_to_notion", args=[str(outbox.id)])
            
        except Exception as e:
            print(e)
            await self.todo_repository.rollback()
            
            
    
    
    async def delete_todo(self, todo_id : str, user_id : str, access_token : str = None) :
        '''삭제 : DB → 노션(메시징큐 사용)'''
        try :
            if not access_token:
                raise Exception("접근 권한이 없습니다.")

            access_token_payload = json.loads(decodeAccessToken(access_token))
            
            if "jti" not in access_token_payload :
                raise Exception("노션 등록에 실패하였습니다.")
            
            before_entity = await self.todo_repository.select_by_id(todo_id, user_id)
            
            if before_entity is None:
                raise Exception("조회된 데이터가 없습니다.")
            
            deleted_entity = await self.todo_repository.delete(todo_id, user_id)
            
            outbox = await self.outbox_repository.insert(
                dto = TodoOutboxDTO(
                    db_id = deleted_entity.id,
                    todo_id = deleted_entity.todoId, 
                    event_type = 'deleted', 
                    user_id = deleted_entity.userId, 
                    token_jti = access_token_payload["jti"], 
                    payload = {
                        "before": self.todo_repository.to_dict(deleted_entity, True),
                        "after":  None
                    }
                ), 
                processed = False
            )
            
            await self.todo_repository.commit()
            
            celery.send_task("tasks.tasks.sync_to_notion", args=[str(outbox.id)])
            
        except Exception as e:
            print(e)
            await self.todo_repository.rollback()
            
    
    async def create_comment(self, comment : TodoComment, access_token : str = None) :
        '''댓글 등록 : 예외 발생 시 DB Rollback만'''
        
        try :
            
            if not access_token:
                raise Exception("접근 권한이 없습니다.")

            access_token_payload = json.loads(decodeAccessToken(access_token))
            
            if "jti" not in access_token_payload :
                raise Exception("노션 등록에 실패하였습니다.")
            
            notion_response = await self.notion_service.create_reply(comment)
            
            if not notion_response["isSuccess"]:
                raise Exception("노션 등록에 실패하였습니다.")
            
            if "id" not in notion_response:
                raise Exception("노션 등록에 실패하였습니다.")
            
            if notion_response["id"] == '':
                raise Exception("노션 등록에 실패하였습니다.")
            
            comment.commentId = notion_response["id"]
            comment.isTrash = False    
            
            created_entity = await self.todo_repository.create_todo_comment(comment)
            
            if created_entity.id <= 0 :
                raise Exception("답글 등록에 실패하였습니다.")
            
            await self.outbox_repository.insertComment(
                dto = TodoCommentOutboxDTO(
                    db_id = created_entity.id,
                    todo_id = created_entity.todoId, 
                    comment_id = created_entity.commentId,
                    event_type = 'created', 
                    token_jti = access_token_payload["jti"], 
                    payload = {
                        "before": None,
                        "after":  self.todo_repository.to_comment_dict(created_entity)
                    }
                ), 
                processed = True
            )
            
            
            await self.todo_repository.commit()
        except Exception as e:
            print(e)
            '''노션에는 delete comment가 존재하지 않기 때문에 실패 시 rollback만 존재'''
            await self.todo_repository.rollback()

            # TODO 실패 시 outbox 처리
            
            