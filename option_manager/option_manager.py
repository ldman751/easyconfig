#!/usr/bin/env python3
# ! -*- coding:utf-8 -*-
# coding:unicode_escape
# author:jeack_chen@hotmail.com

import re


class InfoManager:
    def __init__(self):
        self.buf = {}

    def append(self, section, *options):
        # if section in self.buf:
        #     self.buf[section].update
        self.buf[section] = options

    @staticmethod
    def describe_format(describe):
        if len(describe.strip()) == 0:
            return ""
        return "# " + describe.replace('\n', '\n# ')

    def show(self, *args):
        cs = self.buf if len(args) == 0 else self.buf.fromkeys(args)
        for k, v in cs.items():
            print(f"[{k}]")
            for c in v:
                if len(c[-1]) > 0:
                    print(self.describe_format(c[-1]))
                num = len(c)
                if num >= 2:
                    print(f"{c[0]}={'' if num == 2 else c[1]}")
                print()


class OptionPack:
    def __init__(self, section, option, value=''):
        self.section, self.option, self.value = section, option, value

    def __call__(self, value=None):
        return self.section.get(self.option, value if value is not None else self.value)


class OptionManager:
    """
    example:
        @OptionManager.options(("charset", "utf-8", "文档编码"))
        class ParseBase:
            def __int__(self):
                ...
                # 需要添加下面语句，将 option 与 self 绑定
                self.setup_option(self, conf)
                # 绑定后可以直接使用 option 了
                print(self.CHARSET()) # output: utf-8

    test: OptionManager.info.show()
        [ParseBase]
        # 文档编码
        charset=utf-8
    """
    info = InfoManager()

    @classmethod
    def options(cls, *args, section_name=None):
        """
        :param args:
            ((option,default_value,describe) or (option,describe,) or (describe,),)
        :param section_name:
            if section_name is None,
                default_section_name = target_class.__name__
            If there is a class with the same name in the project, then you need to set this section_name
        :return:
        """

        def wrapper(target_cls):
            default_section_name = section_name if section_name is not None else target_cls.__name__

            @staticmethod
            def setup_option(owner, conf, strict=True, section_name=default_section_name, args=args):
                cls.info.append(section_name, *args)
                if section_name not in conf:
                    if strict:
                        raise Exception(
                            f"Exception: In the configuration file is not found in the section:{section_name}"
                            " {target_cls.__name__}:setup_option")
                    section = {}
                else:
                    section = conf[section_name]
                for c in args:
                    num = len(c)
                    if num >= 2:
                        setattr(owner, re.sub(r'\W', '_', c[0].strip().upper()), OptionPack(section, c[0], None if num == 2 else c[1]))
                return section

            setattr(target_cls, 'setup_option', setup_option)
            cls.info.append(default_section_name, *args)
            return target_cls

        return wrapper
