from instagrapi.cookie_parser import parse_cookies_file
from instagrapi import Client
import os

def test_login():
    # 解析文件中的第一个账户
    cookie_str = parse_cookies_file('fun-docs/10 COOKIES.txt', line_number=1)

    # 使用 cookie 登录
    cl = Client()
    cl.set_proxy("127.0.0.1:7890")
    session_file = "session.json"

    if not os.path.exists(session_file):
        # cl.login_by_cookie(cookie_str)
        cl.login(
            username="ross_kathleen.zsqtg"
            ,password="tPkmnsGZyUVP"
        )
        # print(f"登录成功: @{cl.username}")
    else:
        print(f"正在从 {session_file} 恢复登录...")
        cl.load_settings(session_file)
        # print(f"成功恢复: @{cl.username}")
    
    try:
        user = cl.account_info()
        print(f"{user}")
        # print(f"用户名:    @{user.username}")
        # print(f"全名:      {user.full_name}")
        # print(f"用户 ID:   {user.pk}")
        # print(f"粉丝数:    {user.follower_count:,}")
        # print(f"关注数:    {user.following_count:,}")
        # print(f"帖子数:    {user.media_count:,}")
        # if user.biography:
        #     print(f"简介:      {user.biography[:100]}")
        # print()
    except Exception as e:
        print(f"❌ 获取账户信息失败：{e}")
        return
    

    print("=" * 60)
    print("📸 最近 2 篇帖子")
    print("=" * 60)

    try:
        medias = cl.user_medias(user.pk, amount=2)
        for i, media in enumerate(medias, 1):
            print(f"\n{i}. 帖子 ID: {media.pk}")
            print(f"   类型: {['照片', '视频', '轮播'][media.media_type - 1]}")
            print(f"   点赞: {media.like_count:,}")
            print(f"   评论: {media.comment_count:,}")
            if media.caption_text:
                caption = media.caption_text.replace('\n', ' ')[:80]
                print(f"   文案: {caption}...")
        print()
    except Exception as e:
        print(f"❌ 获取帖子失败：{e}")

    # 保存会话供后续使用
    cl.dump_settings('session.json')

if __name__ == "__main__":
    test_login()