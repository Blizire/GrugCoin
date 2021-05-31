# gbook_html.py
#
# Generates a html file of everyones gcoin wallet that exists in the database

import asyncio
from tinydb import TinyDB


class GBookHtml:
    def __init__(self, client, mining_length):
        self.client = client
        self.mining_length = mining_length


    async def get_gbook(self):
        db = TinyDB('db.json')
        msg = ""
        users = []
        for obj in db.all():
            userid = obj["userid"]
            wallet = obj["wallet"]
            user = await self.client.fetch_user(userid)
            users.append({"username":user, "wallet":wallet})

        # dictionary sort
        users = sorted(users, key= lambda k: k["wallet"], reverse=True)

        for user in users:
            msg += "<div class='gwallet'>\n<h2 class='username'>{user} :</h2>\n<h2 class='currency'>{wallet}gc</h2>\n</div>\n".format(user=user["username"], wallet=user["wallet"])

        return msg



    async def run(self):
        print("HTML report generator running...")
        while True:
            try:
                await asyncio.sleep(self.mining_length)
                gbook = await self.get_gbook()
                head = None
                tail = None
                with open("head.html", "r") as f:
                    head = f.readlines()
                with open("tail.html", "r") as f:
                    tail = f.readlines()
                with open("report.html", "w") as f:
                    f.writelines(head)
                with open("report.html", "a") as f:
                    f.write(gbook)
                    f.writelines(tail)
            except:
                pass