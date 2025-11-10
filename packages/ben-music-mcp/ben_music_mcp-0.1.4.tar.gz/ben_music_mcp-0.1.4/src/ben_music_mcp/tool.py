
import subprocess
import requests

# 全局变量保存 cookie
global_cookie = {}

import os
import json

def _save_cookie_to_file(cookie: dict, filename: str = "cookie.txt"):
    """将cookie保存到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(cookie, ensure_ascii=False))

def _load_cookie_from_file(filename: str = "cookie.txt") -> dict:
    """从文件读取cookie"""
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.loads(f.read())
    except Exception:
        return {}

def _get_cookie() -> dict:
    """获取当前cookie（优先文件）"""
    global global_cookie
    if global_cookie:
        return global_cookie
    cookie = _load_cookie_from_file()
    global_cookie = cookie
    return cookie

def _hello() -> dict:
    """方法注释"""
    return {"code": 200, "msg": "success", "data": "我是哈尔滨工业大学的学生，我叫张三，学号是123456。"}

def _get_song_info(keywords: str) -> dict:
    """
    搜索歌曲，返回json格式
    :param keywords: 歌曲关键词
    :return: 歌曲信息json
    """
    url = f"https://ncm.nekogan.com/search?keywords={keywords}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if "result" in data and "songs" in data["result"]:
            songs = data["result"]["songs"]
            if not songs:
                return {"code": 404, "msg": "未找到相关歌曲", "data": {}}
            song = songs[0]
            return {
                "code": 200,
                "msg": "success",
                "data": {
                    "id": song.get("id", "未知"),
                    "name": song.get("name", "未知"),
                    "artists": [a["name"] for a in song.get("artists", [])],
                    "album": song.get("album", {}).get("name", "未知"),
                    "alias": song.get("alias", []),
                    "transNames": song.get("transNames", []),
                    "duration": song.get("duration", 0),
                    "fee": song.get("fee", 0),
                    "mvid": song.get("mvid", 0)
                }
            }
        else:
            return {"code": 404, "msg": "未找到相关歌曲", "data": {}}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": {}}

def _get_song_id(keywords: str) -> dict:
    """
    搜索歌曲，返回第一个歌曲ID，json格式
    :param keywords: 歌曲关键词
    :return: 歌曲ID json
    """
    result = _get_song_info(keywords)
    if result.get("code") == 200 and "id" in result.get("data", {}):
        return {"code": 200, "msg": "success", "id": str(result["data"]["id"])}
    return {"code": 404, "msg": "未找到相关歌曲ID", "id": ""}

def _lyric(keywords: str) -> dict:
    """先获取歌曲id，再查歌词，返回json"""
    song_id_json = _get_song_id(keywords)
    song_id = song_id_json.get("id", "")
    if not song_id or not song_id.isdigit():
        return {"code": 404, "msg": f"未找到歌曲ID，原因：{song_id_json}", "data": ""}
    url = f"https://ncm.nekogan.com/lyric?id={song_id}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        lyric_text = data.get("lrc", {}).get("lyric", "")
        if lyric_text:
            return {"code": 200, "msg": "success", "data": lyric_text}
        else:
            return {"code": 404, "msg": "未找到歌词。", "data": ""}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败 {e}", "data": ""}


def _search_artist(keyword: str) -> dict:
    """
    搜索歌手，返回json格式
    :param keyword: 歌手关键词
    :return: 歌手信息json
    """
    url = f"https://ncm.nekogan.com/ugc/artist/search?keyword={keyword}"
    try:
        cookie = _get_cookie()
        resp = requests.get(url, timeout=5, cookies=cookie)
        resp.raise_for_status()
        data = resp.json()
        data_field = data.get("data")
        if not data_field or "list" not in data_field:
            return {"code": 404, "msg": "未找到相关歌手", "data": {}}
        artists = data_field.get("list", [])
        if not artists:
            return {"code": 404, "msg": "未找到相关歌手", "data": {}}
        artist = artists[0]
        return {
            "code": 200,
            "msg": "success",
            "data": {
                "artistName": artist.get("artistName", "未知"),
                "artistId": artist.get("artistId", "未知"),
                "avatar": artist.get("artistAvatarPicUrl", "")
            }
        }
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": {}}

def _get_artist_id(keyword: str) -> dict:
    """
    根据关键词搜索歌手，返回第一个歌手ID，json格式
    :param keyword: 歌手关键词
    :return: 歌手ID json
    """
    result = _search_artist(keyword)
    if result.get("code") == 200 and "artistId" in result.get("data", {}):
        return {"code": 200, "msg": "success", "id": str(result["data"]["artistId"])}
    return {"code": 404, "msg": "未找到相关歌手ID", "id": ""}


def _get_artist_info(keyword: str) -> dict:
    """
    根据关键词获取歌手详细信息，先查id再查详情，返回json
    :param keyword: 歌手关键词
    :return: 歌手详细信息json
    """
    id_json = _get_artist_id(keyword)
    artist_id = id_json.get("id", "")
    if not artist_id or not artist_id.isdigit():
        return {"code": 404, "msg": f"未找到歌手ID，原因：{id_json}", "data": {}}
    url = f"https://ncm.nekogan.com/ugc/artist/get?id={artist_id}"
    try:
        cookie = _get_cookie()
        resp = requests.get(url, timeout=5, cookies=cookie)
        resp.raise_for_status()
        data = resp.json()
        return {"code": 200, "msg": "success", "data": data}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": {}}

def _get_artist_hot_songs(keyword: str) -> dict:
    """
    根据关键词获取歌手最火的50首歌曲，先查id再查热门歌曲，返回json
    :param keyword: 歌手关键词
    :return: 热门歌曲json
    """
    id_json = _get_artist_id(keyword)
    artist_id = id_json.get("id", "")
    if not artist_id or not artist_id.isdigit():
        return {"code": 404, "msg": f"未找到歌手ID，原因：{id_json}", "data": []}
    url = f"https://ncm.nekogan.com/artist/top/song?id={artist_id}"
    try:
        cookie = _get_cookie()
        resp = requests.get(url, timeout=5, cookies=cookie)
        resp.raise_for_status()
        data = resp.json()
        return {"code": 200, "msg": "success", "data": data}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": []}


def _get_music_url(keywords: str, level: str = "standard") -> dict:
    """
    根据关键词获取音乐播放url，先查歌曲id再查url，返回json
    :param keywords: 歌曲关键词
    :param level: 音质等级
    :return: 音乐url json
    """
    id_json = _get_song_id(keywords)
    song_id = id_json.get("id", "")
    if not song_id or not song_id.isdigit():
        return {"code": 404, "msg": f"未找到歌曲ID，原因：{id_json}", "data": {}}
    url = f"https://ncm.nekogan.com/song/url/v1?id={song_id}&level={level}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {"code": 200, "msg": "success", "data": data}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": {}}


def _get_song_comment(keywords: str) -> dict:
    """
    根据关键词获取歌曲评论，只保留有用信息，返回json
    :param keywords: 歌曲关键词
    :return: 歌曲评论json
    """
    id_json = _get_song_id(keywords)
    song_id = id_json.get("id", "")
    if not song_id or not song_id.isdigit():
        return {"code": 404, "msg": f"未找到歌曲ID，原因：{id_json}", "data": []}
    url = f"https://ncm.nekogan.com/comment/music?id={song_id}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        hot_comments = data.get("hotComments", [])
        # 只保留有用字段
        result = []
        for c in hot_comments:
            user = c.get("user", {})
            result.append({
                "nickname": user.get("nickname", "未知"),
                "content": c.get("content", ""),
                "likedCount": c.get("likedCount", 0),
                "timeStr": c.get("timeStr", "")
            })
        return {"code": 200, "msg": "success", "data": result}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": []}


def _get_playlist(id):
    """
    获取歌单详情，只返回关键字段。
    参数: id (歌单id)
    返回: JSON
    """
    url = f"https://ncm.nekogan.com/playlist/detail?id={id}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("code") != 200 or "playlist" not in data:
            return {"code": 500, "msg": "请求失败"}
        pl = data["playlist"]
        result = {
            "id": pl.get("id"),
            "name": pl.get("name"),
            "coverImgUrl": pl.get("coverImgUrl"),
            "userId": pl.get("userId"),
            "createTime": pl.get("createTime"),
            "trackCount": pl.get("trackCount"),
            "playCount": pl.get("playCount"),
            "subscribedCount": pl.get("subscribedCount"),
            "description": pl.get("description"),
            "tags": pl.get("tags", []),
            "tracks": []
        }
        for t in pl.get("tracks", []):
            track = {
                "id": t.get("id"),
                "name": t.get("name"),
                "ar": [a.get("name") for a in t.get("ar", [])],
                "al": t.get("al", {}).get("name"),
                "alia": t.get("alia", [])
            }
            result["tracks"].append(track)
        return result
    except Exception as e:
        return {"code": 500, "msg": str(e)}


def _get_toplist(name: str) -> dict:
    """
    根据排行榜名获取榜单详情（先查id再查_get_playlist）
    :param name: 榜单名称
    :return: 榜单详情json
    """
    try:
        path = os.path.join(os.path.dirname(__file__), "toplist.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        toplists = data.get("toplists", [])
        match = next((item for item in toplists if item.get("name") == name), None)
        if not match:
            return {"code": 404, "msg": f"未找到榜单: {name}"}
        return _get_playlist(match["id"])
    except Exception as e:
        return {"code": 500, "msg": f"读取榜单失败: {e}"}


def _get_similar_songs(keywords: str) -> dict:
    """
    根据关键词获取相似音乐（先查id再查/simi/song）
    :param keywords: 歌曲关键词
    :return: 相似音乐json
    """
    id_json = _get_song_id(keywords)
    song_id = id_json.get("id", "")
    if not song_id or not song_id.isdigit():
        return {"code": 404, "msg": f"未找到歌曲ID，原因：{id_json}", "data": []}
    url = f"https://ncm.nekogan.com/simi/song?id={song_id}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        songs = data.get("songs", [])
        result = []
        for s in songs:
            result.append({
                "id": s.get("id"),
                "name": s.get("name"),
                "artists": [a.get("name") for a in s.get("artists", [])],
                "album": s.get("album", {}).get("name"),
                "duration": s.get("duration")
            })
        return {"code": 200, "msg": "success", "data": result}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": []}


def _get_style_songs(style_name: str) -> dict:
    """
    根据曲风名获取对应曲风id，再查 /style/song?tagId=xxx，返回歌曲列表。
    :param style_name: 曲风名
    :return: 歌曲列表json
    """

    # 读取 styleList.json
    try:
        path = os.path.join(os.path.dirname(__file__), "styleList.json")
        with open(path, "r", encoding="utf-8") as f:
            style_list = json.load(f)
    except Exception as e:
        return {"code": 500, "msg": f"读取曲风列表失败: {e}", "data": {}}

    tag_id = None
    for item in style_list:
        if item.get("tagName") == style_name:
            tag_id = item.get("tagId")
            print("tag_id: ",tag_id)
            break
    if not tag_id:
        return {"code": 404, "msg": f"未找到曲风: {style_name}", "data": {}}

    url = f"https://ncm.nekogan.com/style/song?tagId={tag_id}"
    try:
        cookie = _get_cookie()
        resp = requests.get(url, timeout=10, cookies=cookie)
        resp.raise_for_status()
        data = resp.json()
        print("完整响应:", data)
        page = data.get("page", {})
        songs = data.get("songs")
        # 自动适配嵌套结构
        if songs is None:
            for v in data.values():
                if isinstance(v, dict) and "songs" in v:
                    songs = v["songs"]
                    break
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict) and "songs" in item:
                            songs = item["songs"]
                            break
        if songs is None:
            songs = []
        # 只保留关键信息
        result = []
        for s in songs:
            if isinstance(s, dict):
                result.append({
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "artists": [a.get("name") for a in s.get("ar", [])],
                    "album": s.get("al", {}).get("name"),
                    "duration": s.get("dt")
                })
        print("最终精简songs:", result)
        return {"code": 200, "msg": "success", "data": result}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": {}}



def _get_uid(nickname: str) -> dict:
    """
    根据用户昵称获取其uid
    :param nickname: 用户昵称
    :return: 用户uid json
    """
    url = f"https://ncm.nekogan.com/get/userids?nicknames={nickname}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # 适配 nicknames 字段结构
        nick_dict = data.get("nicknames", {})
        if not nick_dict:
            return {"code": 404, "msg": "未找到用户", "data": {}}
        # 取第一个昵称和uid
        for n, uid in nick_dict.items():
            return {"code": 200, "msg": "success", "data": {"uid": uid, "nickname": n}}
        return {"code": 404, "msg": "未找到用户", "data": {}}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": {}}

def _get_user_playlist(nickname: str) -> dict:
    """
    输入用户昵称，获取用户歌单（只保留必要字段）
    :param nickname: 用户昵称
    :return: 歌单列表json
    """
    # 第一步：获取uid
    uid_result = _get_uid(nickname)
    if uid_result.get("code") != 200 or "uid" not in uid_result.get("data", {}):
        return {"code": 404, "msg": f"未找到用户: {nickname}", "data": []}
    uid = uid_result["data"]["uid"]
    # 第二步：获取歌单
    url = f"https://ncm.nekogan.com/user/playlist?uid={uid}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        playlists = data.get("playlist", [])
        result = []
        for pl in playlists:
            result.append({
                "id": pl.get("id"),
                "name": pl.get("name"),
                "coverImgUrl": pl.get("coverImgUrl"),
                "trackCount": pl.get("trackCount"),
                "playCount": pl.get("playCount"),
                "creator": {
                    "userId": pl.get("creator", {}).get("userId"),
                    "nickname": pl.get("creator", {}).get("nickname"),
                    "avatarUrl": pl.get("creator", {}).get("avatarUrl")
                }
            })
        return {"code": 200, "msg": "success", "data": result}
    except Exception as e:
        return {"code": 500, "msg": f"请求失败: {e}", "data": []}


def _return_stylelist() -> dict:
    """
    返回所有风格名称（不含id），从styleList.json读取。
    :return: {"code": 200, "msg": "success", "data": [风格名列表]}
    """
    try:
        path = os.path.join(os.path.dirname(__file__), "styleList.json")
        with open(path, "r", encoding="utf-8") as f:
            style_list = json.load(f)
        names = [item.get("tagName", "") for item in style_list if item.get("tagName")]
        return {"code": 200, "msg": "success", "data": names}
    except Exception as e:
        return {"code": 500, "msg": f"读取风格列表失败: {e}", "data": []}


def _return_toplist_name() -> dict:
    """
    返回所有排行榜名称（不含id），从toplist.json读取。
    :return: {"code": 200, "msg": "success", "data": [榜单名列表]}
    """
    try:
        path = os.path.join(os.path.dirname(__file__), "toplist.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        toplists = data.get("toplists", [])
        names = [item.get("name", "") for item in toplists if item.get("name")]
        return {"code": 200, "msg": "success", "data": names}
    except Exception as e:
        return {"code": 500, "msg": f"读取榜单列表失败: {e}", "data": []}



def _login_anonymous() -> dict:
    url = "https://ncm.nekogan.com/register/anonimous"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cookie = resp.cookies.get_dict()
        global global_cookie
        global_cookie = cookie
        _save_cookie_to_file(cookie)
        return {"code": 200, "msg": "游客登录成功", "cookie": cookie, "data": data}
    except Exception as e:
        return {"code": 500, "msg": f"游客登录失败: {e}", "cookie": {}, "data": {}}

def _login_refresh() -> dict:
    url = "https://ncm.nekogan.com/login/refresh"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cookie = resp.cookies.get_dict()
        return {"code": 200, "msg": "登录状态刷新成功", "cookie": cookie, "data": data}
    except Exception as e:
        return {"code": 500, "msg": f"刷新登录失败: {e}", "cookie": {}, "data": {}}


def _start_netease_music(exe_path: str) -> dict:
    """
    启动本地网易云音乐客户端
    :param exe_path: 网易云音乐客户端的 exe 路径
    :return: 启动结果 json
    """
    try:
        subprocess.Popen(exe_path)
        return {"code": 200, "msg": "网易云音乐已启动", "exe_path": exe_path}
    except Exception as e:
        return {"code": 500, "msg": f"启动失败: {e}", "exe_path": exe_path}
