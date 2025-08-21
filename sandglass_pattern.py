def print_sandglass_question_marks(n):
    """
    打印沙漏形状的问号
    n: 沙漏的高度（必须是奇数）
    """
    if n % 2 == 0:
        n += 1  # 确保n是奇数
    
    # 打印上半部分（递减）
    for i in range(n // 2, -1, -1):
        # 打印前导空格
        spaces = " " * (n // 2 - i)
        # 打印问号
        question_marks = "?" * (2 * i + 1)
        print(spaces + question_marks)
    
    # 打印下半部分（递增）
    for i in range(1, n // 2 + 1):
        # 打印前导空格
        spaces = " " * (n // 2 - i)
        # 打印问号
        question_marks = "?" * (2 * i + 1)
        print(spaces + question_marks)

def print_sandglass_question_marks_alternative(n):
    """
    另一种实现方式：使用字符串拼接
    """
    if n % 2 == 0:
        n += 1
    
    # 上半部分
    for i in range(n // 2, -1, -1):
        line = " " * (n // 2 - i) + "?" * (2 * i + 1)
        print(line)
    
    # 下半部分
    for i in range(1, n // 2 + 1):
        line = " " * (n // 2 - i) + "?" * (2 * i + 1)
        print(line)

def print_sandglass_question_marks_compact(n):
    """
    紧凑版本：一行代码实现
    """
    n = n if n % 2 else n + 1
    for i in range(n):
        spaces = abs(n // 2 - i)
        marks = n - 2 * spaces
        print(" " * spaces + "?" * marks)

# 测试函数
if __name__ == "__main__":
    print("=== 沙漏形状问号图案 ===")
    print("\n方法1 - 标准实现 (n=5):")
    print_sandglass_question_marks(5)
    
    print("\n方法2 - 字符串拼接 (n=7):")
    print_sandglass_question_marks_alternative(7)
    
    print("\n方法3 - 紧凑版本 (n=9):")
    print_sandglass_question_marks_compact(9)
    
    print("\n=== 不同大小的沙漏 ===")
    sizes = [3, 5, 7, 9]
    for size in sizes:
        print(f"\n大小 {size}:")
        print_sandglass_question_marks(size)

