#!/usr/bin/env python3
"""
快速演示：使用 Cookie 登录 Instagram

用法：
    python demo_cookie_login.py

需要：
    在代码中替换 YOUR_COOKIE_STRING 为您从浏览器复制的实际 Cookie
"""

from instagrapi import Client


def demo_login_by_cookie():
    """演示使用 Cookie 登录"""

    # ============================================================
    # 步骤 1: 从浏览器复制 Cookie
    # ============================================================
    # 请将下面的字符串替换为您从浏览器开发者工具中复制的实际 Cookie
    # Chrome: F12 -> Application -> Cookies -> instagram.com
    # Firefox: F12 -> 存储 -> Cookies -> instagram.com

    cookie_string = """
    将这里替换为您的 Cookie 字符串
    例如：
    csrftoken=xxx;
    sessionid=123456%3Ayyy%3A27%3Azzz;
    mid=aaa;
    ds_user_id=123456
    """

    # 检查是否替换了默认 Cookie
    if "将这里替换" in cookie_string:
        print("❌ 错误：请先在代码中替换 cookie_string 为您的实际 Cookie")
        print()
        print("获取 Cookie 的步骤：")
        print("1. 在浏览器中打开 instagram.com 并登录")
        print("2. 按 F12 打开开发者工具")
        print("3. Chrome: Application -> Cookies -> instagram.com")
        print("   Firefox: 存储 -> Cookies -> instagram.com")
        print("4. 复制所有 Cookie 或只复制 sessionid")
        print("5. 粘贴到本脚本的 cookie_string 变量中")
        return

    # ============================================================
    # 步骤 2: 使用 Cookie 登录
    # ============================================================
    print("正在使用 Cookie 登录...")
    try:
        cl = Client()
        cl.login_by_cookie(cookie_string)
        print(f"✅ 登录成功！")
        print()
    except ValueError as e:
        print(f"❌ 登录失败：{e}")
        print()
        print("常见错误：")
        print("- Cookie 已过期：请重新从浏览器获取")
        print("- 缺少 sessionid：确保复制了完整的 Cookie")
        print("- 格式错误：检查 Cookie 字符串是否完整")
        return
    except Exception as e:
        print(f"❌ 未知错误：{e}")
        return

    # ============================================================
    # 步骤 3: 获取账户信息（只读操作，低风险）
    # ============================================================
    print("=" * 60)
    print("📊 账户信息")
    print("=" * 60)

    try:
        user = cl.account_info()
        print(f"用户名:    @{user.username}")
        print(f"全名:      {user.full_name}")
        print(f"用户 ID:   {user.pk}")
        print(f"粉丝数:    {user.follower_count:,}")
        print(f"关注数:    {user.following_count:,}")
        print(f"帖子数:    {user.media_count:,}")
        if user.biography:
            print(f"简介:      {user.biography[:100]}")
        print()
    except Exception as e:
        print(f"❌ 获取账户信息失败：{e}")
        return

    # ============================================================
    # 步骤 4: 获取最近帖子（只读操作）
    # ============================================================
    print("=" * 60)
    print("📸 最近 5 篇帖子")
    print("=" * 60)

    try:
        medias = cl.user_medias(user.pk, amount=5)
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

    # ============================================================
    # 步骤 5: 保存 Session（重要！）
    # ============================================================
    print("=" * 60)
    print("💾 保存 Session")
    print("=" * 60)

    session_file = "instagram_session.json"
    try:
        cl.dump_settings(session_file)
        print(f"✅ Session 已保存到: {session_file}")
        print()
        print("下次可以直接使用保存的 Session 登录，无需重新输入 Cookie：")
        print()
        print("    cl = Client()")
        print(f"    cl.load_settings('{session_file}')")
        print("    user = cl.account_info()  # 直接使用")
        print()
        print("注意：")
        print("- Instagram 会在后续请求中自动更新您的设备指纹")
        print("- 建议首次登录后只做只读操作，等待一段时间后再进行写操作")
        print("- 保存的 Session 可以重复使用，避免频繁重新登录")
    except Exception as e:
        print(f"❌ 保存 Session 失败：{e}")

    print("=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)


def demo_resume_from_session():
    """演示从保存的 Session 恢复登录"""

    session_file = "instagram_session.json"

    import os
    if not os.path.exists(session_file):
        print(f"❌ 未找到保存的 Session 文件: {session_file}")
        print("请先运行 demo_login_by_cookie() 创建 Session")
        return

    print(f"正在从 {session_file} 恢复登录...")

    try:
        cl = Client()
        cl.load_settings(session_file)

        # 验证 Session 是否有效
        user = cl.account_info()
        print(f"✅ 登录成功！欢迎回来，@{user.username}")
        print()
        print("现在您可以直接使用 Client 进行各种操作：")
        print(f"- 粉丝数: {user.follower_count:,}")
        print(f"- 关注数: {user.following_count:,}")
        print()
        print("💡 提示：使用保存的 Session 可以避免重复登录，降低风控风险")

    except Exception as e:
        print(f"❌ Session 已失效或损坏：{e}")
        print("请重新运行 demo_login_by_cookie() 获取新的 Cookie")


if __name__ == "__main__":
    import sys

    print()
    print("=" * 70)
    print("Instagram Cookie 登录演示")
    print("=" * 70)
    print()
    print("选项：")
    print("  1. 使用 Cookie 登录（首次使用）")
    print("  2. 从保存的 Session 恢复登录（后续使用）")
    print()

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("请选择 [1/2]: ").strip()

    print()

    if choice == "1":
        demo_login_by_cookie()
    elif choice == "2":
        demo_resume_from_session()
    else:
        print("❌ 无效的选择")
        print()
        print("直接运行默认演示...")
        print()
        demo_login_by_cookie()
