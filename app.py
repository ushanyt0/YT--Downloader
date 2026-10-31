import os
import re
import shutil
import threading
import time
from flask import Flask, jsonify, request, send_file
import yt_dlp

TMP = os.path.expanduser("~/yt_tmp")

app = Flask(__name__)
state = {"status": "idle", "percent": 0, "code": "ready", "detail": ""}
result = {"path": None}

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>All-in-One Downloader</title>
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;font-family:system-ui,sans-serif;color:#e8ecf4;background:radial-gradient(900px 500px at 0% -10%,#4c1d9566,transparent),radial-gradient(800px 500px at 100% 0%,#0e749066,transparent),#0b0f1a;padding:20px 16px}
.wrap{width:100%;max-width:460px;margin:0 auto}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:18px}
.logo i{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,#8b5cf6,#06b6d4);display:flex;align-items:center;justify-content:center;font-style:normal;font-size:18px}
.card{background:#ffffff0d;border:1px solid #ffffff1f;border-radius:20px;padding:18px}
h1{font-size:22px;margin:0 0 4px}
.sub{color:#9aa4b8;margin:0 0 14px;font-size:14px}
.tabs{display:flex;gap:6px;overflow-x:auto;margin-bottom:12px;padding-bottom:2px}
.tab{flex:0 0 auto;padding:8px 14px;border-radius:999px;border:1px solid #ffffff22;background:#ffffff0f;color:#cfd6e6;font-size:13px;font-weight:600;white-space:nowrap}
.tab.on{background:linear-gradient(135deg,#8b5cf6,#06b6d4);color:#fff;border-color:transparent}
input[type=text],select{width:100%;padding:13px 14px;margin:6px 0;border-radius:12px;border:1px solid #ffffff22;background:#0b0f1acc;color:#e8ecf4;font-size:16px}
#lang{width:auto;padding:8px 12px;margin:0;font-size:14px;border-radius:10px}
.seg{display:flex;background:#0b0f1acc;border:1px solid #ffffff22;border-radius:12px;padding:4px;margin:6px 0}
.seg button{flex:1;padding:10px;border:0;border-radius:9px;background:transparent;color:#9aa4b8;font-size:15px;font-weight:600}
.seg button.on{background:linear-gradient(135deg,#8b5cf6,#06b6d4);color:#fff}
label.c{display:flex;align-items:center;gap:10px;margin:10px 2px;color:#cfd6e6;font-size:15px}
label.c input{width:18px;height:18px;margin:0}
.go{width:100%;padding:14px;margin-top:8px;border:0;border-radius:12px;background:linear-gradient(135deg,#8b5cf6,#06b6d4);color:#fff;font-size:17px;font-weight:700}
.bar{height:10px;border-radius:999px;background:#ffffff1a;overflow:hidden;margin-top:16px}
#fill{height:100%;width:0%;background:linear-gradient(90deg,#8b5cf6,#06b6d4);transition:width .3s}
#msg{margin-top:10px;font-size:14px;color:#cfd6e6;word-break:break-word}
.btn{display:none;text-align:center;padding:13px;margin-top:12px;border-radius:12px;background:#22c55e;color:#04210f;text-decoration:none;font-weight:700}
.note{color:#7d879b;font-size:12px;text-align:center;margin-top:14px}
.foot{margin-top:22px;text-align:center;color:#7d879b;font-size:12px}
.foot b{color:#c4b5fd}
</style></head><body><div class="wrap">
<div class="top">
<div class="logo"><i>⬇</i><span>All-in-One</span></div>
<select id="lang" onchange="setLang(this.value)">
<option value="en">English</option>
<option value="si">සිංහල</option>
<option value="ta">தமிழ்</option>
<option value="hi">हिन्दी</option>
</select>
</div>
<div class="card">
<h1>All-in-One Downloader</h1>
<p class="sub" data-k="sub"></p>
<div class="tabs">
<button class="tab on" id="p_auto" onclick="setPlat('auto')" data-k="auto"></button>
<button class="tab" id="p_youtube" onclick="setPlat('youtube')">YouTube</button>
<button class="tab" id="p_facebook" onclick="setPlat('facebook')">Facebook</button>
<button class="tab" id="p_instagram" onclick="setPlat('instagram')">Instagram</button>
<button class="tab" id="p_tiktok" onclick="setPlat('tiktok')">TikTok</button>
</div>
<input type="text" id="url" inputmode="url" onfocus="this.select()" value="https://youtu.be/gwov8azLd2Q?si=0O47vcjsMwJBmP9_">
<div class="seg">
<button id="m_video" onclick="setMode('video')" data-k="video"></button>
<button id="m_audio" onclick="setMode('audio')" data-k="audio"></button>
</div>
<select id="quality"></select>
<div id="yt_only">
<label class="c"><input type="checkbox" id="playlist"><span data-k="playlist"></span></label>
<label class="c"><input type="checkbox" id="subs"><span data-k="subs"></span></label>
</div>
<button class="go" onclick="go()" data-k="go"></button>
<div class="bar"><div id="fill"></div></div>
<div id="msg"></div>
<a id="save" class="btn" href="/file" data-k="save"></a>
<div class="note" data-k="note"></div>
</div>
<div class="foot">Powered by <b>Shan codex</b></div>
</div>
<script>
var L={
en:{sub:"Pick a platform, paste a link, choose the quality.",auto:"All sites",note:"Only download content you have the right to.",video:"Video",audio:"Audio (MP3)",best:"Best available",high:"High",med:"Medium",low:"Low",playlist:"Download whole playlist",subs:"Subtitles (English)",go:"Download",save:"Save file",ready:"Ready",starting:"Starting...",downloading:"Downloading...",processing:"Processing...",done:"Done! Saving the file...",error:"Error",busy:"A download is already running",empty:"Please paste a valid link",wrongsite:"This link doesn't match the selected platform"},
si:{sub:"Platform එක තෝරන්න, link එක දාන්න, quality එක තෝරන්න.",auto:"සියලුම sites",note:"ඔයාට අයිතිය තියෙන content විතරක් download කරන්න.",video:"Video",audio:"Audio (MP3)",best:"ලබාගත හැකි හොඳම",high:"ඉහළ",med:"මධ්‍යම",low:"අඩු",playlist:"Playlist එක සම්පූර්ණයෙන්ම",subs:"Subtitles (English)",go:"Download කරන්න",save:"File එක save කරන්න",ready:"සූදානම්",starting:"පටන් ගන්නවා...",downloading:"Download වෙනවා...",processing:"සකස් කරනවා...",done:"ඉවරයි! File එක save වෙනවා...",error:"Error",busy:"දැනටමත් download එකක් යනවා",empty:"හරි link එකක් දාන්න",wrongsite:"මේ link එක තෝරපු platform එකට ගැලපෙන්නේ නෑ"},
ta:{sub:"தளத்தைத் தேர்ந்தெடுத்து, இணைப்பை ஒட்டி, தரத்தைத் தேர்ந்தெடுக்கவும்.",auto:"அனைத்தும்",note:"உங்களுக்கு உரிமை உள்ள உள்ளடக்கத்தை மட்டும் பதிவிறக்கவும்.",video:"வீடியோ",audio:"ஆடியோ (MP3)",best:"கிடைக்கும் சிறந்தது",high:"உயர்",med:"நடுத்தரம்",low:"குறைவு",playlist:"முழு பிளேலிஸ்ட்டையும் பதிவிறக்கு",subs:"வசனங்கள் (English)",go:"பதிவிறக்கு",save:"கோப்பைச் சேமி",ready:"தயார்",starting:"தொடங்குகிறது...",downloading:"பதிவிறக்கப்படுகிறது...",processing:"செயலாக்கப்படுகிறது...",done:"முடிந்தது! கோப்பு சேமிக்கப்படுகிறது...",error:"பிழை",busy:"ஒரு பதிவிறக்கம் ஏற்கனவே நடக்கிறது",empty:"சரியான இணைப்பை ஒட்டவும்",wrongsite:"இந்த இணைப்பு தேர்ந்தெடுத்த தளத்துடன் பொருந்தவில்லை"},
hi:{sub:"प्लेटफ़ॉर्म चुनें, लिंक पेस्ट करें और क्वालिटी चुनें।",auto:"सभी साइट",note:"केवल वही कंटेंट डाउनलोड करें जिसका आपको अधिकार है।",video:"वीडियो",audio:"ऑडियो (MP3)",best:"सबसे अच्छी उपलब्ध",high:"उच्च",med:"मध्यम",low:"कम",playlist:"पूरी प्लेलिस्ट डाउनलोड करें",subs:"सबटाइटल (English)",go:"डाउनलोड करें",save:"फ़ाइल सेव करें",ready:"तैयार",starting:"शुरू हो रहा है...",downloading:"डाउनलोड हो रहा है...",processing:"प्रोसेस हो रहा है...",done:"हो गया! फ़ाइल सेव हो रही है...",error:"त्रुटि",busy:"एक डाउनलोड पहले से चल रहा है",empty:"सही लिंक पेस्ट करें",wrongsite:"यह लिंक चुने हुए प्लेटफ़ॉर्म से मेल नहीं खाता"}
};
var EXAMPLE="https://youtu.be/gwov8azLd2Q?si=0O47vcjsMwJBmP9_";
var P={auto:[],youtube:["youtube.com","youtu.be"],facebook:["facebook.com","fb.watch","fb.com"],instagram:["instagram.com","instagr.am"],tiktok:["tiktok.com"]};
var H={auto:"https://...",youtube:"https://youtu.be/...",facebook:"https://www.facebook.com/.../videos/...",instagram:"https://www.instagram.com/reel/...",tiktok:"https://www.tiktok.com/@user/video/..."};
var lang="si";
try{lang=localStorage.getItem("lang")||"si";}catch(e){}
if(!L[lang]){lang="si";}
var mode="video";
var plat="auto";
var last={code:"ready",percent:0,status:"idle",detail:""};
var timer=null;
function fill(){
  var t=L[lang];
  var q=document.getElementById("quality");
  var old=q.value;
  var list=(mode==="video")
    ?[["1080","1080p"],["720","720p"],["480","480p"],["360","360p"],["best",t.best]]
    :[["320",t.high+" (320k)"],["192",t.med+" (192k)"],["128",t.low+" (128k)"]];
  q.innerHTML="";
  list.forEach(function(o){
    q.innerHTML+='<option value="'+o[0]+'">'+o[1]+'</option>';
  });
  for(var i=0;i<q.options.length;i++){
    if(q.options[i].value===old){q.value=old;}
  }
}
function setMode(m){
  mode=m;
  document.getElementById("m_video").className=(m==="video")?"on":"";
  document.getElementById("m_audio").className=(m==="audio")?"on":"";
  fill();
}
function setPlat(p){
  plat=p;
  var ids=["auto","youtube","facebook","instagram","tiktok"];
  for(var i=0;i<ids.length;i++){
    document.getElementById("p_"+ids[i]).className=(ids[i]===p)?"tab on":"tab";
  }
  var u=document.getElementById("url");
  u.placeholder=H[p];
  if(p!=="auto"&&p!=="youtube"&&u.value===EXAMPLE){u.value="";}
  document.getElementById("yt_only").style.display=(p==="auto"||p==="youtube")?"block":"none";
}
function show(s){
  last=s;
  var t=L[lang];
  var m=t[s.code]||"";
  if(s.detail){m+=": "+s.detail;}
  if(s.status==="running"||s.status==="done"){m+=" ("+s.percent+"%)";}
  document.getElementById("fill").style.width=s.percent+"%";
  document.getElementById("msg").innerText=m;
  document.getElementById("save").style.display=(s.status==="done")?"block":"none";
}
function apply(){
  var t=L[lang];
  var els=document.querySelectorAll("[data-k]");
  for(var i=0;i<els.length;i++){
    els[i].textContent=t[els[i].getAttribute("data-k")];
  }
  setMode(mode);
  show(last);
}
function setLang(v){
  lang=v;
  try{localStorage.setItem("lang",v);}catch(e){}
  apply();
}
document.getElementById("lang").value=lang;
apply();
setPlat("auto");
function go(){
  var u=document.getElementById("url").value.trim();
  var low=u.toLowerCase();
  if(low.indexOf("http://")!==0&&low.indexOf("https://")!==0){
    show({code:"empty",percent:0,status:"idle",detail:""});
    return;
  }
  var dom=P[plat];
  if(dom.length>0){
    var ok=false;
    for(var i=0;i<dom.length;i++){
      if(low.indexOf(dom[i])>-1){ok=true;}
    }
    if(!ok){
      show({code:"wrongsite",percent:0,status:"idle",detail:""});
      return;
    }
  }
  var yt=(plat==="auto"||plat==="youtube");
  fetch("/start",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({
    url:u,
    mode:mode,
    quality:document.getElementById("quality").value,
    playlist:yt&&document.getElementById("playlist").checked,
    subs:yt&&document.getElementById("subs").checked})})
  .then(function(r){return r.json()})
  .then(function(d){
    if(!d.ok){show({code:d.code,percent:0,status:"idle",detail:""});return;}
    clearInterval(timer);
    timer=setInterval(poll,1000);
  });
}
function poll(){
  fetch("/progress").then(function(r){return r.json()}).then(function(s){
    show(s);
    if(s.status!=="running"){
      clearInterval(timer);
      if(s.status==="done"){document.getElementById("save").click();}
    }
  });
}
</script></body></html>"""


def hook(d):
    if d["status"] == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        if total:
            state["percent"] = round(d["downloaded_bytes"] / total * 100, 1)
        state["code"] = "downloading"
    elif d["status"] == "finished":
        state["percent"] = 100
        state["code"] = "processing"


def worker(url, mode, quality, playlist, subs):
    shutil.rmtree(TMP, ignore_errors=True)
    job = os.path.join(TMP, str(int(time.time())))
    os.makedirs(job, exist_ok=True)
    result["path"] = None
    if playlist:
        name = "%(playlist_title).60s/%(playlist_index)s - %(title).100s.%(ext)s"
    else:
        name = "%(title).100s.%(ext)s"
    opts = {
        "outtmpl": job + "/" + name,
        "noplaylist": not playlist,
        "js_runtimes": {"node": {}},
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
    }
    if mode == "audio":
        opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }],
        })
    else:
        if quality == "best":
            fmt = "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/b"
        else:
            h = int(quality)
            fmt = f"bv*[height<={h}][ext=mp4]+ba[ext=m4a]/bv*[height<={h}]+ba/b[height<={h}]"
        opts.update({"format": fmt, "merge_output_format": "mp4"})
    if subs:
        opts.update({
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
        })
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        files = []
        for root, _, names in os.walk(job):
            for n in names:
                files.append(os.path.join(root, n))
        if not files:
            raise Exception("No file was created")
        if len(files) == 1:
            result["path"] = files[0]
        else:
            result["path"] = shutil.make_archive(job, "zip", job)
        state.update(status="done", percent=100, code="done", detail="")
    except Exception as e:
        err = re.sub(r"\x1b\[[0-9;]*m", "", str(e))
        state.update(status="error", code="error", detail=err[:300])


@app.route("/")
def home():
    return PAGE


@app.route("/start", methods=["POST"])
def start():
    if state["status"] == "running":
        return jsonify(ok=False, code="busy")
    d = request.get_json()
    url = (d.get("url") or "").strip()
    if not url.lower().startswith(("http://", "https://")):
        return jsonify(ok=False, code="empty")
    state.update(status="running", percent=0, code="starting", detail="")
    threading.Thread(
        target=worker,
        args=(url, d.get("mode"), d.get("quality"),
              bool(d.get("playlist")), bool(d.get("subs"))),
        daemon=True,
    ).start()
    return jsonify(ok=True)


@app.route("/progress")
def progress():
    return jsonify(state)


@app.route("/file")
def get_file():
    p = result["path"]
    if p and os.path.exists(p):
        name = "videos.zip" if p.endswith(".zip") else None
        return send_file(p, as_attachment=True, download_name=name)
    return "No file", 404


if __name__ == "__main__":
    print("Browser එකේ open කරන්න: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000)
