@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def overall_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id not in SUDOERS:
        return await CallbackQuery.answer(
            "Sadece Sudo Kullanıcılar için", show_alert=True
        )
    callback_data = CallbackQuery.data.strip()
    what = callback_data.split(None, 1)[1]
    if what != "s":
        upl = overallback_stats_markup(_)
    else:
        upl = back_stats_buttons(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    await CallbackQuery.edit_message_text("Bot istatistikleri yükleniyor...")
    sc = platform.system()
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
        else:
            cpu_freq = f"{round(cpu_freq, 2)}MHz"
    except:
        cpu_freq = "Alınamadı"
    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    total = str(total)
    used = hdd.used / (1024.0**3)
    used = str(used)
    free = hdd.free / (1024.0**3)
    free = str(free)
    mod = len(ALL_MODULES)
    db = pymongodb
    call = db.command("dbstats")
    datasize = call["dataSize"] / 1024
    datasize = str(datasize)
    storage = call["storageSize"] / 1024
    objects = call["objects"]
    collections = call["collections"]
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    total_queries = await get_queries()
    blocked = len(BANNED_USERS)
    sudoers = len(await get_sudoers())
    text = f"""**Bot İstatistikleri ve Bilgiler:**

**Yüklenen Modüller:** {mod}
**Platform:** {sc}
**RAM:** {ram}
**Fiziksel Çekirdekler:** {p_core}
**Toplam Çekirdekler:** {t_core}
**CPU Frekansı:** {cpu_freq}

**Python Sürümü:** {pyver.split()[0]}
**Pyrogram Sürümü:** {pyrover}
**Py-TgCalls Sürümü:** {pytgver}

**Depolama Toplam:** {total[:4]} GiB
**Depolama Kullanılan:** {used[:4]} GiB
**Depolama Boş:** {free[:4]} GiB

**Hizmet Verilen Sohbetler:** {served_chats} 
**Hizmet Verilen Kullanıcılar:** {served_users} 
**Engellenen Kullanıcılar:** {blocked} 
**Sudo Kullanıcılar:** {sudoers} 

**Toplam DB Boyutu:** {datasize[:6]} Mb
**Toplam DB Depolama:** {storage} Mb
**Toplam DB Koleksiyonları:** {collections}
**Toplam DB Anahtarları:** {objects}
**Toplam Bot Sorguları:** `{total_queries}` 
    """
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(
            media=med, reply_markup=upl
        )
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )


@app.on_callback_query(
    filters.regex(pattern=r"^(TOPMARKUPGET|GETSTATS|GlobalStats)$")
    & ~BANNED_USERS
)
@languageCB
async def back_buttons(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    command = CallbackQuery.matches[0].group(1)
    if command == "TOPMARKUPGET":
        upl = top_ten_stats_markup(_)
        med = InputMediaPhoto(
            media=config.GLOBAL_IMG_URL,
            caption="Top 10 istatistik listesi",  # Mesaj Türkçe
        )
        try:
            await CallbackQuery.edit_message_media(
                media=med, reply_markup=upl
            )
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.GLOBAL_IMG_URL,
                caption="Top 10 istatistik listesi",
                reply_markup=upl,
            )
    if command == "GlobalStats":
        upl = get_stats_markup(
            _,
            True if CallbackQuery.from_user.id in SUDOERS else False,
        )
        med = InputMediaPhoto(
            media=config.GLOBAL_IMG_URL,
            caption=f"{MUSIC_BOT_NAME} global istatistikleri",  # Mesaj Türkçe
        )
        try:
            await CallbackQuery.edit_message_media(
                media=med, reply_markup=upl
            )
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.GLOBAL_IMG_URL,
                caption=f"{MUSIC_BOT_NAME} global istatistikleri",
                reply_markup=upl,
            )
    if command == "GETSTATS":
        upl = stats_buttons(
            _,
            True if CallbackQuery.from_user.id in SUDOERS else False,
        )
        med = InputMediaPhoto(
            media=config.STATS_IMG_URL,
            caption=f"{MUSIC_BOT_NAME} bot istatistikleri",  # Mesaj Türkçe
        )
        try:
            await CallbackQuery.edit_message_media(
                media=med, reply_markup=upl
            )
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.STATS_IMG_URL,
                caption=f"{MUSIC_BOT_NAME} bot istatistikleri",
                reply_markup=upl,
            )
