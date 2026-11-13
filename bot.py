import logging, sqlite3, random, asyncio, os, threading
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 👇👇👇 توکن ربات جدیدت (Anime God) رو اینجا بذار 👇👇👇
TOKEN = "9198924784:AAE56J4uhv53PcEIjYMTjLwD__RdpWOjgxs"
ADMIN = 6267038708
LIMIT = 50
REW = {"Common": 50, "Rare": 150, "Epic": 400, "Legendary": 1000, "Mythic": 2500}
EMO = {"Common": "⚪", "Rare": "🔵", "Epic": "🟣", "Legendary": "🟡", "Mythic": "🔴"}
W = {"Common": 50, "Rare": 30, "Epic": 15, "Legendary": 4, "Mythic": 1}
CM = ["⚡ 𝐋𝐈𝐆𝐇𝐓𝐍𝐈𝐍𝐆 𝐅𝐀𝐒𝐓!", "🔥 𝐁𝐋𝐀𝐙𝐈𝐍𝐆 𝐂𝐀𝐓𝐂𝐇!", "💫 𝐒𝐔𝐏𝐄𝐑𝐁 𝐒𝐊𝐈𝐋𝐋!", "⚔️ 𝐋𝐄𝐆𝐄𝐍𝐃𝐀𝐑𝐘 𝐌𝐎𝐕𝐄!", "🎯 𝐏𝐄𝐑𝐅𝐄𝐂𝐓 𝐇𝐈𝐓!"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running 24/7!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def db():
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS u (id INTEGER PRIMARY KEY, coins INT DEFAULT 100, xp INT DEFAULT 0, lvl INT DEFAULT 1, strk INT DEFAULT 0, daily TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS c (code INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, anime TEXT, rar TEXT, vid TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS h (uid INT, code INT, UNIQUE(uid, code))')
    c.execute('CREATE TABLE IF NOT EXISTS act (chat INT PRIMARY KEY, code INT)')
    c.execute('CREATE TABLE IF NOT EXISTS s (chat INT PRIMARY KEY, cnt INT DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS hist (chat INT, code INT, UNIQUE(chat, code))')
    conn.commit()
    return conn

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db()
    conn.execute("INSERT OR IGNORE INTO u (id) VALUES (?)", (update.effective_user.id,))
    conn.commit(); conn.close()
    await update.message.reply_text("🎮 **ANIME GOD** 🎮\n\n/profile 👤 پروفایل\n/harem 📚 کلکسیون\n/daily 💰 جایزه روزانه\n/top 🏆 تاپ ۱۰ گروه\n/gtop 🌍 تاپ ۱۰ جهانی\n/lb 🎁 لوت‌باکس\n/s <کد> 🔍 اطلاعات کاراکتر\n/sell <کد> 💸 فروش\n/fav <کد> ⭐ علاقه‌مندی\n\n📤 ادمین:\n/upload 📤 آپلود کلیپ\n/spawn 🎬 اسپاون دستی\n/listchars 📋 لیست کاراکترها\n\n💡 هر ۵۰ پیام یک کاراکتر!")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db(); uid = update.effective_user.id
    conn.execute("INSERT OR IGNORE INTO u (id) VALUES (?)", (uid,))
    r = conn.execute("SELECT coins, xp, lvl, strk FROM u WHERE id=?", (uid,)).fetchone()
    h = conn.execute("SELECT COUNT(*) FROM h WHERE uid=?", (uid,)).fetchone()[0]
    conn.commit(); conn.close()
    await update.message.reply_text(f"👤 {update.effective_user.first_name}\n━━━━━━━━━━━\n💰 سکه: {r[0]}\n🎯 شکار: {h}\n🔥 استریک: {r[3]}\n🎖 لول: {r[2]} ({100-(r[1]%100)} XP)")

async def harem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db()
    rows = conn.execute("SELECT c.code, c.name, c.rar FROM h JOIN c ON h.code=c.code WHERE h.uid=?", (update.effective_user.id,)).fetchall()
    conn.close()
    if not rows: return await update.message.reply_text("😢 کلکسیونت خالیه!")
    text = "📚 **کلکسیون شما:**\n"
    for r in rows: text += f"{EMO.get(r[2],'⚪')} `#{r[0]}` {r[1]}\n"
    await update.message.reply_text(text)

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db(); uid = update.effective_user.id
    conn.execute("INSERT OR IGNORE INTO u (id) VALUES (?)", (uid,))
    r = conn.execute("SELECT daily FROM u WHERE id=?", (uid,)).fetchone()
    now = datetime.now()
    if r and r[0] and (now - datetime.fromisoformat(r[0])) < timedelta(days=1):
        conn.close(); return await update.message.reply_text("⏰ امروز جایزه گرفتی!")
    conn.execute("UPDATE u SET coins=coins+500, daily=? WHERE id=?", (now.isoformat(), uid))
    conn.commit(); conn.close()
    await update.message.reply_text("💰 **+۵۰۰ سکه!**")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db(); rows = conn.execute("SELECT id, xp FROM u ORDER BY xp DESC LIMIT 10").fetchall(); conn.close()
    text = "🏆 **TOP 10:**\n"
    for i, r in enumerate(rows, 1): text += f"{i}. `{r[0]}` — {r[1]} XP\n"
    await update.message.reply_text(text)

async def gtop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db(); rows = conn.execute("SELECT id, xp FROM u ORDER BY xp DESC LIMIT 10").fetchall(); conn.close()
    text = "🌍 **GLOBAL TOP 10:**\n"
    for i, r in enumerate(rows, 1): text += f"{i}. `{r[0]}` — {r[1]} XP\n"
    await update.message.reply_text(text)

async def lb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id; conn = db()
    if conn.execute("SELECT coins FROM u WHERE id=?", (uid,)).fetchone()[0] < 1000:
        conn.close(); return await update.message.reply_text("❌ ۱۰۰۰ سکه نیاز است!")
    conn.execute("UPDATE u SET coins=coins-1000 WHERE id=?", (uid,))
    ch = conn.execute("SELECT code, name, rar FROM c ORDER BY RANDOM() LIMIT 1").fetchone()
    if not ch:
        conn.close(); return await update.message.reply_text("⚠️ خالیه!")
    conn.execute("INSERT OR IGNORE INTO h (uid, code) VALUES (?,?)", (uid, ch[0]))
    conn.commit(); conn.close()
    await update.message.reply_text(f"🎁 {EMO.get(ch[2],'⚪')} **{ch[1]}**!")

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("مثال: /sell 1")
    code = int(context.args[0]); conn = db()
    r = conn.execute("SELECT rar FROM c WHERE code=?", (code,)).fetchone()
    if not r:
        conn.close(); return await update.message.reply_text("❌ نیست!")
    val = REW.get(r[0], 50) // 2
    conn.execute("DELETE FROM h WHERE uid=? AND code=?", (update.effective_user.id, code))
    conn.execute("UPDATE u SET coins=coins+? WHERE id=?", (val, update.effective_user.id))
    conn.commit(); conn.close()
    await update.message.reply_text(f"💸 فروختی! +{val} سکه")

async def show_char(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("مثال: /s 1")
    try: code = int(context.args[0])
    except: return await update.message.reply_text("❌ کد باید عدد باشد!")
    conn = db()
    c = conn.execute("SELECT code, name, anime, rar, vid FROM c WHERE code=?", (code,)).fetchone()
    if not c:
        conn.close(); return await update.message.reply_text("❌ پیدا نشد!")
    owners = conn.execute("SELECT COUNT(*) FROM h WHERE code=?", (code,)).fetchone()[0]
    conn.close()
    cap = f"✨ {EMO.get(c[3],'⚪')} **{c[1]}** ✨\n📺 انیمه: {c[2]}\n🔢 کد: {c[0]}\n📊 راریتی: {c[3]}\n👥 صاحبان: {owners}"
    try: await update.message.reply_video(video=c[4], caption=cap)
    except: await update.message.reply_text(cap)

async def fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("مثال: /fav 1")
    code = int(context.args[0]); conn = db()
    conn.execute("INSERT OR IGNORE INTO h (uid, code) VALUES (?,?)", (update.effective_user.id, code))
    conn.commit(); conn.close()
    await update.message.reply_text("⭐ اضافه شد!")

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN: await update.message.reply_text("📤 ویدیو با کپشن:\n`اسم | انیمه | راریتی`\nسطوح: Common, Rare, Epic, Legendary, Mythic")

async def listchars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN: return
    conn = db(); rows = conn.execute("SELECT code, name, anime, rar FROM c ORDER BY code").fetchall(); conn.close()
    if not rows: return await update.message.reply_text("خالیه!")
    text = f"📋 **LIST ({len(rows)}):**\n"
    for r in rows: text += f"`#{r[0]}` {EMO.get(r[3],'⚪')} {r[1]}\n"
    await update.message.reply_text(text)

async def add_vid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN: return
    v = update.message.video or update.message.animation
    if not v or not update.message.caption: return
    p = [x.strip() for x in update.message.caption.split("|")]
    if len(p) != 3 or p[2] not in REW: return await update.message.reply_text("❌ فرمت اشتباه!")
    conn = db(); conn.execute("INSERT OR REPLACE INTO c (name, anime, rar, vid) VALUES (?,?,?,?)", (p[0], p[1], p[2], v.file_id)); conn.commit()
    code = conn.execute("SELECT code FROM c WHERE name=?", (p[0],)).fetchone()[0]
    conn.close()
    await update.message.reply_text(f"✅ #{code} - {p[0]} ({p[2]})")

async def spawn_c(ctx, chat, rid=None):
    conn = db()
    if rid: conn.execute("DELETE FROM act WHERE chat=?", (chat,))
    elif conn.execute("SELECT 1 FROM act WHERE chat=?", (chat,)).fetchone(): return conn.close()
    chars = conn.execute("SELECT code, name, rar, vid FROM c WHERE code NOT IN (SELECT code FROM hist WHERE chat=?)", (chat,)).fetchall()
    if not chars: return conn.close()
    wl = []
    for x in chars:
        for _ in range(W.get(x[2], 1)): wl.append(x)
    ch = random.choice(wl)
    conn.execute("INSERT INTO act (chat, code) VALUES (?,?)", (chat, ch[0]))
    conn.execute("INSERT OR IGNORE INTO hist (chat, code) VALUES (?,?)", (chat, ch[0])); conn.commit(); conn.close()
    cap = f"✨ 𝐀 𝐋𝐄𝐆𝐄𝐍𝐃 𝐀𝐏𝐏𝐄𝐀𝐑𝐒 ✨\n━━━━━━━━━━━━━━━\n{EMO.get(ch[2],'⚪')} 𝐑𝐚𝐫𝐢𝐭𝐲: {ch[2]}\n━━━━━━━━━━━━━━━\n⌨️ 𝐓𝐲𝐩𝐞 𝐭𝐡𝐞 𝐧𝐚𝐦𝐞 𝐢𝐧 𝐜𝐡𝐚𝐭!"
    try:
        if rid: await ctx.bot.send_video(chat_id=chat, video=ch[3], caption=cap, reply_to_message_id=rid)
        else: await ctx.bot.send_video(chat_id=chat, video=ch[3], caption=cap)
    except Exception as e: print(f"ERROR: {e}")

async def spawn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN: await spawn_c(context, update.effective_chat.id)

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if update.effective_user.is_bot: return
    chat = update.effective_chat.id; txt = update.message.text.strip()
    if txt.startswith("/"): return
    conn = db()
    conn.execute("INSERT OR IGNORE INTO s (chat, cnt) VALUES (?,0)", (chat,))
    conn.execute("UPDATE s SET cnt=cnt+1 WHERE chat=?", (chat,))
    cnt = conn.execute("SELECT cnt FROM s WHERE chat=?", (chat,)).fetchone()[0]
    if cnt >= LIMIT:
        conn.execute("UPDATE s SET cnt=0 WHERE chat=?", (chat,)); conn.commit(); conn.close()
        await spawn_c(context, chat, update.message.message_id); return
    act = conn.execute("SELECT c.code, c.name, c.rar FROM act a JOIN c ON a.code=c.code WHERE a.chat=?", (chat,)).fetchone()
    if act and txt.lower() == act[1].lower():
        uid = update.effective_user.id; rw = REW.get(act[2], 50)
        conn.execute("INSERT OR IGNORE INTO u (id) VALUES (?)", (uid,))
        conn.execute("UPDATE u SET coins=coins+?, xp=xp+10, strk=strk+1 WHERE id=?", (rw, uid))
        conn.execute("INSERT INTO h (uid, code) VALUES (?,?)", (uid, act[0]))
        conn.execute("DELETE FROM act WHERE chat=?", (chat,))
        r = conn.execute("SELECT xp, lvl FROM u WHERE id=?", (uid,)).fetchone()
        nl = (r[0] // 100) + 1; lv_up = ""
        if nl > r[1]:
            conn.execute("UPDATE u SET lvl=?, coins=coins+200 WHERE id=?", (nl, uid))
            lv_up = f"\n🎖 **LEVEL UP!** {nl} +۲۰۰ سکه"
        conn.commit(); conn.close()
        await update.message.reply_text(f"{random.choice(CM)}\n{EMO.get(act[2],'⚪')} **{update.effective_user.first_name}** کاراکتر **{act[1]}** رو گرفت!\n💰 +{rw} سکه{lv_up}")
    else: conn.close()

def main():
    db()
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("me", profile))
    app.add_handler(CommandHandler("harem", harem))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("gtop", gtop))
    app.add_handler(CommandHandler("lb", lb))
    app.add_handler(CommandHandler("sell", sell))
    app.add_handler(CommandHandler("s", show_char))
    app.add_handler(CommandHandler("fav", fav))
    app.add_handler(CommandHandler("upload", upload))
    app.add_handler(CommandHandler("listchars", listchars))
    app.add_handler(CommandHandler("spawn", spawn))
    app.add_handler(MessageHandler(filters.VIDEO | filters.ANIMATION, add_vid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))
    print("Bot Started on Cloud!")
    app.run_polling()

if __name__ == "__main__":
    main()
