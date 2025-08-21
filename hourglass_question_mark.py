# 沙漏形状问号打印算法
def print_hourglass_question_mark(height):
    """
    打印沙漏形状的问号
    height: 沙漏的总高度（必须是奇数）
    """
    if height % 2 == 0:
        height += 1  
    
    mid = height // 2 
    
    for i in range(height):
        if i <= mid:

            spaces = i
            question_marks = height - 2 * i
        else:
   
            spaces = height - 1 - i
            question_marks = 2 * (i - mid) + 1
        

        print(" " * spaces, end="")
  
        print("?" * question_marks)

def print_hourglass_question_mark_advanced(height, char="?"):
    """
    高级版本：可自定义字符的沙漏形状
    height: 沙漏的总高度
    char: 用于构建沙漏的字符
    """
    if height % 2 == 0:
        height += 1
    
    mid = height // 2
    
    for i in range(height):
        if i <= mid:
            spaces = i
            chars = height - 2 * i
        else:
            spaces = height - 1 - i
            chars = 2 * (i - mid) + 1
        
        line = " " * spaces + char * chars
        print(line)

def print_hourglass_question_mark_with_border(height, border_char="*"):
    """
    带边框的沙漏形状问号
    height: 沙漏的总高度
    border_char: 边框字符
    """
    if height % 2 == 0:
        height += 1
    
    width = height
    mid = height // 2
    
    # 打印上边框
    print(border_char * (width + 2))
    
    for i in range(height):
        if i <= mid:
            spaces = i
            question_marks = height - 2 * i
        else:
            spaces = height - 1 - i
            question_marks = 2 * (i - mid) + 1
        
        # 构建行内容
        line = " " * spaces + "?" * question_marks
        # 添加左右边框
        line = border_char + line + border_char
        print(line)
    
    # 打印下边框
    print(border_char * (width + 2))

# 测试函数
def test_hourglass_patterns():
    """测试各种沙漏形状"""
    print("=== 基础沙漏问号 (高度=7) ===")
    print_hourglass_question_mark(7)
    
    print("\n=== 基础沙漏问号 (高度=9) ===")
    print_hourglass_question_mark(9)
    
    print("\n=== 使用星号的沙漏 (高度=7) ===")
    print_hourglass_question_mark_advanced(7, "*")
    
    print("\n=== 带边框的沙漏问号 (高度=7) ===")
    print_hourglass_question_mark_with_border(7)

if __name__ == "__main__":
    test_hourglass_patterns()
