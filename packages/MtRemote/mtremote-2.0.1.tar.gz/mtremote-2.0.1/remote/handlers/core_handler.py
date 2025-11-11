from pyrogram import filters , errors
from pyrogram.types import Message 
from ..moudels.admin.admin_manager import (admin_filter , owner_filter)
from ..moudels.account import (account_manager,account_viewer,cleaner) 
from ..moudels.account.client import (client_manager)
from ..moudels.account.profile import (profile_info,profile_media,profile_privacy,username_manager)
from ..moudels.admin import (admin_manager)
from ..moudels.analytics import (analytics_manager)
from ..moudels.batch import (batch_manager)
from ..moudels.core import (config,restart_module,getcode_controller,help_menu)
from ..moudels.db import (db_monitor,sqlite_utils)
from ..moudels.group import (join_controller,leave_controller)
from ..moudels.spammer import (spammer,speed_manager,stop_manager)
from ..moudels.text import (caption_manager,mention_manager,text_manager)
from ..moudels.utils import (block_manager,file_sender)
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
runner = 0

def register_commands(app): 

    # -------------------- Commands --------------------
    
    #ACCOUNT
    @app.on_message(filters.command("add", prefixes=["/", ""]) & admin_filter)
    async def add_account(client, message):
        await account_manager.add_account_cmd(message, account_manager.get_app_info)

    @app.on_message(filters.command("code", prefixes=["/", ""]) & admin_filter)
    async def set_code(client, message):
        await account_manager.set_code_cmd(message)

    @app.on_message(filters.command("pass", prefixes=["/", ""]) & admin_filter)
    async def set_2fa(client, message):
        await account_manager.set_2fa_cmd(message)

    @app.on_message(filters.command("del", prefixes=["/", ""]) & admin_filter)
    async def delete_account(client, message):
        await account_manager.delete_account_cmd(message)

    @app.on_message(filters.command("delall", prefixes=["/", ""]) & admin_filter)
    async def delete_all_accounts(client, message):
        await account_manager.delete_all_accounts_cmd(message)
        
    @app.on_message(filters.command("listacc", prefixes=["/", ""]) & admin_filter)
    async def list_accounts(client, message):
        await account_viewer.list_accounts_cmd(message)

    @app.on_message(filters.command("givedatasessions", prefixes=["/", ""]) & owner_filter)
    async def give_data_sessions_handler(client, message):
        await file_sender.give_data_sessions_cmd(app, message)
        
    @app.on_message(filters.command("delallpvgpchenl", "") & owner_filter)
    async def del_all_pv_gp_ch_en(client, message):
        await cleaner.del_all_pv_gp_ch_en_cmd(message)

    @app.on_message(filters.command("givesessions", "") & owner_filter)
    async def give_sessions_handler(client, message):
        await file_sender.give_sessions_cmd(app, message)



    #TEXT
    @app.on_message(filters.command('text', prefixes=["/", ""]) & admin_filter) 
    async def save_text(client, message): 
        await text_manager.save_text_cmd(message) 
        
    @app.on_message(filters.command('ctext', prefixes=["/", ""]) & admin_filter) 
    async def clear_texts(client, message): 
        await text_manager.clear_texts_cmd(message) 
        
    @app.on_message(filters.command('shtext', prefixes=["/", ""]) & admin_filter) 
    async def show_text(client, message): 
        await text_manager.show_texts_cmd(message) 

    @app.on_message(filters.command('shcap', prefixes=["/", ""]) & admin_filter) 
    async def show_caption(client, message): 
        await caption_manager.show_caption_cmd(message, config.spam_config) 
        
    @app.on_message(filters.command('cap', prefixes=["/", ""]) & admin_filter) 
    async def add_caption(client, message): 
        await caption_manager.add_caption_cmd(message, config.spam_config) 
        
    @app.on_message(filters.command('ccap', prefixes=["/", ""]) & admin_filter) 
    async def clear_caption(client, message): 
        await caption_manager.clear_caption_cmd(message, config.spam_config)

    @app.on_message(admin_filter & filters.command("textmention", prefixes=["/", ""]))
    async def _setmention(client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await mention_manager.set_mention_text(txt))

    @app.on_message(admin_filter & filters.command("mention_user", prefixes=["/", ""]))
    async def _mention_user(client, m: Message):
        user = m.command[1]
        await m.reply(await mention_manager.set_mention_user(user))

    @app.on_message(admin_filter & filters.command("mention_toggle", prefixes=["/", ""]))
    async def _mention_toggle(client, m: Message):
        if len(m.command) < 2:
            return await m.reply("Usage: /mention_toggle <on|off>")
        enable = (m.command[1].lower() == "on")
        await m.reply(await mention_manager.toggle_mention(enable))

    @app.on_message(admin_filter & filters.command("mention_group_toggle", prefixes=["/", ""]))
    async def _mention_group_toggle(client, m: Message):
        if len(m.command) < 2:
            return await m.reply("Usage: /mention_group_toggle <on|off>")
        enable = (m.command[1].lower() == "on")
        await m.reply(await mention_manager.toggle_group_mention(enable))

    @app.on_message(admin_filter & filters.command("mention_gps", prefixes=["/", ""]))
    async def _mention_gps(client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /mention_gps <id1> <id2> ...")
        tokens = m.command[1:]
        ids = await mention_manager._resolve_many_tokens_to_ids(client, tokens)
        if not ids:
            return await m.reply("❌ هیچ شناسهٔ معتبری تشخیص داده نشد.")
        msg = await mention_manager.add_groups_by_ids(*ids)
        await m.reply(msg)

        await m.reply(msg)

    @app.on_message(admin_filter & filters.command("mention_del", prefixes=["/", ""]))
    async def _mention_del(client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /mention_del <id1> <id2> ...")
        tokens = m.command[1:]
        ids = await mention_manager._resolve_many_tokens_to_ids(client, tokens)
        if not ids:
            return await m.reply("❌ هیچ شناسهٔ معتبری برای حذف تشخیص داده نشد.")
        msg = await mention_manager.remove_groups_by_ids(*ids)
        await m.reply(msg)

    @app.on_message(admin_filter & filters.command("mention_clear", prefixes=["/", ""]))
    async def _mention_clear(client, m: Message):
        await m.reply(await mention_manager.clear_groups())

    @app.on_message(admin_filter & filters.command("mention_status", prefixes=["/", ""]))
    async def _mention_status(client, m: Message):
        await m.reply(await mention_manager.mention_status())

        
    #MORE
    @app.on_message(filters.command('gcode', '') & admin_filter) 
    async def get_code_command(client, message): 
        await getcode_controller.handle_getcode_cmd(message)

    @app.on_message(filters.command("restart", prefixes=["/", ""]) & admin_filter)
    async def restart_cmd(client, message): 
        restart_module.clear_logs()
        await message.reply("🔄 عملیات ریست کامل شد!")

    #JOIN & LEFT
    @app.on_message(filters.command("join", "") & admin_filter)
    async def join_command(client, message):
        await join_controller.handle_join_cmd(message)

    @app.on_message(filters.command("leave", "") & admin_filter)
    async def leave_command(client, message):
        await leave_controller.handle_leave_cmd(message)
        
    #ADMIN
    @app.on_message(filters.command("addadmin", "") & owner_filter)
    async def add_admin(client, message):
        await admin_manager.add_admin_cmd(message)

    @app.on_message(filters.command("deladmin", "") & owner_filter)
    async def del_admin(client, message):
        await admin_manager.del_admin_cmd(message)

    @app.on_message(filters.command("admins", "") & owner_filter)
    async def list_admins(client, message):
        await admin_manager.list_admins_cmd(message)


    #PROFILE
    @app.on_message(filters.command("profilesettings", "") & admin_filter)
    async def profilesettings_cmd(client, message):
        await profile_privacy.profile_settings_cmd(message)

    @app.on_message(filters.command("setPic", "") & admin_filter)
    async def set_profile_photo_cmd(client, message):
        await profile_media.change_profile_photo(app, message)

    @app.on_message(filters.command("delallprofile", "") & admin_filter)
    async def delete_all_photos_cmd(client, message):
        await profile_media.delete_all_profile_photos(message)

    @app.on_message(filters.command("name", "") & admin_filter)
    async def change_name_cmd(client, message):
        await profile_info.change_name_cmd(message)

    @app.on_message(filters.command("bio", "") & admin_filter)
    async def change_bio_cmd(client, message):
        await profile_info.change_bio_cmd(message)

    @app.on_message(filters.command("username", "") & admin_filter)
    async def set_username_cmd(client, message):
        await username_manager.set_usernames_for_all(message)

    @app.on_message(filters.command("remusername", "") & admin_filter)
    async def rem_username_cmd(client, message):
        await username_manager.remove_usernames_for_all(message)
        
    @app.on_message(filters.command("block", "") & admin_filter)
    async def block_user_all_accounts(client, message):
        await block_manager.block_user_all_cmd(message)

    @app.on_message(filters.command("unblock", "") & admin_filter)
    async def unblock_user_all_accounts(client, message):
        await block_manager.unblock_user_all_cmd(message)

    #DATABASE
    @app.on_message(filters.command("dbstatus", "") & owner_filter)
    async def cmd_db_status(client, message):
        await db_monitor.db_status_cmd(message)

    @app.on_message(filters.command("dbrepair", "") & owner_filter)
    async def cmd_db_repair(client, message):
        await db_monitor.db_repair_cmd(message)

    #SPAMMER
    @app.on_message(filters.command("spam", "") & admin_filter)
    async def start_spam(client, message):
        if len(message.command) < 2:
            await message.reply("❌ لطفاً لینک یا آیدی هدف را وارد کنید.")
            return

        raw_target = message.command[1].strip()
        config.spam_config["run"] = False
        target_chat_id = None

        ttype, tval, aux = spammer._normalize_target_for_spam(raw_target)
        try:
            if ttype == "chat_id":
                target_chat_id = int(tval)
                await message.reply(f"🧩 آیدی عددی شناسایی شد: `{target_chat_id}`")

            elif ttype == "invite":
                invite_hash = str(tval).lstrip("+").strip()
                invite_link = (
                    f"https://t.me/joinchat/{invite_hash}" if aux is True else f"https://t.me/+{invite_hash}"
                )

                cli = await client_manager.get_any_client(message)
                if not cli:
                    return

                try:
                    chat = await cli.join_chat(invite_link)
                    target_chat_id = chat.id
                    await message.reply(f"🔗 لینک خصوصی شناسایی شد. آیدی: `{target_chat_id}`")
                except errors.UserAlreadyParticipant:
                    chat = await cli.get_chat(invite_link)
                    target_chat_id = chat.id
                    await message.reply(f"🔗 عضو بودی؛ آیدی استخراج شد: `{target_chat_id}`")
                except errors.FloodWait as e:
                    await message.reply(f"⏰ FloodWait {e.value}s؛ بعداً تلاش کنید.")
                    return
                except Exception as e:
                    await message.reply(f"❌ خطا در join: `{type(e).__name__}` - {e}")
                    return

            elif ttype == "username":
                username = str(tval).lstrip("@").strip()
                cli = await client_manager.get_any_client(message)
                if not cli:
                    return
                chat = await cli.get_chat(username)
                target_chat_id = chat.id
                await message.reply(f"👤 یوزرنیم شناسایی شد. آیدی: `{target_chat_id}`")

            else:
                await message.reply("❌ ورودی نامعتبر است.")
                return

            config.spam_config["spamTarget"] = target_chat_id
            config.spam_config["run"] = True
            global runner
            await message.reply(f"🚀 اسپمر شروع شد!\n🎯 هدف: `{target_chat_id}`")

            runner = spammer.SpammerThreadingRunner(
                config.spam_config, 
                client_manager.remove_client_from_pool,
            )

            runner.start()

        except Exception as e:
            logger.exception(f"Error in /spam: {e}")
            await message.reply(f"💥 خطا در پردازش دستور spam: `{type(e).__name__}` - {e}")

    @app.on_message(filters.command("stop", "") & admin_filter)
    async def stop_spam(client, message):
        global runner
        runner.stop()
        await stop_manager.stop_spammer_cmd(message)
        


    @app.on_message(filters.command("speed", "") & admin_filter)
    async def set_speed(client, message):
        await speed_manager.set_speed_cmd(message)

    @app.on_message(filters.command("set", "") & admin_filter)
    async def _set_handler(client, message):
        await batch_manager._set_batch_size_cmd(client, message)

    @app.on_message(filters.command("stats", "") & admin_filter)
    async def show_stats(client, message):
        await analytics_manager.analytics.show_stats_cmd(message)

