import logging
import math
import uuid, json

from dotenv import load_dotenv
from abc import ABC, abstractmethod

from tasks.config.celery_config import sync_celery

from utils.token_utils import decodeAccessToken

from utils import notion_utils as notion

from service.notion_service import NotionService
from service.condition_service import SearchConditionService
from service.outbox_service import OutboxRegistServiceImpl

from model import Todo, TodoComment
from model import OutboxDTO

from repository import TodoBaseRepository
from model import TodoListRequest, TodoListResponse

from datetime import timezone, timedelta

load_dotenv()

logger = logging.getLogger(__name__)

class TodoService(ABC):
    @abstractmethod
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:...
    @abstractmethod
    async def read_todo_detail(self, todo_id: str, user_id : str = None):...
    @abstractmethod
    async def create_todo(self, todo : Todo, access_token : str = None):...
    @abstractmethod
    async def delete_todo(self, todo_id : str, user_id : str = None, access_token : str = None) : ...
    @abstractmethod
    async def update_todo(self, todo_id : str, todo_update: Todo, access_token : str = None) : ...
    @abstractmethod
    async def create_comment(self, comment : TodoComment, access_token : str = None) : ...
    

class LocalTodoServiceImpl(TodoService):
    """Local 환경에서 테스트용으로 사용되는 TodoService 구현체(Notion 연결 X. DB 연결 X)"""
    def __init__(self):
        self.todo_list = []
        self.todo_list.append(Todo(id = str(uuid.uuid4()), title = "Sample Todo", status = "Pending", registDate = "2025-02-06 17:30", deadline = "2025-02-10", description = "This is a sample", userId = "demo"))
        self.todo_list.append(Todo(id = str(uuid.uuid4()), title = "Another Todo", status = "Pending", registDate = "2025-02-06 18:00", deadline = "2025-02-14", description = "This is another sample", userId = "demo"))
        self.todo_list.append(Todo(id = str(uuid.uuid4()), title = "Yet Another Todo", status = "Pending", registDate = "2025-02-06 21:35", deadline = "2025-02-10", description = "This is yet another sample", userId = "demo"))
        
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
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
    
    async def read_todo_detail(self, todo_id: int, user_id : str) -> Todo: 
        return [x for x in self.todo_list if x.id == todo_id and x.userId == user_id][0]
    
    async def create_todo(self, todo : Todo):
        todo.todoId = str(uuid.uuid4())
        self.todo_list.append(todo)    
        
    async def delete_todo(self, todo_id :str, user_id : str) :
        self.todo_list.remove([x for x in self.todo_list if x.id == todo_id and x.userId == user_id][0])

    async def update_todo(self, todo_id : str, todo_update: Todo) :
        
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
    
    async def create_comment(self, comment : TodoComment) :
        '''답글 등록 TODO'''
        pass



class NotionTodoServiceImpl(TodoService):
    """Notion과 연동이 되는 구현체(컨테이너 필요)"""
    
    def __init__(self, notion_service: NotionService):
        self.notion_service = notion_service
    
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
        todos = []

        filter = {}
        
        if listRequest :
            if listRequest.title and listRequest.title != '':
                filter['작업명'] = listRequest.title
            if listRequest.priority and listRequest.priority != '':
                filter['우선순위'] = listRequest.priority
            if listRequest.status and listRequest.status != '':
                filter['상태'] = listRequest.status
        
        result = await self.notion_service.query_datasource(filter)
        
        pages = result['pages']
        
        for page in pages:
            props = page["properties"]

            todo = Todo(
                    id=page["id"],
                    title = notion.get_text(props, "작업명"),
                    status = notion.get_status_name(props, "상태"),
                    registDate = notion.get_date_time(page, 'created_time'),
                    deadline = notion.get_date(props, '마감일'),
                    priority = notion.get_select_name(props, "우선순위")
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
                title = notion.get_text(props, "작업명"),
                description = notion.get_text(props, "설명"),
                status = notion.from_notion_status_id(notion.get_status(props, "상태")),
                registDate = notion.get_date_time(page, 'created_time'),
                deadline = notion.get_date(props, '마감일'),
                priority = notion.from_notion_priority_id(notion.get_select(props, "우선순위"))
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
    """DB와 연동되는 구현체(Notion 연결 X)"""
    
    def __init__(self, todo_repository : TodoBaseRepository):
        self.todo_repository = todo_repository
    
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
        temp_result = await self.todo_repository.select_list(listRequest)
        
        converted_data = [
            item.model_copy(update={"status": notion.sync_notion_status(item.status), "priority" : notion.sync_notion_priority(item.priority)})
            for item in temp_result.data
        ]

        return TodoListResponse(
            data=converted_data,
            total=temp_result.total,
            totalPages=temp_result.totalPages
        )

    async def create_todo(self, todo : Todo):
        todo.todoId = str(uuid.uuid4())
        todo.status = notion.to_notion_status_id(todo.status)
        todo.priority = notion.to_notion_priority_id(todo.priority)
        
        return await self.todo_repository.create_todo(todo)
    
    # 상세 조회
    async def read_todo_detail(self, todo_id: str, user_id : str):
        
        temp_result = await self.todo_repository.select_by_id(todo_id, user_id)
        
        if temp_result:
            temp_result.registDate = temp_result.registDate.astimezone(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M")
            temp_result.status = notion.from_notion_status_id(temp_result.status)
            temp_result.priority = notion.from_notion_priority_id(temp_result.priority)
        
        return temp_result
        
    # 삭제(is_trash를 True로)
    async def delete_todo(self, todo_id : str, user_id : str) :
        await self.todo_repository.delete(Todo(id = todo_id, userId = user_id))
    
    
    # 수정
    async def update_todo(self, todo_id : str, todo_update: Todo) :
        
        todo_update.status = notion.to_notion_status_id(todo_update.status)
        todo_update.priority = notion.to_notion_priority_id(todo_update.priority)
        
        if todo_id == todo_update.id:
            await self.todo_repository.update(todo_id, todo_update)
    
    # 댓글 등록 
    async def create_comment(self, comment : TodoComment) :
        comment.commentId = str(uuid.uuid4())
        comment.isTrash = False
        
        await self.todo_repository.create_todo_comment(comment)



class HybridTodoServiceImpl(TodoService) :
    
    """DB와 Notion 모두 연동하는 구현체(컨테이너 필요)"""
    def __init__(self, notion_service: NotionService, todo_repository : TodoBaseRepository, outbox_service : OutboxRegistServiceImpl, condition_service : SearchConditionService):
        self.notion_service = notion_service
        self.todo_repository = todo_repository
        self.outbox_service = outbox_service
        self.condition_service = condition_service
    
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:
        total = 0
        totalPages = 0
        converted_data = []
        
        try :
            '''읽기 : DB'''
            temp_result = await self.todo_repository.select_list(listRequest)
            
            converted_data = [
                item.model_copy(update={"status": notion.to_notion_status_label(item.status), "priority" : notion.to_notion_priority_label(item.priority)})
                for item in temp_result.data
            ]
            
            total = temp_result.total
            totalPages =temp_result.totalPages
            
        except Exception as e:
            print(e)
        finally : 
            if listRequest.status != '' or listRequest.priority != '' or listRequest.title != '' :
                
                conditions = {}
                
                conditions["status"] = listRequest.status
                conditions["priority"] = listRequest.priority
                conditions["title"] = listRequest.title
                
                # 조회 조건 저장
                await self.condition_service.save_condition(listRequest.userId, conditions)
                
        
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
            
            await self.outbox_service.insert(
                dto = OutboxDTO(
                    db_id = created_entity.id, 
                    event_caller = 'todo',
                    parent_id = created_entity.todoId, 
                    child_id = None,
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
            
            logger.error(e)
            
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
            
            await self.outbox_service.insert(
                dto = OutboxDTO(
                    db_id = updated_entity.id,
                    event_caller = 'todo',
                    parent_id = updated_entity.todoId, 
                    child_id = None,
                    event_type = 'updated', 
                    user_id = updated_entity.userId, 
                    token_jti = access_token_payload["jti"], 
                    payload = {
                        "before": self.todo_repository.to_dict(before_entity),
                        "after":  self.todo_repository.to_dict(updated_entity)
                    }
                ), 
                processed = False,
                queueName = "sync"
            )
            
            await self.todo_repository.commit()
            
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
            
            await self.outbox_service.insert(
                dto = OutboxDTO (
                    db_id = deleted_entity.id,
                    event_caller = 'todo',
                    parent_id = deleted_entity.todoId, 
                    child_id = None,
                    event_type = 'deleted', 
                    user_id = deleted_entity.userId, 
                    token_jti = access_token_payload["jti"], 
                    payload = {
                        "before": self.todo_repository.to_dict(deleted_entity),
                        "after":  None
                    }
                ),
                processed = False,
                queueName = "sync"
            )
            
            await self.todo_repository.commit()
            
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
            
            await self.outbox_service.insert(
                dto = OutboxDTO(
                    db_id = created_entity.id,
                    event_caller = 'todo_comment',
                    parent_id = created_entity.todoId, 
                    child_id = created_entity.commentId, 
                    event_type = 'created', 
                    token_jti = access_token_payload["jti"], 
                    payload = {
                        "before": None,
                        "after":  self.todo_repository.to_comment_dict(created_entity)
                    }
                )
                , 
                processed = True
            )
            
            await self.todo_repository.commit()
        except Exception as e:
            print(e)
            '''노션에는 delete comment가 존재하지 않기 때문에 실패 시 rollback만 존재'''
            await self.todo_repository.rollback()

            # TODO 실패 시 outbox 처리
            
            
            
class TaskTodoServiceImpl(TodoService):
    """Task에서 사용하는 TodoService - Update만 필요"""
    
    def __init__(self, repository : TodoBaseRepository):
        self.repository = repository
    
    async def update_todo(self, todo_id : str, todo_update: Todo, access_token : str = None) : 
        
        try :
            await self.repository.update(todo_id, todo_update)
            await self.repository.commit()
        except Exception as ex:
            logger.error(f"[Task Update Todo] 예외 발생 - {ex}")
            await self.repository.rollback()
        
    
    async def read_todos(self, listRequest : TodoListRequest) -> TodoListResponse:...
    async def read_todo_detail(self, todo_id: str, user_id : str = None):...
    async def create_todo(self, todo : Todo, access_token : str = None):...
    async def delete_todo(self, todo_id : str, user_id : str = None, access_token : str = None) : ...
    async def create_comment(self, comment : TodoComment, access_token : str = None) : ...
    
    