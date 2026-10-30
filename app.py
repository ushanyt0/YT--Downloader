import re
import threading
from flask import Flask, jsonify, request
import yt_dlp

DEFAULT_URL = "https://youtu.be/gwov8azLd2Q?si=0O47vcjsMwJBmP9_"
OUT = "/storage/emulated/0/Download"

app = Flask(__name__)
state = {"status": "idle", "percent": 0, "code": "ready", "detail": ""}

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>YT Downloader</title>
<style>
body{font-family:sans-serif;background:#0d1117;color:#e6edf3;max-width:480px;margin:auto;padding:16px}
input,select,button{width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #30363d;background:#161b22;color:#e6edf3;font-size:16px;box-sizing:border-box}
button{background:#238636;border:0;font-weight:bold}
label.c{display:flex;align-items:center;gap:8px;margin:8px 0}
label.c input{width:auto;margin:0}
.bar{background:#30363d;border-radius:8px;height:22px;overflow:hidden;margin-top:12px}
#fill{background:#238636;height:100%;width:0%;transition:width .3s}
#msg{margin-top:8px;word-break:break-word}
</style></head><body>
<select id="lang" onchange="setLang(this.value)">
<option value="en">English</option>
<option value="si">සිංහල</option>
<option value="ta">தமிழ்</option>
<option value="hi">हिन्दी</option>
</select>
<h2>YT Downloader</h2>
<input id="url" value="https://youtu.be/gwov8azLd2Q?si=0O47vcjsMwJBmP9_">
<select id="mode" onchange="fill()">
<option value="video" data-k="video"></option>
<option value="audio" data-k="audio"></option>
</select>
<select id="quality"></select>
<label class="c"><input type="checkbox" id="playlist"><span data-k="playlist"></span></label>
<label class="c"><input type="checkbox" id="subs"><span data-k="subs"></span></label>
<button onclick="go()" data-k="go"></button>
<div class="bar"><div id="fill"></div></div>
<div id="msg"></div>
<script>
var L={
en:{video:"Video",audio:"Audio (MP3)",best:"Best available",high:"High",med:"Medium",low:"Low",playlist:"Download whole playlist",subs:"Subtitles (English)",go:"Download",ready:"Ready",starting:"Starting...",downloading:"Downloading...",processing:"Processing...",done:"Done! Check your Download folder",error:"Error",busy:"A download is already running"},
si:{video:"Video",audio:"Audio (MP3)",best:"ලබාගත හැකි හොඳම",high:"ඉහළ",med:"මධ්‍යම",low:"අඩු",playlist:"Playlist එක සම්පූර්ණයෙන්ම",subs:"Subtitles (English)",go:"Download කරන්න",ready:"සූදානම්",starting:"පටන් ගන්නවා...",downloading:"Download වෙනවා...",processing:"සකස් කරනවා...",done:"Download ඉවරයි! Download folder එක බලන්න",error:"Error",busy:"දැනටමත් download එකක් යනවා"},
ta:{video:"வீடியோ",audio:"ஆடியோ (MP3)",best:"கிடைக்கும் சிறந்தது",high:"உயர்",med:"நடுத்தரம்",low:"குறைவு",playlist:"முழு பிளேலிஸ்ட்டையும் பதிவிறக்கு",subs:"வசனங்கள் (English)",go:"பதிவிறக்கு",ready:"தயார்",starting:"தொடங்குகிறது...",downloading:"பதிவிறக்கப்படுகிறது...",processing:"செயலாக்கப்படுகிறது...",done:"முடிந்தது! Download folder-ஐப் பாருங்கள்",error:"பிழை",busy:"ஒரு பதிவிறக்கம் ஏற்கனவே நடக்கிறது"},
hi:{video:"वीडियो",audio:"ऑडियो (MP3)",best:"सबसे अच्छी उपलब्ध",high:"उच्च",med:"मध्यम",low:"कम",playlist:"पूरी प्लेलिस्ट डाउनलोड करें",subs:"सबटाइटल (English)",go:"डाउनलोड करें",ready:"तैयार",starting:"शुरू हो रहा है...",downloading:"डाउनलोड हो रहा है...",processing:"प्रोसेस हो रहा है...",done:"हो गया! Download folder देखें",error:"त्रुटि",busy:"एक डाउनलोड पहले से चल रहा है"}
};
var lang="si";
try{lang=localStorage.getItem("lang")||"si";}catch(e){}
if(!L[lang]){lang="si";}
var last={code:"ready",percent:0,status:"idle",detail:""};
var timer=null;
function fill(){
  var t=L[lang];
  var q=document.getElementById("quality");
  var old=q.value;
  var m=document.getElementById("mode").value;
  var list=(m==="video")
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
function show(s){
  last=s;
  var t=L[lang];
  var m=t[s.code]||"";
  if(s.detail){m+=": "+s.detail;}
  if(s.status==="running"||s.status==="done"){m+=" ("+s.percent+"%)";}
  document.getElementById("fill").style.width=s.percent+"%";
  document.getElementById("msg").innerText=m;
}
function apply(){
  var t=L[lang];
  var els=document.querySelectorAll("[data-k]");
  for(var i=0;i<els.length;i++){
    els[i].textContent=t[els[i].getAttribute("data-k")];
  }
  fill();
  show(last);
}
function setLang(v){
  lang=v;
  try{localStorage.setItem("lang",v);}catch(e){}
  apply();
}
document.getElementById("lang").value=lang;
apply();
function go(){
  fetch("/start",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({
    url:document.getElementById("url").value,
    mode:document.getElementById("mode").value,
    quality:document.getElementById("quality").value,
    playlist:document.getElementById("playlist").checked,
    subs:document.getElementById("subs").checked})})
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
    if(s.status!=="running"){clearInterval(timer);}
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
    if playlist:
        name = "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"
    else:
        name = "%(title)s.%(ext)s"
    opts = {
        "outtmpl": OUT + "/" + name,
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
    url = (d.get("url") or "").strip() or DEFAULT_URL
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


if __name__ == "__main__":
    print("Browser එකේ open කරන්න: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000)
