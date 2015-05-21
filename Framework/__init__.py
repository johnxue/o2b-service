version = "0.2.0"
version_info = (0, 2, 0, 2)

# Ver 0,2,0,2

# 变更日期： 2015.05.19
# (1) 修复dbMysql.py update & delete 对ids的判断及处理bug

# 变更日期: 2015.04.21
# 增强了CURD.save 功能，确保可以按照指定的key值去修改（以前只能按照ID）

# 变更日期： 2015.04.18
#(1)修复 CURD.find 分页处理函数的Bug;
#(2)新增CURD.find返回时自动带上struct属性，如果是分页显示的会再自动带上count属性；
#(3)采用traceback.print_exc()增强代码调试在Debug I/O中的报错指引能力；
#(4)在Debug I/O 中直接输出 SQL 语句；
