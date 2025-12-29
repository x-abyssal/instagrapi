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
        cl.login_by_cookie(cookie_str)
    else:
        print(f"正在从 {session_file} 恢复登录...")
        cl.load_settings(session_file)
    
    try:
        user = cl.account_info()
        print(f"{user.model_dump()}")
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
        print(f"❌ 获取登录账户信息失败：{e}")
        return
    

    # try:
    #     user_info = cl.user_info_by_username("jjlin")
    #     print(f"{user_info.model_dump()}")
    #     user_medias = cl.user_medias(user_info.pk, amount=4)
    #     for i, media in enumerate(user_medias, 1):
    #         print(f"\n{i}. 帖子 ID: {media.pk}")
    #         print(f"   类型: {media.media_type}")
    #         print(f"   点赞: {media.like_count:,}")
    #         print(f"   评论: {media.comment_count:,}")
    #         if media.caption_text:
    #             caption = media.caption_text
    #             print(f"   文案: {caption}...")
    #     print()
    # except Exception as e:
    #     print(f"❌ 获取用户或用户帖子失败：{e}")
    

    print("=" * 60)
    print("📸 指定帖子")
    print("=" * 60)

    try:
        media = cl.media_info('https://www.instagram.com/reels/DM9RBWXziHe/')
        # media = cl.media_oembed('https://www.instagram.com/reels/DM9RBWXziHe/')
        print(f"帖子信息:{media.model_dump()}")
        print()
    except Exception as e:
        print(f"❌ 获取帖子失败：{e}")

    print("=" * 60)
    print("📸 指定帖子的评论")
    print("=" * 60)

    try:
        media_id = cl.media_id(cl.media_pk_from_url('https://www.instagram.com/reels/DM9RBWXziHe/'))
        comments = cl.media_comments(media_id,10)
        for i, comment in enumerate(comments, 1):
            print(f"{comment.text}")
            print(f"{comment.user.username}({comment.user.pk})")
            print()
            # print(f"comment: {comment.model_dump()}")
        print()
    except Exception as e:
        print(f"❌ 获取帖子评论失败：{e}")

    # 保存会话供后续使用
    cl.dump_settings('session.json')

if __name__ == "__main__":
    test_login()