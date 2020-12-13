# UserindoBot
# Copyright (C) 2020  UserindoBot Team, <https://github.com/MoveAngel/UserIndoBot.git>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Federation database."""

from ubotindo.modules.no_sql import get_collection


FEDS = get_collection("FEDERATION")
CHAT_FED = get_collection("CHAT_FEDS")
FED_BANS = get_collection("FED_BANS")
FED_SETTINGS = get_collection("FED_SETTINGS")
FED_SUBS = get_collection("FED_SUBS")

FEDERATION_BYNAME = {}
FEDERATION_BYOWNER = {}
FEDERATION_BYFEDID = {}

FEDERATION_CHATS = {}
FEDERATION_CHATS_BYID = {}

FEDERATION_BANNED_FULL = {}
FEDERATION_BANNED_USERID = {}

FEDERATION_NOTIFICATION = {}
FEDS_SUBSCRIBER = {}
MYFEDS_SUBSCRIBER = {}


def get_fen_info(fed_id) -> str:
    data = FEDERATION_BYFEDID.get(str(fed_id))
    if data is None:
        return False
    return data


def get_fed_id(chat_id) -> str:
    data = FEDERATION_CHATS.get(str(chat_id))
    if data is None:
        return False
    return data["fid"]


def get_fed_name(chat_id) -> str:
    data = FEDERATION_CHATS.get(str(chat_id))
    if data is None:
        return False
    return data["chat_name"]


def get_user_fban(fed_id, user_id) -> str:
    if not FEDERATION_BANNED_FULL.get(fed_id):
        return False, False, False
    user_info = FEDERATION_BANNED_FULL[fed_id].get(user_id)
    if not user_info:
        return None, None, None
    return user_info["first_name"], user_info["reason"], user_info["time"]


def get_user_admin_fed_name(user_id) -> list:
    user_feds = []
    for f in FEDERATION_BYFEDID:
        if int(user_id) in eval(
            eval(FEDERATION_BYFEDID[f]["fusers"])["members"]
        ):
            user_feds.append(FEDERATION_BYFEDID[f]["fname"])
    return user_feds


def get_user_owner_fed_name(user_id) -> list:
    user_feds = []
    for f in FEDERATION_BYFEDID:
        if int(user_id) == int(eval(FEDERATION_BYFEDID[f]["fusers"])["owner"]):
            user_feds.append(FEDERATION_BYFEDID[f]["fname"])
    return user_feds


def get_user_admin_fed_full(user_id) -> list:
    user_feds = []
    for f in FEDERATION_BYFEDID:
        if int(user_id) in eval(
            eval(FEDERATION_BYFEDID[f]["fusers"])["members"]
        ):
            user_feds.append({"fed_id": f, "fed": FEDERATION_BYFEDID[f]})
    return user_feds


def get_user_owner_fed_full(user_id) -> list:
    user_feds = []
    for f in FEDERATION_BYFEDID:
        if int(user_id) == int(eval(FEDERATION_BYFEDID[f]["fusers"])["owner"]):
            user_feds.append({"fed_id": f, "fed": FEDERATION_BYFEDID[f]})
    return user_feds


def get_user_fbanlist(user_id) -> [str, list]:
    banlist = FEDERATION_BANNED_FULL
    user_name = ""
    fedname = []
    for x in banlist:
        if banlist[x].get(user_id):
            if user_name == "":
                user_name = banlist[x][user_id].get("first_name")
            fedname.append([x, banlist[x][user_id].get("reason")])
    return user_name, fedname


def new_fed(owner_id, fed_name, fed_id):
    global FEDERATION_BYOWNER, FEDERATION_BYFEDID, FEDERATION_BYNAME
    create = FEDS.inser_one(
        {'owner_id': str(owner_id),
        'fed_name': fed_name,
        'fed_id': str(fed_id),
        'fed_rules': "Rules is not set in this federation.",
        'fed_log': None,
        'fed_users': {'owner': str(owner_id), 'members': []}}
    )
    FEDERATION_BYOWNER[str(owner_id)] = {
        "fid": str(fed_id),
        "fname": fed_name,
        "frules": "Rules is not set in this federation.",
        "flog": None,
        "fusers": str({"owner": str(owner_id), "members": "[]"}),
    }
    FEDERATION_BYFEDID[str(fed_id)] = {
        "owner": str(owner_id),
        "fname": fed_name,
        "frules": "Rules is not set in this federation.",
        "flog": None,
        "fusers": str({"owner": str(owner_id), "members": "[]"}),
    }
    FEDERATION_BYNAME[fed_name] = {
        "fid": str(fed_id),
        "owner": str(owner_id),
        "frules": "Rules is not set in this federation.",
        "flog": None,
        "fusers": str({"owner": str(owner_id), "members": "[]"}),
    }
    return create


def del_fed(fed_id):
    global FEDERATION_BYOWNER, FEDERATION_BYFEDID, FEDERATION_BYNAME, FEDERATION_CHATS, FEDERATION_CHATS_BYID, FEDERATION_BANNED_USERID, FEDERATION_BANNED_FULL
    getcache = FEDERATION_BYFEDID.get(fed_id)
    if getcache is None:
        return False
    # Variables
    getfed = FEDERATION_BYFEDID.get(fed_id)
    owner_id = getfed["owner"]
    fed_name = getfed["fname"]
    # Delete from cache
    FEDERATION_BYOWNER.pop(owner_id)
    FEDERATION_BYFEDID.pop(fed_id)
    FEDERATION_BYNAME.pop(fed_name)
    if FEDERATION_CHATS_BYID.get(fed_id):
        for x in FEDERATION_BYFEDID[fed_id]:
            CHAT_FED.delete_one({'chat_id': str(x)})
            FEDERATION_CHATS.pop(x)
        FEDERATION_CHATS_BYID.pop(x)
    # Delete fedban users
    getall = FEDERATION_BANNED_USERID.get(fed_id)
    if getall:
        FED_BANS.delete_many({'fed_id': fed_id})
    if FEDERATION_BANNED_USERID.get(fed_id):
        FEDERATION_BANNED_USERID.pop(fed_id)
    if FEDERATION_BANNED_FULL.get(fed_id):
        FEDERATION_BANNED_FULL.pop(fed_id)
    # Delete FedSubs
    getall = MYFEDS_SUBSCRIBER.get(fed_id)
    if getall:
        for x in getall:
            FED_SUBS.delete_one({'fed_id': fed_id, 'fed_subs': str(x)})
    if FEDS_SUBSCRIBER.get(fed_id):
        FEDS_SUBSCRIBER.pop(fed_id)
    if MYFEDS_SUBSCRIBER.get(fed_id):
        MYFEDS_SUBSCRIBER.pop(fed_id)
    FEDS.delete_one({'fed_id': fed_id})
    return True


def chat_join_fed(fed_id, chat_name, chat_id):
    global FEDERATION_CHATS, FEDERATION_CHATS_BYID
    CHAT_FED.insert_one(
        {'chat_id': chat_id, 'chat_name': chat_name, 'fed_id': fed_id})
    FEDERATION_CHATS[str(chat_id)] = {
        "chat_name": chat_name,
        "fid": fed_id,
    }
    checkid = FEDERATION_CHATS_BYID.get(fed_id)
    if checkid is None:
        FEDERATION_CHATS_BYID[fed_id] = []
    FEDERATION_CHATS_BYID[fed_id].append(str(chat_id))
    return True


def search_fed_by_name(fed_name):
    allfed = FEDERATION_BYNAME.get(fed_name)
    if allfed is None:
        return False
    return allfed


def search_user_in_fed(fed_id, user_id):
    getfed = FEDERATION_BYFEDID.get(fed_id)
    if getfed is None:
        return False
    getfed = eval(getfed["fusers"])["members"]
    if user_id in eval(getfed):
        return True
    else:
        return False


def user_demote_fed(fed_id, user_id):
    global FEDERATION_BYOWNER, FEDERATION_BYFEDID, FEDERATION_BYNAME
    # Variables
    getfed = FEDERATION_BYFEDID.get(str(fed_id))
    owner_id = getfed["owner"]
    fed_name = getfed["fname"]
    try:
        members = eval(eval(getfed["fusers"])["members"])
    except ValueError:
        return False
    members.remove(user_id)
    # Set user
    FEDERATION_BYOWNER[str(owner_id)]["fusers"] = str(
        {"owner": str(owner_id), "members": str(members)}
    )
    FEDERATION_BYFEDID[str(fed_id)]["fusers"] = str(
        {"owner": str(owner_id), "members": str(members)}
    )
    FEDERATION_BYNAME[fed_name]["fusers"] = str(
        {"owner": str(owner_id), "members": str(members)}
    )
    # Set on database
    FEDS.update_one(
        {'owner_id': str(owner_id), 'fed_name': fed_name, 'fed_id': str(fed_id)},
        {"$pull": {
            'fusers.members': str(members)
        }}
    )

    CHAT_FED.delete_many({'chat_id': user_id, 'fed_id': fed_id})
    return True


def user_join_fed(fed_id, user_id):
    global FEDERATION_BYOWNER, FEDERATION_BYFEDID, FEDERATION_BYNAME
    # Variables
    getfed = FEDERATION_BYFEDID.get(str(fed_id))
    owner_id = getfed["owner"]
    fed_name = getfed["fname"]
    # Temp set
    members = eval(eval(getfed["fusers"])["members"])
    members.append(user_id)
    # Set user
    FEDERATION_BYOWNER[str(owner_id)]["fusers"] = str(
        {"owner": str(owner_id), "members": str(members)}
    )
    FEDERATION_BYFEDID[str(fed_id)]["fusers"] = str(
        {"owner": str(owner_id), "members": str(members)}
    )
    FEDERATION_BYNAME[fed_name]["fusers"] = str(
        {"owner": str(owner_id), "members": str(members)}
    )
    # Set on database
    FEDS.update_one(
        {'owner_id': str(owner_id), 'fed_name': fed_name, 'fed_id': str(fed_id)},
        {"$push": {
            'fusers.members': str(members)
        }}
    )
    return True


def chat_leave_fed(chat_id):
    global FEDERATION_CHATS, FEDERATION_CHATS_BYID
    # Set variables
    fed_info = FEDERATION_CHATS.get(str(chat_id))
    if fed_info is None:
        return False
    fed_id = fed_info["fid"]
    # Delete from cache
    FEDERATION_CHATS.pop(str(chat_id))
    FEDERATION_CHATS_BYID[str(fed_id)].remove(str(chat_id))
    # Delete from db
    CHAT_FED.delete_one({'chat_id': chat_id})
    return True


def all_fed_chats(fed_id):
    getfed = FEDERATION_CHATS_BYID.get(fed_id)
    if getfed is None:
        return []
    else:
        return getfed


def all_fed_users(fed_id):
    getfed = FEDERATION_BYFEDID.get(str(fed_id))
    if getfed is None:
        return False
    fed_owner = eval(eval(getfed["fusers"])["owner"])
    fed_admins = eval(eval(getfed["fusers"])["members"])
    fed_admins.append(fed_owner)
    return fed_admins

def set_frules(fed_id, rules):
    global FEDERATION_BYOWNER, FEDERATION_BYFEDID, FEDERATION_BYNAME
    # Variables
    getfed = FEDERATION_BYFEDID.get(str(fed_id))
    owner_id = getfed["owner"]
    fed_name = getfed["fname"]
    fed_rules = str(rules)
    # Set user
    FEDERATION_BYOWNER[str(owner_id)]["frules"] = fed_rules
    FEDERATION_BYFEDID[str(fed_id)]["frules"] = fed_rules
    FEDERATION_BYNAME[fed_name]["frules"] = fed_rules

    FEDS.update_one(
        {'owner_id': str(owner_id), 'fed_name': fed_name, 'fed_id': str(fed_id)},
        {"$set": {'fed_rules': fed_rules}}
    )
    return True


def get_frules(fed_id):
    rules = FEDERATION_BYFEDID[str(fed_id)]["frules"]
    return rules


def fban_user(fed_id, user_id, first_name, last_name, user_name, reason, time):
    FED_BANS.update_one(
        {'fed_id': str(fed_id), 'user_id': str(user_id),
        'first_name': first_name, 'last_name': last_name,
        'username': user_name},
        {"$set": {'reason': reason, 'time': time}},
        upsert=True
    )
    __load_all_feds_banned()
    return True


def multi_fban_user(
    multi_fed_id,
    multi_user_id,
    multi_first_name,
    multi_last_name,
    multi_user_name,
    multi_reason,
):
    if True:  # with FEDS_LOCK:
        counter = 0
        time = 0
        for x in range(len(multi_fed_id)):
            fed_id = multi_fed_id[x]
            user_id = multi_user_id[x]
            first_name = multi_first_name[x]
            last_name = multi_last_name[x]
            user_name = multi_user_name[x]
            reason = multi_reason[x]

            FED_BANS.update_one(
                {'fed_id': str(fed_id), 'user_id': str(user_id),
                'first_name': first_name, 'last_name': last_name,
                'username': user_name},
                {"$set": {'reason': reason, 'time': time}},
                upsert=True
            )
            counter += 1
    __load_all_feds_banned()
    return counter


def un_fban_user(fed_id, user_id):
    FED_BANS.delete_one(
        {'fed_id': fed_id, 'user_id': user_id}
    )
    __load_all_feds_banned()
    return True


def get_fban_user(fed_id, user_id):
    list_fbanned = FEDERATION_BANNED_USERID.get(fed_id)
    if list_fbanned is None:
        FEDERATION_BANNED_USERID[fed_id] = []
    if user_id in FEDERATION_BANNED_USERID[fed_id]:
        data = FED_BANS.find_one(
            {'fed_id': fed_id, 'user_id': int(user_id)}
        )
        reason = None
        if data:
            reason = data["reason"]
            time = data["time"]
        return True, reason, time
    return False, None, None


def get_all_fban_users(fed_id):
    list_fbanned = FEDERATION_BANNED_USERID.get(fed_id)
    if list_fbanned is None:
        FEDERATION_BANNED_USERID[fed_id] = []
    return FEDERATION_BANNED_USERID[fed_id]


def get_all_fban_users_target(fed_id, user_id):
    list_fbanned = FEDERATION_BANNED_FULL.get(fed_id)
    if list_fbanned is None:
        FEDERATION_BANNED_FULL[fed_id] = []
        return False
    getuser = list_fbanned[str(user_id)]
    return getuser


def get_all_fban_users_global():
    total = []
    for x in list(FEDERATION_BANNED_USERID):
        for y in FEDERATION_BANNED_USERID[x]:
            total.append(y)
    return total


def get_all_feds_users_global():
    total = []
    for x in list(FEDERATION_BYFEDID):
        total.append(FEDERATION_BYFEDID[x])
    return total


def search_fed_by_id(fed_id) -> False:
    # Broken source
    return False


def user_feds_report(user_id: int) -> bool:
    user_setting = FEDERATION_NOTIFICATION.get(str(user_id))
    if user_setting is None:
        user_setting = True
    return user_setting
