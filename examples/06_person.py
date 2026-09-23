"""演示类继承（Inheritance）的示例脚本。

通过 person (人类)、student (学生) 和 teacher (教师) 的关系，
向学生展示 Python 中如何通过继承减少重复代码、实现代码复用和多态。
"""


class Person:
    """人类基类（父类）"""

    def __init__(self, name: str, age: int) -> None:
        """初始化人的基本属性。

        Args:
            name: 姓名
            age: 年龄
        """
        self.name: str = name
        self.age: int = age

    def introduce(self) -> str:
        """自我介绍。"""
        return f"你好，我叫 {self.name}，今年 {self.age} 岁。"

    def perform_activity(self) -> str:
        """日常活动。"""
        return f"{self.name} 正在进行日常活动。"


class Student(Person):
    """学生子类，继承自 Person 基类。"""

    def __init__(self, name: str, age: int, student_id: str) -> None:
        """初始化学生，并调用父类构造函数。

        Args:
            name: 姓名
            age: 年龄
            student_id: 学号
        """
        # super() 指向父类 Person，这里调用父类的构造函数以初始化姓名和年龄
        super().__init__(name, age)
        self.student_id: str = student_id

    def introduce(self) -> str:
        """重写父类的 introduce 方法，展示多态。"""
        # 调用父类的自我介绍，并在此基础上增加学生特有的属性
        base_intro = super().introduce()
        return f"{base_intro} 我是一名学生，学号是 {self.student_id}。"

    def perform_activity(self) -> str:
        """重写父类的日常活动方法。"""
        return f"学生 {self.name} 正在认真学习《土木人的Python课》。"


class Teacher(Person):
    """教师子类，继承自 Person 基类。"""

    def __init__(self, name: str, age: int, subject: str) -> None:
        """初始化教师，并调用父类构造函数。

        Args:
            name: 姓名
            age: 年龄
            subject: 授课科目
        """
        super().__init__(name, age)
        self.subject: str = subject

    def introduce(self) -> str:
        """重写父类的 introduce 方法。"""
        base_intro = super().introduce()
        return f"{base_intro} 我是一名教师，教的科目是 {self.subject}。"

    def perform_activity(self) -> str:
        """重写父类的日常活动方法。"""
        return f"教师 {self.name} 正在为学生准备《BIM几何数据渲染及运算》的教案。"


# 为兼容小写拼写的类名，提供小写别名以便于教学演示
person = Person
student = Student
teacher = Teacher


def main() -> None:
    """运行类继承演示的主函数。"""
    print("=" * 60)
    print(" 演示：Python 中的类继承 (Class Inheritance) ")
    print("=" * 60)

    # 1. 实例化父类 (Person)
    print("[1] 实例化父类 Person:")
    p = Person("张工", 35)
    print(p.introduce())
    print(p.perform_activity())
    print("-" * 50)

    # 2. 实例化子类 Student 并展示属性与方法继承
    print("[2] 实例化子类 Student (继承并重写方法):")
    s = Student("小明", 20, "2026001")
    # 即使 Student 中没有直接在属性列表里写 name 和 age，它也完美继承了它们
    print(f"-> 继承的属性: name={s.name}, age={s.age}")
    print(s.introduce())
    print(s.perform_activity())
    print("-" * 50)

    # 3. 实例化子类 Teacher
    print("[3] 实例化子类 Teacher:")
    t = Teacher("李教授", 48, "工程制图与参数化建模")
    print(f"-> 继承的属性: name={t.name}, age={t.age}")
    print(t.introduce())
    print(t.perform_activity())
    print("-" * 50)

    # 4. 类型检查 (isinstance 和 issubclass)
    print("[4] 类型的关系判定:")
    print(f"Student 是 Person 的子类吗？ {issubclass(Student, Person)}")
    print(f"Teacher 是 Person 的子类吗？ {issubclass(Teacher, Person)}")
    print(f"学生小明 (s) 是 Student 类型吗？ {isinstance(s, Student)}")
    # 子类的实例也属于父类类型，这就是多态和继承的基础
    print(f"学生小明 (s) 也是 Person 类型吗？ {isinstance(s, Person)}")
    print(f"教师李教授 (t) 也是 Person 类型吗？ {isinstance(t, Person)}")
    print("=" * 60)


if __name__ == "__main__":
    main()