"""演示装饰器（Decorator）的示例脚本。

通过给 Student 和 Teacher 的方法添加“日志记录”和“耗时统计”装饰器，
向学生深入浅出地解释 Python 装饰器的基本原理、语法糖（@ 符号）以及实际应用。
"""

import functools
import time
from typing import Any, Callable

# =====================================================================
# 1. 装饰器的定义
# =====================================================================


def log_activity(func: Callable[..., Any]) -> Callable[..., Any]:
    """日志记录装饰器 (Decorator)。

    在不改变原函数代码的前提下，在函数执行的前后自动打印日志信息。
    """

    @functools.wraps(func)  # 保留原函数（被装饰函数）的元数据（如名称、文档字符串）
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 在类方法中，第一个参数 args[0] 通常是实例对象本身 (self)
        instance = args[0]
        class_name = type(instance).__name__
        person_name = getattr(instance, "name", "未知")

        print(
            f"[日志系统] 自动拦截：{class_name}【{person_name}】开始执行 '{func.__name__}' 方法..."
        )

        # 执行被装饰的原始函数
        result = func(*args, **kwargs)

        print(
            f"[日志系统] 自动拦截：{class_name}【{person_name}】成功完成了 '{func.__name__}' 的执行。"
        )
        return result

    return wrapper


def time_spent(func: Callable[..., Any]) -> Callable[..., Any]:
    """耗时统计装饰器 (Decorator)。

    用于计算并输出被装饰函数的执行时间。在几何计算、冲突检测或大批量BIM数据渲染时非常实用。
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()

        # 执行原函数
        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"[计时系统] 性能报告：'{func.__name__}' 实际耗时 {elapsed:.4f} 秒。")
        return result

    return wrapper


# =====================================================================
# 2. 定义人类、学生类与教师类，并应用装饰器
# =====================================================================


class Person:
    """人类基类"""

    def __init__(self, name: str, age: int) -> None:
        self.name: str = name
        self.age: int = age


class Student(Person):
    """学生子类"""

    def __init__(self, name: str, age: int, student_id: str) -> None:
        super().__init__(name, age)
        self.student_id: str = student_id

    # 多个装饰器可以叠加，执行顺序为自上而下 (即先外层后内层)
    @log_activity
    @time_spent
    def study(self, course_name: str) -> None:
        """学生特有的学习方法。"""
        print(f"  (学习中) 学生 {self.name} (学号: {self.student_id}) 正在努力阅读《{course_name}》课件...")
        time.sleep(0.5)  # 模拟学习花费了 0.5 秒


class Teacher(Person):
    """教师子类"""

    def __init__(self, name: str, age: int, subject: str) -> None:
        super().__init__(name, age)
        self.subject: str = subject

    @log_activity
    @time_spent
    def prepare_lesson(self, topic: str) -> None:
        """教师特有的备课方法。"""
        print(f"  (备课中) 教师 {self.name} 正在制作《{self.subject} - {topic}》的教学 PPT...")
        time.sleep(0.8)  # 模拟备课花费了 0.8 秒


# 提供小写别名以兼容教学场景
person = Person
student = Student
teacher = Teacher


# =====================================================================
# 3. 教学运行与概念解释
# =====================================================================


def main() -> None:
    """演示装饰器效果的主函数。"""
    print("=" * 60)
    print(" 演示：Python 中的装饰器 (Decorators) ")
    print("=" * 60)

    print(
        "(*) 什么是装饰器？\n"
        "   装饰器本质上是一个 Python 函数，它可以让其他函数在不需要做任何代码修改的前提下，\n"
        "   增加额外功能。例如在土木计算中，我们可以用来统计某段计算代码的耗时、记录日志或进行权限校验。\n"
    )
    print("-" * 50)

    # 1. 实例化学生并调用被装饰的 study 方法
    s = Student("小明", 20, "2026001")
    print(f"[调用 student.study()]:")
    s.study("土木人的Python课")
    print("-" * 50)

    # 2. 实例化教师并调用被装饰的 prepare_lesson 方法
    t = Teacher("李老师", 42, "工程三维几何制图")
    print(f"[调用 teacher.prepare_lesson()]:")
    t.prepare_lesson("Python 装饰器与切面编程")
    print("-" * 50)

    print(
        "(*) 核心原理说明：\n"
        "   当我们在方法上写下 `@log_activity` 时，Python 自动将该方法包装成了：\n"
        "   method = log_activity(method)\n"
        "   这样，在调用 `s.study(...)` 时，实际上是在运行 `log_activity` 内部定义的 `wrapper` 函数，\n"
        "   它自动替我们处理了日志输出与耗时统计的逻辑。\n"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
