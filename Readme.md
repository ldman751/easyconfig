# 创建 OptionManager 的有两个原因
## 获取一个配置值太过繁琐
```
    old: section.get(option, default_value))
    vs.
    new: OPTION() or OPTION(default_value)
```
## 维护配置文件，繁琐易遗漏。使用 OptionManager 可以直接生成配置
```commandline
    OptionManager.info.show()
```

# OptionManager 使用说明
## OptionManager.options
    这是带参数的装饰器，带有两个参数：args, strict, section_name
        args 是 option 列表 :(option_name, default_value, describe),...
            default_value，可以省略。省略时等价于：default_value=None
            option_name为设置时，生成配置文件时，会加入: f“# {describe}
                如果此时 describe 为空，会在配置文件加入一空行
        section_name:
            默认为None，这是会采用target_class.__name__代替
            当项目中存在同名class时，这时设置不同的section_name比较好
    OptionManager.options 会在被装饰类taget_class中添加静态方法：setup_option

## target_class.setup_option
    您应该在target_class.__init__中调用: setup_option
    setup_option 有五个参数
        owner - 此方法，会将所有args包含option绑定成owner的实例成员，
                option 作为 owner 的成员名大写
                option 以 OptionPack 实例作为 owner 的成员
        conf  - configparser.ConfigParser
        section_name - 调用时通常不用设置，使用默认值
        args  - 调用时通常不用设置，使用默认值
        strict 默认为：True
            True，如果config对应的section不存在时，、会抛异常
            False，如果config对应的section不存在，设置：section={}
            
# 实例
    参见 ：test/test.py

        