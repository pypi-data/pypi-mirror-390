



from fastmcp import FastMCP
from .tool import (
    _hello,
    _get_song_info,
    _get_song_id,
    _lyric,
    _search_artist,
    _login_anonymous,
    _login_refresh,
    _get_artist_info,
    _get_artist_hot_songs,
    _get_music_url,
    _get_song_comment,
    _get_playlist,
    _get_toplist,
    _get_similar_songs,
    _get_style_songs,
    _start_netease_music,
    _get_uid,
    _get_user_playlist,
    _return_stylelist,
    _return_toplist_name,
    global_cookie
)

mcp = FastMCP("MCPService")


@mcp.tool
def hello() -> dict:
    """测试使用,version=0.1.5"""
    return _hello()





@mcp.tool
def get_song_info(keywords: str) -> dict:
    """
    根据关键词搜索歌曲信息，歌曲id无需向用户透漏
    :param keywords: 歌曲关键词
    :return: 歌曲信息
    """
    return _get_song_info(keywords)

# @mcp.tool
# def get_song_id(keywords: str) -> dict:
#     """
#     根据关键词搜索歌曲，返回第一首歌的ID
#     :param keywords: 歌曲关键词
#     :return: 歌曲ID
#     """
#     return _get_song_id(keywords)

@mcp.tool
def lyric(keywords: str) -> dict:
    """
    根据歌名关键词搜索歌词
    :param keywords: 歌曲关键词
    :return: 歌词文本
    """
    return _lyric(keywords)

@mcp.tool
def get_music_url(keywords: str, level: str = "standard") -> dict:
    """
    根据关键词获取音乐在线试听url
    :param keywords: 歌曲关键词
    :param level: 音质等级
    :return: 音乐url json
    """
    return _get_music_url(keywords, level)

@mcp.tool
def get_song_comment(keywords: str) -> dict:
    """
    根据歌名关键词获取歌曲评论
    :param keywords: 歌曲关键词
    :return: 歌曲评论json
    """
    return _get_song_comment(keywords)

@mcp.tool
def get_similar_songs(keywords: str) -> dict:
    """
    根据关键词获取相似音乐（先查id再查/simi/song）
    :param keywords: 歌曲关键词
    :return: 相似音乐json
    """
    return _get_similar_songs(keywords)

@mcp.tool
def get_style_songs(style_name: str) -> dict:
    """
    根据曲风名返回歌曲列表。
    :param style_name: 曲风名
    :return: 歌曲列表json
    """
    return _get_style_songs(style_name)





@mcp.tool
def search_artist(keyword: str) -> dict:
    """
    根据关键词搜索歌手信息
    :param keyword: 歌手关键词
    :return: 歌手信息字符串
    """
    return _search_artist(keyword)

@mcp.tool
def get_artist_info(keyword: str) -> dict:
    """
    根据关键词获取歌手详细信息
    :param keyword: 歌手关键词
    :return: 歌手详细信息json
    """
    return _get_artist_info(keyword)

@mcp.tool
def get_artist_hot_songs(keyword: str) -> dict:
    """
    根据关键词获取歌手最火的50首歌曲
    :param keyword: 歌手关键词
    :return: 热门歌曲json
    """
    return _get_artist_hot_songs(keyword)





@mcp.tool
def get_playlist(id: int) -> dict:
    """
    根据歌单id获取歌单详情
    :param id: 歌单id
    :return: 歌单详情json
    """
    return _get_playlist(id)

@mcp.tool
def get_toplist(name: str) -> dict:
    """
    根据排行榜名字获取榜单详情（先查id再查_get_playlist）
    :param name: 榜单名称
    :return: 榜单详情json
    """
    return _get_toplist(name)





# @mcp.tool()
# def get_uid(nickname: str) -> dict:
#     """
#     根据用户昵称获取其uid
#     :param nickname: 用户昵称
#     :return: 用户uid json
#     """
#     return _get_uid(nickname)

@mcp.tool()
def get_user_playlist(nickname: str) -> dict:
    """
    输入用户昵称，获取用户歌单（含有歌单id）
    :param nickname: 用户昵称
    :return: 歌单列表json
    """
    return _get_user_playlist(nickname)





@mcp.tool
def return_stylelist() -> dict:
    """
    返回所有风格名称（不含id），从styleList.json读取。没有输入参数
    :return: {"code": 200, "msg": "success", "data": [风格名列表]}
    """
    return _return_stylelist()

@mcp.tool
def return_toplist_name() -> dict:
    """
    返回所有排行榜名称（不含id），从toplist.json读取。没有输入参数
    :return: {"code": 200, "msg": "success", "data": [榜单名列表]}
    """
    return _return_toplist_name()



# @mcp.tool
# def login_anonymous() -> dict:
#     """
#     游客登录，获取游客 cookie，并保存到全局变量
#     :return: 游客 cookie 字符串
#     """
#     return _login_anonymous()

# @mcp.tool
# def login_refresh() -> dict:
#     """
#     刷新登录状态，获取新的 cookie
#     :return: 新的 cookie 字符串
#     """
#     return _login_refresh()


@mcp.tool()
def start_netease_music(exe_path: str) -> dict:
    """
    启动本地网易云音乐客户端
    :param exe_path: 网易云音乐客户端的 exe 路径，默认 C:\\CloudMusic\\cloudmusic.exe
    :return: 启动结果 json
    """
    return _start_netease_music(exe_path)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    mcp.run(transport="stdio")