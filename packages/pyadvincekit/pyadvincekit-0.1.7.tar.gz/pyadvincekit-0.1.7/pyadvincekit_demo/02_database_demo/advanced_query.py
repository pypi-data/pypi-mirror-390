#!/usr/bin/env python3
"""
PyAdvanceKit 数据库高级查询演示

包括：
1. 多表关联查询 (JOIN)
2. 嵌套子查询 (Subquery)
3. 聚合查询 (GROUP BY, COUNT, SUM等)
4. 复杂条件查询
5. 原生SQL查询
6. 事务中的复杂查询
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import delete
from sqlalchemy import (
    select, join, func, and_, exists,
    text, case, distinct, union, desc
)
from sqlalchemy.orm import Mapped

from pyadvincekit import (
    get_database, BaseCRUD, BaseModel,
    create_required_string_column, create_optional_string_column,
    create_integer_column, create_decimal_column, create_datetime_column,
    create_boolean_column, create_foreign_key_column
)
from pyadvincekit import init_database
from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


# ==================== 定义示例模型 ====================

class Department(BaseModel):
    """部门模型"""
    __tablename__ = "departments"
    
    name: Mapped[str] = create_required_string_column(100, comment="部门名称")
    description: Mapped[Optional[str]] = create_optional_string_column(500, comment="部门描述")
    budget: Mapped[Optional[Decimal]] = create_decimal_column(precision=15, scale=2, comment="部门预算")


class Employee(BaseModel):
    """员工模型"""
    __tablename__ = "employees"
    
    name: Mapped[str] = create_required_string_column(100, comment="员工姓名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱")
    salary: Mapped[Optional[Decimal]] = create_decimal_column(precision=10, scale=2, comment="薪资")
    hire_date: Mapped[Optional[datetime]] = create_datetime_column(comment="入职日期")
    is_active: Mapped[bool] = create_boolean_column(default=True, comment="是否在职")
    department_id: Mapped[Optional[str]] = create_foreign_key_column("departments.id", comment="部门ID")


class Project(BaseModel):
    """项目模型"""
    __tablename__ = "projects"
    
    name: Mapped[str] = create_required_string_column(200, comment="项目名称")
    description: Mapped[Optional[str]] = create_optional_string_column(1000, comment="项目描述")
    budget: Mapped[Optional[Decimal]] = create_decimal_column(precision=15, scale=2, comment="项目预算")
    start_date: Mapped[Optional[datetime]] = create_datetime_column(comment="开始日期")
    end_date: Mapped[Optional[datetime]] = create_datetime_column(comment="结束日期")
    status: Mapped[str] = create_required_string_column(50, comment="项目状态")


class ProjectAssignment(BaseModel):
    """项目分配模型"""
    __tablename__ = "project_assignments"
    
    employee_id: Mapped[str] = create_foreign_key_column("employees.id", comment="员工ID")
    project_id: Mapped[str] = create_foreign_key_column("projects.id", comment="项目ID")
    role: Mapped[str] = create_required_string_column(100, comment="角色")
    hours_allocated: Mapped[Optional[int]] = create_integer_column(comment="分配工时")
    start_date: Mapped[Optional[datetime]] = create_datetime_column(comment="参与开始日期")


# ==================== 高级查询服务类 ====================

class AdvancedQueryService:
    """高级查询服务"""
    
    def __init__(self):
        self.department_crud = BaseCRUD(Department)
        self.employee_crud = BaseCRUD(Employee)
        self.project_crud = BaseCRUD(Project)
        self.assignment_crud = BaseCRUD(ProjectAssignment)
    
    async def demo_basic_joins(self):
        """演示基本的多表关联查询"""
        print("\n" + "="*60)
        print("🔗 基本多表关联查询演示")
        print("="*60)
        
        async with get_database() as db:
            # 1. INNER JOIN - 查询员工及其部门信息
            print("\n1️⃣ INNER JOIN - 员工及部门信息:")
            query = (
                select(Employee.name, Employee.email, Employee.salary, Department.name.label('dept_name'))
                .select_from(join(Employee, Department, Employee.department_id == Department.id))
                .where(Employee.is_active == True)
                .order_by(Employee.name)
            )
            
            result = await db.execute(query)
            employees_with_dept = result.fetchall()
            
            for emp in employees_with_dept:
                print(f"  👤 {emp.name} ({emp.email}) - {emp.dept_name} - 薪资: {emp.salary}")
            
            # 2. LEFT JOIN - 查询所有员工（包括没有部门的）
            print("\n2️⃣ LEFT JOIN - 所有员工（包括无部门）:")
            query = (
                select(Employee.name, Employee.email, Department.name.label('dept_name'))
                .select_from(Employee.__table__.join(Department.__table__, Employee.department_id == Department.id, isouter=True))
                .order_by(Employee.name)
            )
            
            result = await db.execute(query)
            all_employees = result.fetchall()
            
            for emp in all_employees:
                dept_name = emp.dept_name or "无部门"
                print(f"  👤 {emp.name} - {dept_name}")
    
    async def demo_subqueries(self):
        """演示子查询"""
        print("\n" + "="*60)
        print("🔍 子查询演示")
        print("="*60)
        
        async with get_database() as db:
            # 1. 标量子查询 - 查询高于平均薪资的员工
            print("\n1️⃣ 标量子查询 - 高于平均薪资的员工:")
            
            # 先计算平均薪资
            avg_salary_query = select(func.avg(Employee.salary)).where(Employee.is_active == True)
            
            # 查询高于平均薪资的员工
            query = (
                select(Employee.name, Employee.salary)
                .where(
                    and_(
                        Employee.is_active == True,
                        Employee.salary > avg_salary_query.scalar_subquery()
                    )
                )
                .order_by(desc(Employee.salary))
            )
            
            result = await db.execute(query)
            high_salary_employees = result.fetchall()
            
            for emp in high_salary_employees:
                print(f"  💰 {emp.name} - 薪资: {emp.salary}")
            
            # 2. EXISTS 子查询 - 查询有项目分配的员工
            print("\n2️⃣ EXISTS 子查询 - 有项目分配的员工:")
            
            exists_subquery = (
                select(1)
                .select_from(ProjectAssignment)
                .where(ProjectAssignment.employee_id == Employee.id)
            )
            
            query = (
                select(Employee.name, Employee.email)
                .where(exists(exists_subquery))
                .order_by(Employee.name)
            )
            
            result = await db.execute(query)
            employees_with_projects = result.fetchall()
            
            for emp in employees_with_projects:
                print(f"  🎯 {emp.name} ({emp.email})")
            
            # 3. IN 子查询 - 查询特定部门的员工
            print("\n3️⃣ IN 子查询 - 技术相关部门的员工:")
            
            tech_dept_subquery = (
                select(Department.id)
                .where(Department.name.like('%技术%'))
            )
            
            query = (
                select(Employee.name, Employee.email)
                .where(Employee.department_id.in_(tech_dept_subquery))
                .order_by(Employee.name)
            )
            
            result = await db.execute(query)
            tech_employees = result.fetchall()
            
            for emp in tech_employees:
                print(f"  💻 {emp.name} ({emp.email})")
    
    async def demo_aggregation_queries(self):
        """演示聚合查询"""
        print("\n" + "="*60)
        print("📊 聚合查询演示")
        print("="*60)
        
        async with get_database() as db:
            # 1. 基本聚合 - 部门统计
            print("\n1️⃣ 部门员工统计:")
            
            query = (
                select(
                    Department.name.label('dept_name'),
                    func.count(Employee.id).label('employee_count'),
                    func.avg(Employee.salary).label('avg_salary'),
                    func.sum(Employee.salary).label('total_salary'),
                    func.min(Employee.salary).label('min_salary'),
                    func.max(Employee.salary).label('max_salary')
                )
                .select_from(join(Employee, Department, Employee.department_id == Department.id))
                .where(Employee.is_active == True)
                .group_by(Department.id, Department.name)
                .having(func.count(Employee.id) > 0)
                .order_by(desc('employee_count'))
            )
            
            result = await db.execute(query)
            dept_stats = result.fetchall()
            
            for stat in dept_stats:
                print(f"  🏢 {stat.dept_name}:")
                print(f"    👥 员工数: {stat.employee_count}")
                print(f"    💰 平均薪资: {stat.avg_salary:.2f}")
                print(f"    💸 薪资总和: {stat.total_salary:.2f}")
                print(f"    📉 最低薪资: {stat.min_salary:.2f}")
                print(f"    📈 最高薪资: {stat.max_salary:.2f}")
            
            # 2. 复杂聚合 - 项目参与统计
            print("\n2️⃣ 员工项目参与统计:")
            
            query = (
                select(
                    Employee.name,
                    func.count(distinct(ProjectAssignment.project_id)).label('project_count'),
                    func.sum(ProjectAssignment.hours_allocated).label('total_hours'),
                    func.group_concat(Project.name, ', ').label('project_names')
                )
                .select_from(
                    Employee.__table__
                    .join(ProjectAssignment.__table__, Employee.id == ProjectAssignment.employee_id)
                    .join(Project.__table__, ProjectAssignment.project_id == Project.id)
                )
                .group_by(Employee.id, Employee.name)
                .having(func.count(ProjectAssignment.project_id) > 0)
                .order_by(desc('project_count'))
            )
            
            result = await db.execute(query)
            employee_project_stats = result.fetchall()
            
            for stat in employee_project_stats:
                print(f"  👤 {stat.name}:")
                print(f"    🎯 参与项目数: {stat.project_count}")
                print(f"    ⏰ 总分配工时: {stat.total_hours or 0}")
                print(f"    📋 项目列表: {stat.project_names or '无'}")
    
    async def demo_complex_conditions(self):
        """演示复杂条件查询"""
        print("\n" + "="*60)
        print("🎛️ 复杂条件查询演示")
        print("="*60)
        
        async with get_database() as db:
            # 1. 复合条件查询
            print("\n1️⃣ 复合条件查询 - 高薪且有项目的活跃员工:")
            
            query = (
                select(Employee.name, Employee.salary, Employee.email)
                .where(
                    and_(
                        Employee.is_active == True,
                        Employee.salary > 8000,
                        exists(
                            select(1)
                            .select_from(ProjectAssignment)
                            .where(ProjectAssignment.employee_id == Employee.id)
                        )
                    )
                )
                .order_by(desc(Employee.salary))
            )
            
            result = await db.execute(query)
            qualified_employees = result.fetchall()
            
            for emp in qualified_employees:
                print(f"  ⭐ {emp.name} - 薪资: {emp.salary} ({emp.email})")
            
            # 2. CASE WHEN 条件查询
            print("\n2️⃣ CASE WHEN 条件查询 - 员工薪资等级:")
            
            salary_level = case(
                (Employee.salary >= 15000, "高级"),
                (Employee.salary >= 10000, "中级"),
                (Employee.salary >= 5000, "初级"),
                else_="实习"
            ).label('salary_level')
            
            query = (
                select(
                    Employee.name,
                    Employee.salary,
                    salary_level,
                    Department.name.label('dept_name')
                )
                .select_from(join(Employee, Department, Employee.department_id == Department.id, isouter=True))
                .where(Employee.is_active == True)
                .order_by(desc(Employee.salary))
            )
            
            result = await db.execute(query)
            employees_with_level = result.fetchall()
            
            for emp in employees_with_level:
                dept = emp.dept_name or "无部门"
                print(f"  🏆 {emp.name} - {emp.salary_level} ({emp.salary}) - {dept}")
            
            # 3. 日期范围查询
            print("\n3️⃣ 日期范围查询 - 近期入职员工:")
            
            from datetime import datetime, timedelta
            recent_date = datetime.now() - timedelta(days=365)  # 一年内
            
            query = (
                select(Employee.name, Employee.hire_date, Employee.email)
                .where(
                    and_(
                        Employee.hire_date >= recent_date,
                        Employee.is_active == True
                    )
                )
                .order_by(desc(Employee.hire_date))
            )
            
            result = await db.execute(query)
            recent_hires = result.fetchall()
            
            for emp in recent_hires:
                print(f"  🆕 {emp.name} - 入职: {emp.hire_date} ({emp.email})")
    
    async def demo_window_functions(self):
        """演示窗口函数"""
        print("\n" + "="*60)
        print("🪟 窗口函数演示")
        print("="*60)
        
        async with get_database() as db:
            # 1. ROW_NUMBER - 部门内薪资排名
            print("\n1️⃣ 部门内薪资排名:")
            
            query = (
                select(
                    Employee.name,
                    Employee.salary,
                    Department.name.label('dept_name'),
                    func.row_number().over(
                        partition_by=Employee.department_id,
                        order_by=desc(Employee.salary)
                    ).label('salary_rank')
                )
                .select_from(join(Employee, Department, Employee.department_id == Department.id))
                .where(Employee.is_active == True)
                .order_by(Department.name, 'salary_rank')
            )
            
            result = await db.execute(query)
            ranked_employees = result.fetchall()
            
            current_dept = None
            for emp in ranked_employees:
                if current_dept != emp.dept_name:
                    current_dept = emp.dept_name
                    print(f"\n  🏢 {current_dept}:")
                
                print(f"    #{emp.salary_rank} {emp.name} - {emp.salary}")
            
            # 2. DENSE_RANK - 全公司薪资排名
            print("\n2️⃣ 全公司薪资排名 (DENSE_RANK):")
            
            query = (
                select(
                    Employee.name,
                    Employee.salary,
                    func.dense_rank().over(order_by=desc(Employee.salary)).label('rank'),
                    func.percent_rank().over(order_by=desc(Employee.salary)).label('percentile')
                )
                .where(Employee.is_active == True)
                .order_by('rank')
                .limit(10)  # 只显示前10名
            )
            
            result = await db.execute(query)
            top_employees = result.fetchall()
            
            for emp in top_employees:
                percentile = f"{emp.percentile:.1%}" if emp.percentile else "N/A"
                print(f"  🏆 #{emp.rank} {emp.name} - {emp.salary} (前{percentile})")
    
    async def demo_raw_sql_queries(self):
        """演示原生SQL查询"""
        print("\n" + "="*60)
        print("🔧 原生SQL查询演示")
        print("="*60)
        
        async with get_database() as db:
            # 1. 复杂统计查询
            print("\n1️⃣ 复杂统计查询 - 部门项目参与度:")
            
            raw_sql = text("""
                SELECT 
                    d.name as dept_name,
                    COUNT(DISTINCT e.id) as employee_count,
                    COUNT(DISTINCT pa.project_id) as project_count,
                    COALESCE(SUM(pa.hours_allocated), 0) as total_hours,
                    ROUND(AVG(e.salary), 2) as avg_salary,
                    ROUND(
                        CAST(COUNT(DISTINCT pa.project_id) AS FLOAT) / 
                        NULLIF(COUNT(DISTINCT e.id), 0), 2
                    ) as projects_per_employee
                FROM departments d
                LEFT JOIN employees e ON d.id = e.department_id AND e.is_active = true
                LEFT JOIN project_assignments pa ON e.id = pa.employee_id
                GROUP BY d.id, d.name
                HAVING COUNT(DISTINCT e.id) > 0
                ORDER BY projects_per_employee DESC, total_hours DESC
            """)
            
            result = await db.execute(raw_sql)
            dept_project_stats = result.fetchall()
            
            for stat in dept_project_stats:
                print(f"  🏢 {stat.dept_name}:")
                print(f"    👥 员工数: {stat.employee_count}")
                print(f"    🎯 参与项目数: {stat.project_count}")
                print(f"    ⏰ 总工时: {stat.total_hours}")
                print(f"    💰 平均薪资: {stat.avg_salary}")
                print(f"    📊 人均项目数: {stat.projects_per_employee}")
            
            # 2. 带参数的原生SQL
            print("\n2️⃣ 带参数的原生SQL - 查询特定薪资范围的员工:")
            
            min_salary = 8000
            max_salary = 15000
            
            raw_sql = text("""
                SELECT 
                    e.name,
                    e.salary,
                    d.name as dept_name,
                    COUNT(pa.project_id) as project_count
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                LEFT JOIN project_assignments pa ON e.id = pa.employee_id
                WHERE e.salary BETWEEN :min_salary AND :max_salary
                  AND e.is_active = true
                GROUP BY e.id, e.name, e.salary, d.name
                ORDER BY e.salary DESC
            """)
            
            result = await db.execute(raw_sql, {
                "min_salary": min_salary,
                "max_salary": max_salary
            })
            salary_range_employees = result.fetchall()
            
            for emp in salary_range_employees:
                dept = emp.dept_name or "无部门"
                print(f"  💼 {emp.name} - {emp.salary} - {dept} - 项目数: {emp.project_count}")
    
    async def demo_union_queries(self):
        """演示UNION查询"""
        print("\n" + "="*60)
        print("🔗 UNION查询演示")
        print("="*60)
        
        async with get_database() as db:
            # UNION查询 - 合并不同来源的数据
            print("\n1️⃣ UNION查询 - 高薪员工和项目经理:")
            
            # 高薪员工查询
            high_salary_query = (
                select(
                    Employee.name,
                    Employee.email,
                    func.concat('高薪员工 - ', Employee.salary).label('category')
                )
                .where(
                    and_(
                        Employee.salary > 12000,
                        Employee.is_active == True
                    )
                )
            )
            
            # 项目经理查询
            project_manager_query = (
                select(
                    Employee.name,
                    Employee.email,
                    func.concat('项目经理 - ', ProjectAssignment.role).label('category')
                )
                .select_from(
                    join(Employee, ProjectAssignment, Employee.id == ProjectAssignment.employee_id)
                )
                .where(
                    and_(
                        ProjectAssignment.role.like('%经理%'),
                        Employee.is_active == True
                    )
                )
            )
            
            # UNION查询
            union_query = union(high_salary_query, project_manager_query).order_by('name')
            
            result = await db.execute(union_query)
            union_results = result.fetchall()
            
            for person in union_results:
                print(f"  🌟 {person.name} ({person.email}) - {person.category}")


# ==================== 主函数和测试 ====================

async def create_sample_data():
    """创建示例数据"""
    print("📝 创建示例数据...")
    
    async with get_database() as db:
        # 先清空现有数据（按依赖顺序）
        await db.execute(delete(ProjectAssignment))
        await db.execute(delete(Project))
        await db.execute(delete(Employee))
        await db.execute(delete(Department))
        await db.commit()
        # 创建部门
        departments = [
            Department(name="技术部", description="负责产品开发", budget=Decimal("500000")),
            Department(name="市场部", description="负责市场推广", budget=Decimal("300000")),
            Department(name="人事部", description="负责人力资源", budget=Decimal("200000")),
        ]
        
        for dept in departments:
            db.add(dept)
        
        await db.flush()  # 获取ID
        
        # 创建员工
        employees = [
            Employee(name="张三", email="zhangsan@company.com", salary=Decimal("12000"), 
                    hire_date=datetime(2023, 1, 15), department_id=departments[0].id),
            Employee(name="李四", email="lisi@company.com", salary=Decimal("15000"), 
                    hire_date=datetime(2022, 6, 1), department_id=departments[0].id),
            Employee(name="王五", email="wangwu@company.com", salary=Decimal("8000"), 
                    hire_date=datetime(2023, 8, 20), department_id=departments[1].id),
            Employee(name="赵六", email="zhaoliu@company.com", salary=Decimal("10000"), 
                    hire_date=datetime(2023, 3, 10), department_id=departments[2].id),
        ]
        
        for emp in employees:
            db.add(emp)
        
        await db.flush()
        
        # 创建项目
        projects = [
            Project(name="电商平台", description="在线购物平台", budget=Decimal("1000000"), 
                   start_date=datetime(2023, 1, 1), status="进行中"),
            Project(name="移动APP", description="移动端应用", budget=Decimal("500000"), 
                   start_date=datetime(2023, 3, 1), status="计划中"),
        ]
        
        for proj in projects:
            db.add(proj)
        
        await db.flush()
        
        # 创建项目分配
        assignments = [
            ProjectAssignment(employee_id=employees[0].id, project_id=projects[0].id, 
                            role="开发工程师", hours_allocated=160),
            ProjectAssignment(employee_id=employees[1].id, project_id=projects[0].id, 
                            role="项目经理", hours_allocated=120),
            ProjectAssignment(employee_id=employees[1].id, project_id=projects[1].id, 
                            role="技术负责人", hours_allocated=80),
        ]
        
        for assignment in assignments:
            db.add(assignment)
        
        await db.commit()
        print("✅ 示例数据创建完成")


async def main():
    """主函数"""
    print("🚀 PyAdvanceKit 数据库高级查询演示")
    await init_database()

    # 创建示例数据
    await create_sample_data()
    
    # 创建查询服务
    query_service = AdvancedQueryService()
    
    # 运行各种查询演示
    await query_service.demo_basic_joins()
    await query_service.demo_subqueries()
    await query_service.demo_aggregation_queries()
    await query_service.demo_complex_conditions()
    await query_service.demo_window_functions()
    await query_service.demo_raw_sql_queries()
    await query_service.demo_union_queries()
    
    print(f"\n{'🎉' * 20}")
    print("PyAdvanceKit 数据库高级查询演示完成！")
    print(f"{'🎉' * 20}")


if __name__ == "__main__":
    asyncio.run(main())
