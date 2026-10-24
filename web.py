import base64
import json
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.Agent.agent import RoboDoctor
from src.llm.client import LLMError

doctor = RoboDoctor()
MAX_FRAMES = 6

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RoboDoctor</title>
<style>
  :root { --bg:#070b14; --panel:#0e1626; --panel2:#0a111f; --line:#1d2a44;
          --cyan:#22d3ee; --amber:#fbbf24; --green:#4ade80; --red:#f87171;
          --text:#d7e3f4; --muted:#7b8ba8;
          --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
  * { box-sizing:border-box; }
  body { margin:0; color:var(--text); font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;
         background:
           radial-gradient(1200px 500px at 50% -10%, #12335a55, transparent),
           linear-gradient(var(--line) 1px, transparent 1px) 0 0/40px 40px,
           linear-gradient(90deg, var(--line) 1px, transparent 1px) 0 0/40px 40px,
           var(--bg);
         background-blend-mode:normal,soft-light,soft-light,normal; min-height:100vh; }

  /* ---------- header ---------- */
  header { max-width:1100px; margin:0 auto; padding:28px 16px 8px;
           display:flex; align-items:center; gap:24px; flex-wrap:wrap; justify-content:center; }
  #bot { width:150px; height:150px; flex:none; filter:drop-shadow(0 0 18px #22d3ee55); }
  .titles h1 { margin:0; font:800 38px/1.1 var(--mono); letter-spacing:.04em; }
  .titles h1 span { color:var(--cyan); text-shadow:0 0 14px #22d3ee88; }
  .titles p { margin:6px 0 10px; color:var(--muted); }
  .sysline { display:inline-flex; align-items:center; gap:10px; font:600 12px var(--mono);
             letter-spacing:.12em; padding:6px 12px; border:1px solid var(--line);
             border-radius:999px; background:var(--panel2); }
  .led { width:9px; height:9px; border-radius:50%; background:var(--green);
         box-shadow:0 0 10px var(--green); }
  [data-state=scan] ~ * .led, body[data-state=scan] .led { background:var(--amber); box-shadow:0 0 10px var(--amber); animation:pulse .6s infinite alternate; }
  body[data-state=error] .led { background:var(--red); box-shadow:0 0 10px var(--red); }

  /* ---------- robot svg ---------- */
  .head { fill:#16233b; stroke:var(--cyan); stroke-width:3; }
  .ear { fill:#0f1a2e; stroke:var(--cyan); stroke-width:3; }
  .screen { fill:#050a14; stroke:#1f3a5f; stroke-width:2; }
  .eye { fill:#0b3a4a; stroke:var(--cyan); stroke-width:2; }
  .pupil { fill:var(--cyan); transition:transform .12s ease-out; }
  .eyeg { transform-box:fill-box; transform-origin:center; animation:blink 5s infinite; }
  .mouth { fill:none; stroke:var(--cyan); stroke-width:4; stroke-linecap:round; transition:d .2s; }
  .ant { stroke:var(--cyan); stroke-width:3; }
  .bulb { fill:var(--green); }
  #bot[data-state=scan] .bulb { fill:var(--amber); animation:pulse .5s infinite alternate; }
  #bot[data-state=scan] .pupils { animation:look .9s ease-in-out infinite alternate; }
  #bot[data-state=scan] .pupil, #bot[data-state=scan] .mouth { stroke:var(--amber); fill:var(--amber); }
  #bot[data-state=scan] .mouth { fill:none; }
  #bot[data-state=happy] .bulb { fill:var(--green); }
  #bot[data-state=happy] { animation:hop .5s 2; }
  #bot[data-state=error] .bulb { fill:var(--red); animation:pulse .3s infinite alternate; }
  #bot[data-state=error] .pupil { fill:var(--red); }
  #bot[data-state=error] .mouth { stroke:var(--red); }
  #bot[data-state=error] { animation:shake .4s 2; }
  @keyframes blink { 0%,92%,100%{transform:scaleY(1)} 95%{transform:scaleY(.1)} }
  @keyframes look { from{transform:translateX(-6px)} to{transform:translateX(6px)} }
  @keyframes pulse { from{opacity:.35} to{opacity:1} }
  @keyframes hop { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
  @keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-6px)} 75%{transform:translateX(6px)} }

  /* ---------- layout ---------- */
  main { max-width:1100px; margin:0 auto; padding:16px; display:grid; gap:18px;
         grid-template-columns:1fr 1fr; }
  @media (max-width:860px) { main { grid-template-columns:1fr; } }
  .panel { background:var(--panel); border:1px solid var(--line); border-radius:14px;
           position:relative; box-shadow:0 10px 40px rgba(0,0,0,.35); overflow:hidden; }
  .panel::before, .panel::after { content:""; position:absolute; width:8px; height:8px;
           border-radius:50%; background:#26385c; bottom:10px; }
  .panel::before { left:10px; } .panel::after { right:10px; }
  .phead { display:flex; align-items:center; justify-content:space-between; padding:10px 14px;
           background:var(--panel2); border-bottom:1px solid var(--line);
           font:700 12px var(--mono); letter-spacing:.14em; color:var(--cyan); }
  .dots span { display:inline-block; width:8px; height:8px; border-radius:50%; margin-left:5px; background:#26385c; }
  .dots span:first-child { background:var(--red); } .dots span:nth-child(2){ background:var(--amber); }
  .dots span:nth-child(3){ background:var(--green); }
  .pbody { padding:16px 16px 28px; }

  label { display:block; font:700 12px var(--mono); letter-spacing:.1em; color:var(--muted); margin-bottom:6px; }
  textarea { width:100%; min-height:100px; padding:12px; resize:vertical; color:var(--text);
             background:#050a14; border:1px solid var(--line); border-radius:10px; font:14px var(--mono); }
  textarea:focus { outline:none; border-color:var(--cyan); box-shadow:0 0 0 3px #22d3ee22; }

  .chips { display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 16px; }
  .chip { display:flex; gap:6px; align-items:center; border:1px solid var(--line); background:var(--panel2);
          color:var(--text); padding:5px 10px; border-radius:8px; font-size:12px; cursor:pointer; text-align:left; }
  .chip b { color:var(--amber); font-family:var(--mono); }
  .chip:hover { border-color:var(--cyan); box-shadow:0 0 12px #22d3ee33; }

  .bay { position:relative; border:2px dashed #26385c; border-radius:12px; padding:18px;
         text-align:center; color:var(--muted); cursor:pointer; overflow:hidden; background:#050a14; }
  .bay.over { border-color:var(--cyan); color:var(--cyan); box-shadow:inset 0 0 30px #22d3ee22; }
  .bay .icon { font-size:30px; display:block; }
  .bay small { display:block; margin-top:2px; }
  #preview-img, #preview-vid { display:none; max-width:100%; max-height:200px; border-radius:8px; margin:12px auto 0; }
  .bay.scanning::after { content:""; position:absolute; left:0; right:0; height:3px; top:0;
         background:linear-gradient(90deg, transparent, var(--cyan), transparent);
         box-shadow:0 0 18px var(--cyan); animation:sweep 1.4s linear infinite; }
  @keyframes sweep { from{top:0} to{top:100%} }
  #fileInfo { font:12px var(--mono); color:var(--muted); }
  #remove { display:none; background:none; border:0; color:var(--red); cursor:pointer; font:12px var(--mono); padding:0 0 0 8px; }

  #go { width:100%; margin-top:16px; padding:14px; border-radius:10px; cursor:pointer;
        font:800 15px var(--mono); letter-spacing:.15em; color:#031018;
        background:linear-gradient(135deg,var(--cyan),#38bdf8); border:0;
        box-shadow:0 0 22px #22d3ee55; transition:transform .1s; }
  #go:hover { transform:translateY(-1px); }
  #go:disabled { opacity:.55; cursor:wait; box-shadow:none; }

  /* ---------- console ---------- */
  #console { height:440px; overflow:auto; padding:14px; font:13.5px/1.55 var(--mono); background:#050a14; }
  .msg { margin-bottom:14px; white-space:pre-wrap; word-break:break-word; }
  .who { font-weight:700; letter-spacing:.08em; margin-bottom:2px; }
  .you .who { color:var(--amber); } .bot .who { color:var(--cyan); }
  .you .txt { color:#ffe9b0; } .bot .txt { color:#cdeffa; }
  .msg img, .msg video { display:block; max-width:180px; border-radius:6px; margin-top:6px; border:1px solid var(--line); }
  .caret::after { content:"\\2588"; color:var(--cyan); animation:pulse .5s infinite alternate; }
  .think::after { content:""; animation:dots 1.2s steps(4) infinite; }
  @keyframes dots { 0%{content:""} 25%{content:"."} 50%{content:".."} 75%{content:"..."} }
  #clear { background:none; border:1px solid var(--line); color:var(--muted); border-radius:6px;
           font:11px var(--mono); padding:3px 8px; cursor:pointer; }
  #clear:hover { color:var(--text); border-color:var(--muted); }

  .foot { text-align:center; color:var(--muted); font-size:12px; padding:6px 16px 36px; font-family:var(--mono); }
  @media (prefers-reduced-motion: reduce) { * { animation:none !important; transition:none !important; } }
</style></head>
<body data-state="idle">
<header>
  <svg id="bot" data-state="idle" viewBox="0 0 200 200" aria-label="RoboDoctor robot face">
    <line class="ant" x1="100" y1="46" x2="100" y2="22"/>
    <circle class="bulb" cx="100" cy="18" r="7"/>
    <rect class="ear" x="12" y="88" width="20" height="44" rx="8"/>
    <rect class="ear" x="168" y="88" width="20" height="44" rx="8"/>
    <rect class="head" x="28" y="46" width="144" height="124" rx="28"/>
    <rect class="screen" x="44" y="64" width="112" height="82" rx="16"/>
    <g class="eyeg"><ellipse class="eye" cx="76" cy="96" rx="15" ry="17"/>
      <g class="pupils"><circle class="pupil" cx="76" cy="96" r="7"/></g></g>
    <g class="eyeg"><ellipse class="eye" cx="124" cy="96" rx="15" ry="17"/>
      <g class="pupils"><circle class="pupil" cx="124" cy="96" r="7"/></g></g>
    <path id="mouth" class="mouth" d="M82 130 Q100 138 118 130"/>
    <circle cx="48" cy="158" r="3" fill="#26385c"/><circle cx="152" cy="158" r="3" fill="#26385c"/>
  </svg>
  <div class="titles">
    <h1>ROBO<span>DOCTOR</span></h1>
    <p>Robot repair bay. Describe the fault, scan a photo or a short video.</p>
    <div class="sysline"><span class="led"></span> SYSTEM: <span id="sys">STANDBY</span></div>
  </div>
</header>

<main>
  <section class="panel">
    <div class="phead"><span>&#9638; FAULT REPORT</span><span class="dots"><span></span><span></span><span></span></span></div>
    <div class="pbody">
      <label for="text">&gt; DESCRIBE THE SYMPTOMS</label>
      <textarea id="text" placeholder="e.g. My robot turns on but the wheels don't move..."></textarea>
      <div class="chips" id="chips"></div>

      <label>&gt; SCANNER BAY (PHOTO OR VIDEO)</label>
      <div class="bay" id="drop">
        <span class="icon">&#128247;</span>Drop a photo or short video, or click to browse
        <small>Videos are sampled into 4 frames in your browser</small>
        <img id="preview-img" alt="preview">
        <video id="preview-vid" controls muted playsinline></video>
      </div>
      <input type="file" id="file" accept="image/*,video/*" hidden>
      <div><span id="fileInfo"></span><button id="remove" type="button">[ eject ]</button></div>

      <button id="go">RUN DIAGNOSTIC</button>
    </div>
  </section>

  <section class="panel">
    <div class="phead"><span>&#9638; DIAGNOSTIC CONSOLE</span><button id="clear" type="button">CLEAR</button></div>
    <div id="console"></div>
  </section>
</main>
<p class="foot">&#9888; Power the robot off before inspecting wiring or batteries.</p>

<script>
const $ = id => document.getElementById(id);
const FRAME_COUNT = 4;
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let media = null;
let resetTimer = null;

/* ---------- robot face ---------- */
const bot = $("bot");
const SYS = { idle:"STANDBY", scan:"SCANNING", happy:"DIAGNOSIS READY", error:"FAULT DETECTED" };
const MOUTH = {
  idle:  "M82 130 Q100 138 118 130",
  scan:  "M84 130 L116 130",
  happy: "M78 124 Q100 148 122 124",
  error: "M82 136 Q100 120 118 136",
};
function setState(s) {
  bot.dataset.state = s;
  document.body.dataset.state = s;
  $("sys").textContent = SYS[s];
  $("mouth").setAttribute("d", MOUTH[s]);
  clearTimeout(resetTimer);
  if (s === "happy" || s === "error") resetTimer = setTimeout(() => setState("idle"), 6000);
}
const pupils = document.querySelectorAll(".pupil");
document.addEventListener("mousemove", e => {
  if (bot.dataset.state === "scan") return;
  const r = bot.getBoundingClientRect();
  const dx = Math.max(-1, Math.min(1, (e.clientX - (r.left + r.width / 2)) / 300));
  const dy = Math.max(-1, Math.min(1, (e.clientY - (r.top + r.height / 2)) / 300));
  pupils.forEach(p => { p.style.transform = "translate(" + (dx * 6) + "px," + (dy * 5) + "px)"; });
});

/* ---------- example fault codes ---------- */
const faults = [
  { code:"E-01", label:"Wheels dead",   text:"My robot turns on but the wheels don't move." },
  { code:"E-02", label:"Lidar silent",  text:"The lidar spins but I get no scan data in ROS2." },
  { code:"E-03", label:"Servo jitter",  text:"The servo in my robotic arm jitters and gets hot." },
  { code:"E-04", label:"Battery drain", text:"Battery drains in 10 minutes and the motors stutter." },
];
faults.forEach(f => {
  const b = document.createElement("button");
  b.className = "chip"; b.type = "button";
  const c = document.createElement("b"); c.textContent = f.code;
  b.append(c, document.createTextNode(f.label));
  b.onclick = () => { $("text").value = f.text; $("text").focus(); };
  $("chips").appendChild(b);
});

/* ---------- media handling ---------- */
function readAsDataURL(file) {
  return new Promise((res, rej) => {
    const r = new FileReader();
    r.onload = () => res(r.result);
    r.onerror = () => rej(new Error("Could not read file"));
    r.readAsDataURL(file);
  });
}

async function extractFrames(file, count) {
  const url = URL.createObjectURL(file);
  const v = document.createElement("video");
  v.muted = true; v.preload = "auto"; v.playsInline = true; v.src = url;
  await new Promise((res, rej) => {
    v.onloadedmetadata = res;
    v.onerror = () => rej(new Error("This browser cannot decode that video. Try MP4 (H.264) or WebM."));
  });
  const dur = v.duration;
  if (!isFinite(dur) || dur <= 0) throw new Error("Could not read the video length.");
  const scale = Math.min(1, 640 / (v.videoWidth || 640));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(v.videoWidth * scale);
  canvas.height = Math.round(v.videoHeight * scale);
  const ctx = canvas.getContext("2d");
  const frames = [];
  for (let i = 0; i < count; i++) {
    await new Promise(res => { v.onseeked = res; v.currentTime = dur * (i + 0.5) / count; });
    ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
    frames.push({ data: canvas.toDataURL("image/jpeg", 0.8).split(",")[1], ext: ".jpg" });
  }
  URL.revokeObjectURL(url);
  return frames;
}

function clearMedia() {
  media = null; $("file").value = "";
  $("preview-img").style.display = "none";
  $("preview-vid").style.display = "none";
  $("preview-vid").removeAttribute("src");
  $("remove").style.display = "none";
  $("fileInfo").textContent = "";
}

async function setFile(f) {
  if (!f) return;
  const isImg = f.type.startsWith("image/");
  const isVid = f.type.startsWith("video/");
  if (!isImg && !isVid) { $("fileInfo").textContent = "Please choose an image or a video."; return; }
  if (f.size > 200 * 1024 * 1024) { $("fileInfo").textContent = "File too large (max 200 MB)."; return; }
  clearMedia();
  $("fileInfo").textContent = isVid ? "Extracting frames..." : "";
  try {
    if (isImg) {
      const url = await readAsDataURL(f);
      const dot = f.name.lastIndexOf(".");
      media = { kind:"image", url, frames:[{ data:url.split(",")[1], ext: dot >= 0 ? f.name.slice(dot) : ".jpg" }] };
      $("preview-img").src = url; $("preview-img").style.display = "block";
      $("fileInfo").textContent = "1 image loaded.";
    } else {
      const frames = await extractFrames(f, FRAME_COUNT);
      const url = URL.createObjectURL(f);
      media = { kind:"video", url, frames };
      $("preview-vid").src = url; $("preview-vid").style.display = "block";
      $("fileInfo").textContent = frames.length + " frames ready.";
    }
    $("remove").style.display = "inline";
  } catch (err) {
    media = null;
    $("fileInfo").textContent = "ERROR: " + err.message;
  }
}

$("drop").onclick = e => { if (e.target.tagName !== "VIDEO") $("file").click(); };
$("file").onchange = e => setFile(e.target.files[0]);
$("remove").onclick = clearMedia;
["dragover","dragenter"].forEach(ev => $("drop").addEventListener(ev, e => { e.preventDefault(); $("drop").classList.add("over"); }));
["dragleave","drop"].forEach(ev => $("drop").addEventListener(ev, e => { e.preventDefault(); $("drop").classList.remove("over"); }));
$("drop").addEventListener("drop", e => setFile(e.dataTransfer.files[0]));

/* ---------- console ---------- */
const con = $("console");

function addMsg(cls, who, text, m) {
  const d = document.createElement("div"); d.className = "msg " + cls;
  const w = document.createElement("div"); w.className = "who"; w.textContent = who;
  const t = document.createElement("div"); t.className = "txt"; t.textContent = text;
  d.append(w, t);
  if (m) {
    const el = document.createElement(m.kind === "video" ? "video" : "img");
    el.src = m.url;
    if (m.kind === "video") { el.controls = true; el.muted = true; }
    d.appendChild(el);
  }
  con.appendChild(d);
  con.scrollTop = con.scrollHeight;
  return t;
}

function typeText(el, text) {
  return new Promise(resolve => {
    if (REDUCED) { el.textContent = text; resolve(); return; }
    let i = 0;
    el.classList.add("caret");
    const step = () => {
      i = Math.min(text.length, i + 3);
      el.textContent = text.slice(0, i);
      con.scrollTop = con.scrollHeight;
      if (i < text.length) setTimeout(step, 12);
      else { el.classList.remove("caret"); resolve(); }
    };
    step();
  });
}

function welcome() {
  addMsg("bot", "ROBODOCTOR >", "Systems ready. Describe the fault, or load a photo or video into the scanner bay.");
}
welcome();
$("clear").onclick = () => { con.textContent = ""; welcome(); };

/* ---------- run diagnostic ---------- */
$("go").onclick = async () => {
  const text = $("text").value.trim();
  if (!text && !media) { $("text").focus(); $("fileInfo").textContent = "Enter a symptom or load a scan first."; return; }

  const sent = media;
  const isVideo = !!sent && sent.kind === "video";
  addMsg("you", "OPERATOR >", text || (isVideo ? "(video scan only)" : "(photo scan only)"), sent);
  const body = addMsg("bot", "ROBODOCTOR >", isVideo ? "Analyzing video frames, this can take a minute" : "Analyzing");
  body.classList.add("think");

  $("go").disabled = true; $("go").textContent = "SCANNING...";
  if (sent) $("drop").classList.add("scanning");
  setState("scan");

  let answer, failed = false;
  try {
    const res = await fetch("/diagnose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, frames: sent ? sent.frames : [], is_video: isVideo }),
    });
    const data = await res.json();
    answer = data.answer;
    failed = answer.trim().startsWith("\\u274c");
  } catch (err) {
    answer = "Request failed: " + err;
    failed = true;
  }

  body.classList.remove("think");
  $("drop").classList.remove("scanning");
  setState(failed ? "error" : "happy");
  await typeText(body, answer);

  $("go").disabled = false; $("go").textContent = "RUN DIAGNOSTIC";
  $("text").value = ""; clearMedia();
};

$("text").addEventListener("keydown", e => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) $("go").click();
});
</script></body></html>"""

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self._send(404, b"Not found", "text/plain")

    def do_POST(self):
        if self.path != "/diagnose":
            self._send(404, b"Not found", "text/plain")
            return

        tmp_paths: list[str] = []
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))

            for frame in (data.get("frames") or [])[:MAX_FRAMES]:
                ext = (frame.get("ext") or ".jpg").lower()
                if ext not in IMAGE_EXTS:
                    ext = ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(base64.b64decode(frame["data"]))
                    tmp_paths.append(tmp.name)

            answer = doctor.diagnose(
                data.get("text", ""),
                image_paths=tmp_paths,
                is_video=bool(data.get("is_video")),
            )
        except LLMError as exc:
            answer = f"❌ {exc}"
        except Exception as exc:
            answer = f"❌ Something went wrong: {exc}"
        finally:
            for p in tmp_paths:
                Path(p).unlink(missing_ok=True)

        self._send(200, json.dumps({"answer": answer}).encode("utf-8"), "application/json")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("RoboDoctor running at http://127.0.0.1:8000  (Ctrl+C to stop)")
    server.serve_forever()
