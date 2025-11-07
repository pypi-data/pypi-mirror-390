"""
通用CRUD操作基类

提供数据库增删改查的通用操作，支持类型安全和自动化处理。
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel as PydanticModel
from sqlalchemy import and_, asc, desc, func, or_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from pyadvincekit.core.exceptions import (
    DatabaseError,
    NotFoundError,
    RecordNotFoundError,
    RecordAlreadyExistsError,
)
from pyadvincekit.models.base import BaseModel, SoftDeleteModel

from pyadvincekit.logging import get_logger
from pyadvincekit.docs import api_category, api_doc, api_example, api_table

logger = get_logger(__name__)

# 泛型类型变量
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """通用CRUD操作基类"""

    def __init__(self, model: Type[ModelType]) -> None:
        """
        初始化CRUD操作类
        
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model

    @api_category("数据库操作", "基础CRUD")
    @api_doc(
        title="根据ID获取单个记录",
        description="通过主键ID获取数据库中的单条记录，支持灵活的异常处理策略",
        signature="get(db: AsyncSession, id: Any, raise_not_found: bool = True) -> Optional[ModelType]",
        params={
            "db": "AsyncSession数据库会话对象",
            "id": "记录的主键ID，支持各种类型",
            "raise_not_found": "找不到记录时是否抛出异常，默认True"
        },
        returns="Optional[ModelType]: 找到的模型实例或None",
        version="2.0.0"
    )
    @api_example('''
from pyadvincekit.crud.base import BaseCRUD
from models import User
from schemas import UserCreate, UserUpdate

# 创建CRUD实例
user_crud = BaseCRUD(User)

# 获取用户（找不到会抛异常）
user = await user_crud.get(db, user_id="123")
print(f"用户名: {user.username}")

# 获取用户（找不到返回None）
user = await user_crud.get(db, user_id="999", raise_not_found=False)
if user is None:
    print("用户不存在")

# 在事务中使用
async with get_db() as db:
    try:
        user = await user_crud.get(db, "invalid_id")
    except RecordNotFoundError as e:
        print(f"记录不存在: {e}")
    except DatabaseError as e:
        print(f"数据库错误: {e}")
    ''', description="单个记录查询的多种用法", title="get 使用示例")
    async def get(
        self, 
        db: AsyncSession, 
        id: Any,
        raise_not_found: bool = True
    ) -> Optional[ModelType]:
        """
        根据ID获取单个记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            raise_not_found: 是否在找不到记录时抛出异常
            
        Returns:
            模型实例或None
            
        Raises:
            RecordNotFoundError: 当记录不存在且raise_not_found为True时
        """
        try:
            result = await db.get(self.model, id)
            
            if result is None and raise_not_found:
                raise RecordNotFoundError(
                    f"{self.model.__name__} with id {id} not found",
                    model=self.model.__name__,
                    resource_id=str(id)
                )
            
            return result
            
        except Exception as e:
            if isinstance(e, RecordNotFoundError):
                raise
            logger.error(f"Failed to get {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to retrieve record: {e}")

    @api_category("数据库操作")
    @api_doc(
        title="批量查询数据",
        description="支持分页、过滤、排序的高级查询功能，包含AND/OR组合查询",
        params={
            "db": "数据库会话",
            "skip": "跳过记录数，用于分页",
            "limit": "限制返回数量（默认100）",
            "order_by": "排序字段名称",
            "order_desc": "是否降序排列（默认False）",
            "filters": "AND过滤条件字典，支持简单值、列表（IN查询）、复杂操作符",
            "or_filters": "OR过滤条件列表，每个元素是一个过滤条件字典",
            "include_deleted": "是否包含已删除记录（软删除模型）"
        },
        returns="List[ModelType]: 符合条件的模型实例列表",
        version="2.0.0"
    )
    @api_example("""
# 基础分页查询
users = await user_crud.get_multi(db, skip=0, limit=10)

# 简单过滤查询
active_users = await user_crud.get_multi(
    db, 
    filters={"is_active": True, "status": "normal"}
)

# 列表值查询（IN操作）
specific_users = await user_crud.get_multi(
    db,
    filters={"id": [1, 2, 3, 4, 5]}
)

# 复杂操作符查询示例
adult_users = await user_crud.get_multi(
    db,
    filters={
        "age": {"operator": "gte", "value": 18},
        "name": {"operator": "like", "value": "张"}
    }
)

# OR查询
vip_or_admin = await user_crud.get_multi(
    db,
    or_filters=[
        {"is_vip": True},
        {"role": "admin"}
    ]
)

# AND + OR组合查询
complex_query = await user_crud.get_multi(
    db,
    filters={"is_active": True},  # 必须激活
    or_filters=[                   # 并且是VIP或管理员
        {"is_vip": True},
        {"role": "admin"}
    ],
    order_by="created_at",
    order_desc=True,
    limit=20
)
    """, description="get_multi方法的多种使用场景")
    @api_table(
        title="其他操作",
        table_data="""| operator操作 | 含义                     | 示例                                                      |
| ------------ | ------------------------ | --------------------------------------------------------- |
| like         | 区分大小写的模糊匹配 %A% | filters={"username": {"operator": "like", "value": "A"}}  |
| ilike        | 不区分大小写的模糊匹配   | filters={"username": {"operator": "ilike", "value": "A"}} |
| gt           | 大于 >                   | filters={"age": {"operator": "gt", "value": 30}}          |
| gte          | 大于等于 >=              | filters={"age": {"operator": "gte", "value": 30}}         |
| lt           | 小于 <                   | filters={"age": {"operator": "lt", "value": 30}}          |
| lte          | 小于等于 <=              | filters={"age": {"operator": "lte", "value": 30}}         |
| ne           | 不等于 !=                | filters={"age": {"operator": "ne", "value": 30}}          |""",
        description="filter支持多种operator操作，其他匹配符如下表所示："
    )
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        or_filters: Optional[List[Dict[str, Any]]] = None,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        获取多个记录
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 限制记录数
            order_by: 排序字段
            order_desc: 是否降序
            filters: 过滤条件（AND关系）
            or_filters: OR过滤条件列表，每个元素是一个过滤条件字典
            include_deleted: 是否包含已删除记录（软删除模型）
            
        Returns:
            模型实例列表
            
        Examples:
            # AND查询（原有功能）
            users = await crud.get_multi(db, filters={"is_active": True, "status": "normal"})
            
            # OR查询
            users = await crud.get_multi(db, or_filters=[
                {"name": {"operator": "like", "value": "张"}},
                {"email": {"operator": "like", "value": "gmail"}}
            ])
            
            # AND + OR组合查询
            users = await crud.get_multi(db, 
                filters={"is_active": True},
                or_filters=[{"name": {"operator": "like", "value": "张"}}, {"department": "IT"}]
            )
        """
        try:
            query = select(self.model)
            
            # 处理软删除过滤
            if issubclass(self.model, SoftDeleteModel) and not include_deleted:
                query = query.where(self.model.is_deleted == False)
            
            # 构建查询条件列表
            conditions = []
            
            # 处理AND过滤条件（原有filters逻辑）
            if filters:
                and_conditions = self._build_filter_conditions(filters)
                conditions.extend(and_conditions)
            
            # 处理OR过滤条件
            if or_filters:
                or_conditions_list = []
                for or_filter in or_filters:
                    or_single_conditions = self._build_filter_conditions(or_filter)
                    or_conditions_list.extend(or_single_conditions)
                
                if or_conditions_list:
                    # 将所有OR条件组合成一个OR表达式
                    conditions.append(or_(*or_conditions_list))
            
            # 应用所有条件
            if conditions:
                query = query.where(and_(*conditions))
            
            # 处理排序
            if order_by and hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))
            else:
                # 默认按创建时间降序
                if hasattr(self.model, 'created_at'):
                    query = query.order_by(desc(self.model.created_at))
            
            # 分页
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get multiple {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to retrieve records: {e}")

    async def count(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        or_filters: Optional[List[Dict[str, Any]]] = None,
        include_deleted: bool = False
    ) -> int:
        """
        获取记录总数
        
        Args:
            db: 数据库会话
            filters: 过滤条件（AND关系）
            or_filters: OR过滤条件列表，每个元素是一个过滤条件字典
            include_deleted: 是否包含已删除记录
            
        Returns:
            记录总数
        """
        try:
            # 使用 * 来计数所有行，而不是依赖特定字段
            query = select(func.count()).select_from(self.model)
            
            # 处理软删除过滤
            if issubclass(self.model, SoftDeleteModel) and not include_deleted:
                query = query.where(self.model.is_deleted == False)
            
            # 构建查询条件列表
            conditions = []
            
            # 处理AND过滤条件
            if filters:
                and_conditions = self._build_filter_conditions(filters)
                conditions.extend(and_conditions)
            
            # 处理OR过滤条件
            if or_filters:
                or_conditions_list = []
                for or_filter in or_filters:
                    or_single_conditions = self._build_filter_conditions(or_filter)
                    or_conditions_list.extend(or_single_conditions)
                
                if or_conditions_list:
                    # 将所有OR条件组合成一个OR表达式
                    conditions.append(or_(*or_conditions_list))
            
            # 应用所有条件
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await db.execute(query)
            return result.scalar() or 0
            
        except Exception as e:
            logger.error(f"Failed to count {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to count records: {e}")

    @api_category("数据库操作", "基础CRUD")
    @api_doc(
        title="创建新记录",
        description="在数据库中创建新记录，支持完整的异常处理和数据验证",
        params={
            "db": "AsyncSession数据库会话对象",
            "obj_in": "输入数据，支持Pydantic模型或字典格式"
        },
        returns="ModelType: 创建成功的模型实例，包含自动生成的ID和时间戳",
        version="2.0.0"
    )
    @api_example('''
from pyadvincekit.crud.base import BaseCRUD
from models import User
from schemas import UserCreate, UserUpdate

# 创建CRUD实例
user_crud = BaseCRUD(User)

# 使用Pydantic模型创建用户
user_data = UserCreate(
    username="john_doe",
    email="john@example.com",
    full_name="John Doe",
    is_active=True
)
new_user = await user_crud.create(db, user_data)
print(f"创建用户: {new_user.id}")

# 使用字典创建用户
user_dict = {
    "username": "jane_doe",
    "email": "jane@example.com", 
    "full_name": "Jane Doe",
    "is_active": True
}
new_user = await user_crud.create(db, user_dict)

# 处理创建异常
try:
    duplicate_user = await user_crud.create(db, user_data)
except RecordAlreadyExistsError as e:
    print(f"用户已存在: {e}")
except DatabaseError as e:
    print(f"数据库错误: {e}")
    ''', description="创建记录的多种方式和异常处理", title="create 使用示例")
    async def create(
        self, 
        db: AsyncSession, 
        obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        创建新记录
        
        Args:
            db: 数据库会话
            obj_in: 输入数据（Pydantic模型或字典）
            
        Returns:
            创建的模型实例
        """
        try:
            if isinstance(obj_in, dict):
                create_data = obj_in
            else:
                create_data = obj_in.model_dump(exclude_unset=True)
            
            db_obj = self.model(**create_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            
            # 获取主键值用于日志记录
            pk_value = self._get_primary_key_value(db_obj)
            logger.info(f"Created {self.model.__name__} with primary key {pk_value}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create {self.model.__name__}: {e}")
            
            # 获取完整的错误信息
            error_str = str(e)
            error_lower = error_str.lower()
            
            # 记录详细错误用于调试
            logger.error(f"Full error details: {repr(e)}")
            
            # 检查是否为完整性约束错误
            if any(keyword in error_lower for keyword in [
                "unique constraint failed", "duplicate key", "duplicate entry",
                "integrityerror", "1062", "duplicate"
            ]):
                # 提取更详细的错误信息
                if "duplicate entry" in error_lower:
                    raise RecordAlreadyExistsError(f"Duplicate entry error: {error_str}")
                else:
                    raise RecordAlreadyExistsError(f"Record already exists: {error_str}")
            
            # 检查是否为外键约束错误
            if any(keyword in error_lower for keyword in [
                "foreign key constraint", "cannot add or update", "1452"
            ]):
                raise DatabaseError(f"Foreign key constraint violation: {error_str}")
            
            # 检查是否为非空约束错误
            if any(keyword in error_lower for keyword in [
                "not null constraint", "cannot be null", "1048"
            ]):
                raise DatabaseError(f"Required field cannot be null: {error_str}")
            
            # 对于其他 IntegrityError，提供完整错误信息
            if "integrityerror" in error_lower or "integrity" in error_lower:
                raise DatabaseError(f"Database integrity constraint violation: {error_str}")
            
            raise DatabaseError(f"Failed to create record: {error_str}")

    @api_category("数据库操作", "基础CRUD")
    @api_doc(
        title="更新记录",
        description="更新数据库中的现有记录，支持部分字段更新和事务回滚",
        params={
            "db": "AsyncSession数据库会话对象",
            "db_obj": "要更新的模型实例对象",
            "obj_in": "更新数据，支持Pydantic模型或字典格式"
        },
        returns="ModelType: 更新后的模型实例，包含最新的时间戳",
        version="2.0.0"
    )
    @api_example('''
from pyadvincekit.crud.base import BaseCRUD
from models import User
from schemas import UserCreate, UserUpdate

user_crud = BaseCRUD(User)

# 先获取要更新的用户
user = await user_crud.get(db, user_id="123")

# 使用Pydantic模型更新
update_data = UserUpdate(
    full_name="John Smith",
    is_active=False
)
updated_user = await user_crud.update(db, user, update_data)
print(f"更新用户: {updated_user.full_name}")

# 使用字典部分更新
update_dict = {
    "email": "newemail@example.com",
    "last_login_at": datetime.now()
}
updated_user = await user_crud.update(db, user, update_dict)

# 处理更新异常
try:
    updated_user = await user_crud.update(db, user, update_data)
except DatabaseError as e:
    print(f"更新失败: {e}")
    ''', description="记录更新的多种方式", title="update 使用示例")
    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录
        
        Args:
            db: 数据库会话
            db_obj: 要更新的模型实例
            obj_in: 更新数据
            
        Returns:
            更新后的模型实例
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            
            # 使用BaseModel的update_from_dict方法
            db_obj.update_from_dict(update_data)
            
            await db.commit()
            await db.refresh(db_obj)
            
            logger.info(f"Updated {self.model.__name__} with id {db_obj.id}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to update record: {e}")

    async def update_by_id(
        self,
        db: AsyncSession,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        根据ID更新记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            obj_in: 更新数据
            
        Returns:
            更新后的模型实例
        """
        db_obj = await self.get(db, id)
        return await self.update(db, db_obj, obj_in)

    @api_category("数据库操作", "基础CRUD")
    @api_doc(
        title="删除记录（物理删除）",
        description="从数据库中永久删除指定记录，操作不可恢复",
        params={
            "db": "AsyncSession数据库会话对象",
            "id": "要删除记录的主键ID"
        },
        returns="bool: 删除操作是否成功",
        version="2.0.0"
    )
    @api_example('''
from pyadvincekit.crud.base import BaseCRUD
from models import User
from schemas import UserCreate, UserUpdate

user_crud = BaseCRUD(User)

# 删除用户
try:
    success = await user_crud.delete(db, user_id="123")
    if success:
        print("用户删除成功")
except RecordNotFoundError:
    print("用户不存在")
except DatabaseError as e:
    print(f"删除失败: {e}")

# 在事务中批量删除
async with get_db() as db:
    user_ids = ["123", "456", "789"]
    deleted_count = 0
    
    for user_id in user_ids:
        try:
            await user_crud.delete(db, user_id)
            deleted_count += 1
        except Exception as e:
            print(f"删除用户 {user_id} 失败: {e}")
    
    print(f"成功删除 {deleted_count} 个用户")

# 注意：这是物理删除，数据会永久丢失
# 如果需要可恢复的删除，请使用 soft_delete 方法
    ''', description="物理删除记录的使用方法", title="delete 使用示例")
    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """
        删除记录（物理删除）
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            是否删除成功
        """
        try:
            db_obj = await self.get(db, id)
            await db.delete(db_obj)
            await db.commit()
            
            logger.info(f"Deleted {self.model.__name__} with id {id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to delete record: {e}")

    async def soft_delete(self, db: AsyncSession, id: Any) -> ModelType:
        """
        软删除记录（仅对SoftDeleteModel有效）
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            软删除后的模型实例
        """
        if not issubclass(self.model, SoftDeleteModel):
            raise DatabaseError(f"{self.model.__name__} does not support soft delete")
        
        try:
            db_obj = await self.get(db, id)
            db_obj.soft_delete()
            await db.commit()
            await db.refresh(db_obj)
            
            logger.info(f"Soft deleted {self.model.__name__} with id {id}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to soft delete {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to soft delete record: {e}")

    async def restore(self, db: AsyncSession, id: Any) -> ModelType:
        """
        恢复软删除的记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            恢复后的模型实例
        """
        if not issubclass(self.model, SoftDeleteModel):
            raise DatabaseError(f"{self.model.__name__} does not support soft delete")
        
        try:
            # 包含已删除记录的查询
            query = select(self.model).where(self.model.id == id)
            result = await db.execute(query)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                raise RecordNotFoundError(f"{self.model.__name__} with id {id} not found")
            
            db_obj.restore()
            await db.commit()
            await db.refresh(db_obj)
            
            logger.info(f"Restored {self.model.__name__} with id {id}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to restore {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to restore record: {e}")

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """
        检查记录是否存在
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            是否存在
        """
        try:
            result = await self.get(db, id, raise_not_found=False)
            return result is not None
        except Exception as e:
            logger.error(f"Failed to check existence of {self.model.__name__} with id {id}: {e}")
            return False

    def _build_filter_conditions(self, filters: Dict[str, Any]) -> List:
        """
        构建过滤条件列表
        
        Args:
            filters: 过滤条件字典
            
        Returns:
            SQLAlchemy条件列表
        """
        conditions = []
        
        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, list):
                    # 列表值使用IN查询
                    conditions.append(getattr(self.model, field).in_(value))
                elif isinstance(value, dict) and "operator" in value:
                    # 复杂查询条件
                    column = getattr(self.model, field)
                    operator = value["operator"]
                    operand = value["value"]
                    
                    if operator == "like":
                        conditions.append(column.like(f"%{operand}%"))
                    elif operator == "ilike":
                        conditions.append(column.ilike(f"%{operand}%"))
                    elif operator == "gt":
                        conditions.append(column > operand)
                    elif operator == "gte":
                        conditions.append(column >= operand)
                    elif operator == "lt":
                        conditions.append(column < operand)
                    elif operator == "lte":
                        conditions.append(column <= operand)
                    elif operator == "ne":
                        conditions.append(column != operand)
                else:
                    # 简单等值查询
                    conditions.append(getattr(self.model, field) == value)
        
        return conditions

    async def bulk_create(
        self, 
        db: AsyncSession, 
        objs_in: List[Union[CreateSchemaType, Dict[str, Any]]]
    ) -> List[ModelType]:
        """
        批量创建记录
        
        Args:
            db: 数据库会话
            objs_in: 输入数据列表
            
        Returns:
            创建的模型实例列表
        """
        try:
            db_objs = []
            for obj_in in objs_in:
                if isinstance(obj_in, dict):
                    create_data = obj_in
                else:
                    create_data = obj_in.model_dump(exclude_unset=True)
                
                db_obj = self.model(**create_data)
                db_objs.append(db_obj)
            
            db.add_all(db_objs)
            await db.commit()
            
            # 刷新所有对象
            for db_obj in db_objs:
                await db.refresh(db_obj)
            
            logger.info(f"Bulk created {len(db_objs)} {self.model.__name__} records")
            return db_objs
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to bulk create {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to bulk create records: {e}")

    def _get_primary_key_value(self, db_obj: ModelType) -> str:
        """获取模型实例的主键值"""
        try:
            # 获取模型的主键列
            primary_keys = []
            for column in self.model.__table__.primary_key.columns:
                pk_value = getattr(db_obj, column.name, None)
                if pk_value is not None:
                    primary_keys.append(str(pk_value))
            
            # 如果有多个主键，用逗号连接
            return ", ".join(primary_keys) if primary_keys else "unknown"
            
        except Exception:
            # 如果获取主键失败，返回默认值
            return "unknown"


class CRUDBase(BaseCRUD[ModelType, PydanticModel, PydanticModel]):
    """简化的CRUD基类，不需要指定Schema类型"""
    pass
