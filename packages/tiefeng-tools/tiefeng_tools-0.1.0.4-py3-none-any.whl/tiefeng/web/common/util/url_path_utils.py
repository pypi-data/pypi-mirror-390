import re
from functools import lru_cache
from urllib.parse import quote, unquote


def is_path_ignored(path: str, ignore_paths: list[str]) -> bool:
    """
    判断路径是否在忽略列表中（支持通配符匹配）
    :param path: 请求路径
    :param ignore_paths: 忽略路径列表
    :return: 是否忽略
    """
    # 规范化路径，确保以/开头
    normalized_path = path if path.startswith('/') else '/' + path

    for ignore_path in ignore_paths:
        # 精确匹配
        if normalized_path == ignore_path:
            return True

        # 通配符匹配
        if '*' in ignore_path:
            if _wildcard_match_simple(normalized_path, ignore_path):
                return True

    return False


def _wildcard_match_simple(path: str, pattern: str) -> bool:
    """
    简化的通配符匹配方法
    """
    # 特殊处理 /** 模式
    if pattern == '/**':
        return True

    # 处理以 /** 结尾的模式
    if pattern.endswith('/**'):
        base_pattern = pattern[:-3]  # 移除 /**
        # 检查路径是否以基础模式开头，或者正好等于基础模式
        if path == base_pattern or path.startswith(base_pattern + '/'):
            return True
        # 如果基础模式以/结尾，检查路径是否等于基础模式（去掉结尾/）
        if base_pattern.endswith('/') and path == base_pattern[:-1]:
            return True
        return False

    # 处理其他通配符模式
    regex_pattern = _pattern_to_regex(pattern)
    try:
        return bool(re.match(regex_pattern, path))
    except re.error:
        return False


def _pattern_to_regex(pattern: str) -> str:
    """
    将通配符模式转换为正则表达式
    """
    # 分割路径部分
    parts = pattern.split('/')
    regex_parts = []

    for i, part in enumerate(parts):
        if not part:
            if i == 0:  # 开头的空部分表示根路径
                regex_parts.append('')
            continue

        if part == '**':
            regex_parts.append('.*')
        elif '*' in part:
            # 将非通配符部分转义，通配符*替换为[^/]*
            escaped_part = re.escape(part).replace(r'\*', '[^/]*')
            regex_parts.append(escaped_part)
        else:
            regex_parts.append(re.escape(part))

    # 构建完整的正则表达式
    if regex_parts and regex_parts[0] == '':
        # 以根路径开头
        regex_pattern = '^/' + '/'.join(regex_parts[1:])
    else:
        regex_pattern = '^/' + '/'.join(regex_parts)

    # 处理结尾
    if pattern.endswith('/**'):
        regex_pattern += '(/?.*)?$'
    elif pattern.endswith('**'):
        regex_pattern += '(/?.*)?$'
    else:
        regex_pattern += '$'

    return regex_pattern


# 保留原有的复杂匹配方法作为备选
def _wildcard_match_encoded(path: str, pattern: str) -> bool:
    """
    使用URL编码的方法进行通配符匹配（备选方法）
    """
    try:
        # 对路径和模式进行URL编码
        encoded_path = quote(path, safe='')
        encoded_pattern = quote(pattern, safe='')

        # 将编码后的通配符(* -> %2A)替换为正则表达式
        regex_pattern = encoded_pattern.replace('%2A%2A', '.*')  # 处理 **
        regex_pattern = regex_pattern.replace('%2A', '[^/]*')  # 处理 *

        # 特殊处理以 /** 结尾的模式
        if pattern.endswith('/**'):
            if regex_pattern.endswith('/.*'):
                regex_pattern = regex_pattern[:-3] + '(/?.*)?'
            elif regex_pattern.endswith('.*'):
                regex_pattern = regex_pattern[:-2] + '(/?.*)?'

        # 添加正则表达式锚点
        regex_pattern = '^' + regex_pattern + '$'

        return bool(re.match(regex_pattern, encoded_path))
    except Exception:
        return _wildcard_match_simple(path, pattern)


@lru_cache(maxsize=128)
def _compile_pattern(pattern: str) -> re.Pattern:
    """
    编译通配符模式为正则表达式（带缓存）- 保留作为备选
    """
    regex_pattern = _pattern_to_regex(pattern)
    return re.compile(regex_pattern)


if __name__ == '__main__':
    test_cases = [
        # 基础测试
        ("/openapi/v1/users", ["/openapi/**"], True),
        ("/openapi/", ["/openapi/**"], True),
        ("/openapi", ["/openapi/**"], True),

        # 开头匹配测试
        ("/test/user/open123/test/abc/public.html",
         ["/test/user/open*/test/**/*.html"], True),
        ("/test/user/open123/test/abc/public.txt",
         ["/test/user/open*/test/**/*.html"], False),

        # 结尾匹配测试
        ("/test/user/123open/test/abc/public.html",
         ["/test/user/*open/test/**/*.html"], True),
        ("/test/user/open1/test/abc/public.html",
         ["/test/user/*open/test/**/*.html"], False),

        ("/test/user/somethingopen/test/abc/def/ghi.html",
         ["/test/user/*open/test/**/*.html"], True),
        ("/test/user/open/test/abc/def/ghi.text",
         ["/test/user/*open/test/**/*.html"], False),

        # 混合匹配测试
        ("/test/user/pre123mid456suf/test/abc/public.html",
         ["/test/user/pre*mid*suf/test/**/*.html"], True),

        # 不匹配的情况
        ("/test/user/123close/test/abc/public.html",
         ["/test/user/*open/test/**/*.html"], False),

        ("/test/user/open123/api/abc/public.html",
         ["/test/user/open*/test/**/*.html"], False),

        # 中间包含测试
        ("/test/user/abc123def/test/abc/public.html",
         ["/test/user/*123*/test/**/*.html"], True),

        ("/test/user/abc23def/test/abc/public.html",
         ["/test/user/*123*/test/**/*.html"], False),

        # 额外测试用例
        ("/api", ["/api/**"], True),
        ("/api/", ["/api/**"], True),
        ("/api/v1", ["/api/**"], True),
        ("/api/v1/users", ["/api/**"], True),
        ("/auth", ["/api/**"], False),

        # 更多边界测试
        ("/", ["/**"], True),
        ("/any/path", ["/**"], True),
        ("/test", ["/test**"], True),
        ("/testing", ["/test**"], True),
    ]

    print("测试结果:")
    print("=" * 50)

    all_passed = True
    for path, ignore_paths, expected in test_cases:
        result = is_path_ignored(path, ignore_paths)
        status = "✓" if result == expected else "✗"
        if status == "✗":
            all_passed = False
        print(f"{status} Path: {path}")
        print(f"  Pattern: {ignore_paths[0]}")
        print(f"  Result: {result}, Expected: {expected}")
        if status == "✗":
            print(f"  REGEX: {_pattern_to_regex(ignore_paths[0])}")
        print()

    print("=" * 50)
    if all_passed:
        print("🎉 所有测试用例通过！")
    else:
        print("❌ 有测试用例失败，请检查上述结果")