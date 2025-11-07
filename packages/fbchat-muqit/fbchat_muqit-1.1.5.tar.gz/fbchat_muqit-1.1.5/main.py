# testing file
import random

from fbchat_muqit.client import Client
from fbchat_muqit.events.dispatcher import EventType
from fbchat_muqit.facebook.client import Audience, FBReaction, Privacy
from fbchat_muqit.models import message
from fbchat_muqit.models.attachment import PostAttachment
from fbchat_muqit.models.message import Message
from fbchat_muqit.models.deltas.parser import MessageParser
from fbchat_muqit.models.thread import ThreadFolder, ThreadType

bot = Client("../c.json", log_level="DEBUG")
# one = True
#
# @bot.event(EventType.LISTENING)
# async def on_listen():
    # await bot.unsend("mid.$cAABtCv7ILEif2q1h3mZqWgWc9Dg_", "100012503553014")
    # meow = "Zhongli is the Geo Archon of Liyue, Rex Lapis, who now lives as a mortal consultant for the Wangsheng Funeral Parlor, known for his elegance, wealth of knowledge, and signature dark hair with amber tips and amber eyes with diamond-shaped pupils. He is a mysterious and cultured individual who enjoys history and the finer things in life, often to the dismay of his employer, Hu Tao, due to Zhongli's persistent lack of money."
    # await bot.typing("100012503553014", 1, 1)
    # await asyncio.sleep(0.5)
    # await bot.typing("100012503553014", 0, 1)
    # await bot.send_message(meow, "100012503553014")

new_thread = "817627187306472"
didonce = True
@bot.event(EventType.MESSAGE)
async def on_message(message_data: Message):
    thread_id = "7187797204617094"
    global new_thread
    thread_id2 = "4426180757442232"
    userId = "100026557698259"
    rudues = "100094571413433"
    mu = "100012503553014"
    print(f"message sent by {message_data.sender_id}: {message_data.text}")
    if message_data.attachments and isinstance(message_data.attachments[0], PostAttachment):
        f_id = message_data.attachments[0].post.feedback_id
        print('feedback_id is: ', f_id)
        await bot.react_to_post(f_id, reaction=FBReaction.LOVE)
        print("Done reactig")

    if message_data.sender_id == rudues:
        if "create group" in message_data.text:
            t_id = await bot.create_group_thread([mu, rudues])
            global new_thread
            new_thread = t_id
            print("recived tid: ", t_id)

        elif "update theme" in message_data.text:
            baka = await bot.fetch_thread_themes()
            theme = random.choice(baka)
            print(f"Updating theme to Id ({theme.id})")
            await bot.change_thread_theme(new_thread, int(theme.id))

        elif "confirm" in message_data.text:
            uid = message_data.text.split(" ")[-1].strip()
            await bot.send_friend_request([uid])



        elif "send post" in message_data.text:
            uid = " ".join(message_data.text.split(" ")[1:])
            except_users=["61574763012364","100090529639824","61579320458133","100068632251236"]
            h = ["/sdcard/bakaya.jpg", "/sdcard/horizon.jpg"]
            v = ["/sdcard/meows/meow.mp4"]

            some = await bot.publish_post("why would you even do such thing? because i like it.", video_paths=v, audience=Audience.FRIENDS)
            print("Some is :", some)
            # kk = await bot.upload_video(v[0])
            # print("Uploaded Video: ", kk)

        elif "delete" in message_data.text:
            uid = message_data.text.split(" ")[-1].strip()
            await bot.unfriend(uid)

        elif "change emoji" in message_data.text:
            await bot.change_thread_emoji(new_thread, "✨")

        elif "change name" in message_data.text:
            await bot.change_thread_name(new_thread, "Togashi Gang")

        elif "change approval mode" in message_data.text:
            await bot.change_thread_approval(new_thread, True)

        elif "add participant" in message_data.text:
            uid = int(message_data.text.split(" ")[-1].strip())
            if message_data.thread_participants and uid not in message_data.thread_participants:
                print(f"User not in grouo. Adding user...{uid} to {new_thread}")
                await bot.add_participants(new_thread, [uid])


        elif "remove participant" in message_data.text:
            uid = message_data.text.split(" ")[-1].strip()
            if message_data.thread_participants and uid in message_data.thread_participants:
                print(f"User not in grouo. Adding user...{uid} to {new_thread}")
                await bot.remove_participant(new_thread, uid)
        elif "add admin" in message_data.text:
            uid = message_data.text.split(" ")[-1].strip()
            await bot.set_thread_admin(new_thread, uid, True)
        elif "remove admin" in message_data.text:
            uid = message_data.text.split(" ")[-1].strip()
            await bot.set_thread_admin(new_thread, uid,  False)
        elif "read update" in message_data.text:
            await bot.change_read_receipts(new_thread, False)
        elif "message share" in message_data.text:
            await bot.change_thread_message_share(new_thread, False)
        elif "send from url" in message_data.text:
            await bot.send_files_from_url(new_thread, file_urls=["https://4kwallpapers.com/images/walls/thumbs_3t/24150.jpg", "https://4kwallpapers.com/images/walls/thumbs_3t/23761.jpg"])

        print("done printing")
bot.run()

# #
# # with open("./ThreadMessages.json", "rb") as f:
# #     da = msgspec.json.decode(f.read())
# # a = MessageParser()
# #
# # k = a.parse_thread_message(da)
# #
# # for i in k:
# #     print(i)
# #     print()
# #



