## 创建 EasyConfig 原因
### 获取一个配置值太过繁琐
```
    old: conf[section].get('option', default_value))
    vs.
    new: section_pack.OPTION() or section_pack("option")
```
### 维护配置文件，繁琐易遗漏。使用 OptionManager 可以直接生成配置
```python
    EasyConfig.get_info()
```

## EasyConfig 使用说明
### 向 EasyConfig 注册ini数据 
    数据包括：section 和(配置项、默认值、配置说明) 三元组
```python
    EasyConfig\
        .register(section, 
                 (option1, default, comment) or (option1, comment) or (comment,),
                 ...
                  )
```

### 获取 SectionPack
```python
    sp = EasyConfig.section_pack(conf, section)
```    
    section 必须是已经在 EasyConfig 注册过的
        如果曾以 类名 在 EasyConfig 注册过，可以将 类对象 作为 section 传入。EasyConfig 会自动关联其父类 section

    SectionPack 会尽量将 option 关联成 SectionPack 的实例属性，方便使用。
```python
       # 正常读取配置option_a
       self.assertEqual(a.sp.OPTION_A(), self.conf.get('DemoA', 'option_a'))
```

# 详情
    参见 ：history.lst, test/test.py

        