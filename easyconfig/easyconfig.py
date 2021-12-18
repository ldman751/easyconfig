#!/usr/bin/env python3
# ! -*- coding:utf-8 -*-
# coding:unicode_escape
"""
jeack_chen@hotmail.com
2021-12
"""

import configparser
import re
from collections import defaultdict
from configparser import NoSectionError, NoOptionError


_UNSET = object()


def can_field(c):
    units = (
        ('\u4e00', '\u9fa5'),
        ('\u0410', '\u044f'),
    )
    for u in units:
        if u[0] <= c <= u[1]:
            return True
    return False


class OptionPack:
    def __init__(self, conf, section, option, value=_UNSET):
        self.conf, self.section, self.option, self.value = conf, section, option, value

    def __call__(self, value=_UNSET):
        try:
            return self.conf.get(self.section, self.option)
        except (NoSectionError, NoOptionError):
            if value is _UNSET and self.value is _UNSET:
                raise
            return value if value is not _UNSET else self.value

    @classmethod
    def to_field_name(cls, option):
        return re.sub(r'\W', '_', option.strip().upper())


class SectionPack:
    def __init__(self, conf, sections):
        self._options = {}
        alias = defaultdict(set)

        for section in sections:
            for field, option in self.setup_section(conf, section, EasyConfig.info.get_options(section)):
                alias[field].add(option)
        if OptionInfo.kDefault not in sections:
            for field, option in self.setup_section(conf, sections[-1], EasyConfig.info.get_options()):
                alias[field].add(option)
        # 去掉有名字冲突的
        for field, options in alias.items():
            if len(options) > 1:
                delattr(self, field)

    def setup_section(self, conf, section, options):
        for arg in options:
            if len(arg) < 2:
                continue
            # section 区分大小写，option 不区分大小写
            option = arg[0]
            self._options[option.upper()] = OptionPack(conf, section, *arg[:-1])
            field = OptionPack.to_field_name(option)
            if field[0].isalpha() or can_field(field[0]):
                yield field, option # alias[field].add(option)
                setattr(self, field, self._options[option.upper()])

    def __call__(self, option: str, *args) -> OptionPack:
        """
        :param option: 需要获取的 option name
        :return: OptionPack
        """
        if option.upper() in self._options:
            return self._options[option.upper()](*args)
        if not hasattr(self, "sections"):
            self.sections = {op.section for op in self._options.values()}
        raise Exception(f"no option:{option} in section:{','.join(self.sections)}")

    def all_options(self):
        res = defaultdict(list)
        for op in self._options.values():
            res[op.section].append(op.option)
        return res


class OptionInfo:
    kDefault = "DEFAULT"

    def __init__(self):
        # in buf: {section: (index, ((options, default, comment) or (options, comment) or (comment), ...)}
        self.buf = {}

    def append(self, section, *options):
        if self.has(section):
            raise Exception(f"Option:append section:'{section}' existed.")
        index = -1 if section == self.kDefault else len(self.buf)
        self.buf[section] = (index, options)

    def has(self, section):
        return section in self.buf


    def get_options(self, section=None):
        """
        :param section:
        :return:
            ((option, default) or (option, ), ...)
        """
        sect = self.kDefault if section is None else section
        if sect == self.kDefault and self.kDefault not in self.buf:
            return tuple()
        return self.buf[sect][-1]

    @staticmethod
    def comment_format(comment):
        if len(comment.strip()) == 0:
            return ""
        return "# " + comment.replace('\n', '\n# ')

    def show(self, *sections):
        for line in self.config_data(*sections):
            print(line)

    def config_data(self, *sections):
        cs = self.buf if len(sections) == 0 else self.buf.fromkeys(sections)
        datas = sorted([(v[0], k, v[-1]) for k, v in cs.items()], key=lambda x: x[0])
        for d in datas:
            yield f"[{d[1]}]"
            for c in d[-1]:
                if len(c[-1]) > 0:
                    yield self.comment_format(c[-1])
                num = len(c)
                if num >= 2:
                    yield f"{c[0]}={'' if num == 2 else '' if c[1] is None else c[1]}"
                yield ""


class EasyConfig:
    info = OptionInfo()

    @classmethod
    def register(cls, section: str, *option_arg):
        """
        :param section:
        :param option_arg: tuple
            ((option, default, comment) or (option, comment) or (comment,), ...)
        :return: cls
        """
        cls.info.append(section, *option_arg)
        return cls

    @classmethod
    def get_info(cls, *sections):
        return '\n'.join(cls.info.config_data(*sections))

    @classmethod
    def section_pack(cls, conf: configparser.ConfigParser, section) -> SectionPack:
        """
        :param conf:
            configparser.ConfigParser
        :param section:
            if type(section) == str: sections = [section,]
            if type(section) == type: sections = [c.__name__ for c in sections.mro() if c != object]
        :return:
            SectionPack
        """
        if type(section) == str:
            sections = [section, ]
        elif type(section) == type:
            sections = [c.__name__ for c in section.mro() if c != object]
            sections.reverse()
        else:
            raise Exception(f"section type not str or type")

        for sect in sections:
            if not cls.info.has(sect):
                raise Exception(f"section:'{sect}' has not been configured.")

        return SectionPack(conf, sections)
