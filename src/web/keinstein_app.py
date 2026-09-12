from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib
import json
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / 'data'
PAGE_DIR = Path(__file__).resolve().parent / 'pages'
DATA_DIR.mkdir(parents=True, exist_ok=True)

HOST = "127.0.0.1"
PORT = 8002
DATABASE = DATA_DIR / 'keinstein.db'
PAGE_ROUTES = {
	'/story': 'story.html',
	'/story.html': 'story.html',
	'/gallery': 'gallery.html',
	'/gallery.html': 'gallery.html',
	'/timeline': 'timeline.html',
	'/timeline.html': 'timeline.html',
	'/dreams': 'dreams.html',
	'/dreams.html': 'dreams.html',
	'/memories': 'memories.html',
	'/memories.html': 'memories.html',
	'/about': 'about.html',
	'/about.html': 'about.html',
}


def initialize_database():
	with sqlite3.connect(DATABASE) as connection:
		connection.execute('''CREATE TABLE IF NOT EXISTS accounts (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			partner TEXT NOT NULL,
			address TEXT,
			phone TEXT,
			mother TEXT,
			father TEXT,
			course TEXT,
			qualification TEXT,
			current_study TEXT,
			email TEXT NOT NULL UNIQUE,
			password_hash TEXT NOT NULL,
			created_at TEXT DEFAULT CURRENT_TIMESTAMP
		)''')


initialize_database()

PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KEINSTEIN | Kapil Loves Gayatri</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --night:#111a3c; --deep:#1b285a; --violet:#7055d9; --pink:#f579ac; --peach:#ffc78d; --ink:#25264d; --muted:#74749b; --card:#fffdf9; --line:#e7e5f2; }
* { box-sizing:border-box; }
html, body { min-height:100%; }
body { margin:0; color:var(--ink); background:#10183a; font-family:'Nunito',sans-serif; }
button, input { font:inherit; }
button { cursor:pointer; }
.app { min-height:100vh; position:relative; overflow:hidden; perspective:1400px; background:radial-gradient(ellipse at 72% 38%,#4a3d91 0%,#252b70 24%,transparent 57%),radial-gradient(ellipse at 12% 88%,#124b67 0%,#101b4d 36%,transparent 66%),linear-gradient(135deg,#101b4c,#17245f 48%,#351e62); }
.app:before { content:""; position:absolute; inset:0; opacity:.58; background-image:radial-gradient(#fff 1px,transparent 1px),radial-gradient(rgba(174,213,255,.9) 1px,transparent 1px),radial-gradient(rgba(255,200,130,.8) 1px,transparent 1px); background-size:37px 37px,83px 83px,127px 127px; background-position:0 0,17px 24px,54px 77px; animation:star-drift 24s linear infinite; }
.app:after { content:""; position:absolute; inset:-20%; opacity:.2; pointer-events:none; background:radial-gradient(ellipse at 70% 35%,transparent 0 17%,rgba(116,191,255,.6) 24%,transparent 43%),radial-gradient(ellipse at 20% 75%,rgba(239,107,190,.5),transparent 32%); filter:blur(35px); animation:nebula-drift 18s ease-in-out infinite alternate; }
.aurora { position:absolute; border-radius:50%; filter:blur(2px); opacity:.35; pointer-events:none; }
.aurora.one { width:420px; height:420px; left:-160px; top:-100px; background:#eb79bc; }
.aurora.two { width:380px; height:380px; right:-90px; bottom:-130px; background:#ffc88b; }
.front-solar { position:absolute; z-index:1; left:calc(50% - 100px); top:50%; width:630px; height:630px; transform:translateY(-50%); perspective:950px; transform-style:preserve-3d; pointer-events:none; opacity:1; transition:opacity .4s; filter:saturate(1.2); }
.front-solar.hidden { opacity:0; }
.sun { position:absolute; z-index:3; left:calc(50% - 55px); top:calc(50% - 55px); width:110px; height:110px; border-radius:50%; background:radial-gradient(circle at 35% 30%,#fffde0 0 8%,#ffe36e 25%,#ff9b35 61%,#e95c45 100%); box-shadow:0 0 35px #ffd36b,0 0 105px rgba(255,159,67,.82),0 0 170px rgba(255,102,102,.32); animation:sun-pulse 2.4s ease-in-out infinite,sun-turn 8s linear infinite; }
.sun:after { content:""; position:absolute; inset:11px; border-radius:50%; border:2px solid rgba(255,248,179,.42); border-left-color:transparent; border-right-color:rgba(255,232,117,.65); transform:rotate(28deg); }
.orbit { position:absolute; left:50%; top:50%; border:1px solid rgba(255,231,188,.55); border-radius:50%; transform:translate(-50%,-50%) rotateX(62deg) rotateZ(-13deg); transform-style:preserve-3d; box-shadow:0 0 14px rgba(157,194,255,.14),inset 0 0 10px rgba(255,220,160,.06); }
.orbit.one { width:190px; height:190px; }.orbit.two { width:320px; height:320px; }.orbit.three { width:470px; height:470px; }.orbit.four { width:620px; height:620px; }
.planet-track { position:absolute; inset:0; transform-style:preserve-3d; animation:solar-spin var(--orbit-time) linear infinite; }
.planet { position:absolute; left:50%; top:50%; border-radius:50%; transform:translate(-50%,-50%); transform-style:preserve-3d; animation:planet-turn var(--planet-time,2s) linear infinite; }
.planet.one { width:16px; height:16px; margin-left:95px; background:#c99b74; box-shadow:0 0 12px rgba(255,220,170,.9); }
.planet.two { width:28px; height:28px; margin-left:160px; background:radial-gradient(circle at 30% 28%,#ffe2a0,#dc8e4f 55%,#91495a); box-shadow:inset -7px -4px #9d4c5a,0 0 12px rgba(255,190,120,.6); }
.planet.three { width:34px; height:34px; margin-left:235px; background:radial-gradient(circle at 30% 25%,#9ee4df,#438fae 54%,#263f84); box-shadow:inset -9px -5px #284a80,0 0 14px rgba(92,218,255,.7); }
.planet.four { width:25px; height:25px; margin-left:310px; background:radial-gradient(circle at 30% 25%,#ffb486,#db665d 55%,#833c63); box-shadow:inset -6px -4px #9a445d,0 0 12px rgba(255,125,116,.65); }
.planet-ring { position:absolute; inset:-5px; border:2px solid rgba(255,221,149,.65); border-radius:50%; transform:rotate(-17deg) scaleX(1.6); }
.star.s1,.star.s2,.star.s3,.star.s4,.star.s5,.star.s6 { box-shadow:0 0 9px 2px rgba(255,255,255,.7); }
.light-string { position:absolute; z-index:1; top:84px; right:8%; display:flex; gap:19px; align-items:center; pointer-events:none; }
.light-string:before { content:""; position:absolute; left:-12px; right:-12px; top:4px; height:1px; background:rgba(255,255,255,.35); }
.bulb { position:relative; z-index:1; width:9px; height:9px; border-radius:50%; background:#7d7d94; box-shadow:0 0 0 transparent; animation:bulb-blink 2.8s ease-in-out infinite; }
.bulb:nth-child(2) { animation-delay:.45s; }.bulb:nth-child(3) { animation-delay:1.1s; }.bulb:nth-child(4) { animation-delay:1.7s; }.bulb:nth-child(5) { animation-delay:2.25s; }.bulb:nth-child(6) { animation-delay:.8s; }.bulb:nth-child(7) { animation-delay:1.45s; }
.bulb:nth-child(odd) { background:#ffd36d; animation-name:gold-blink; }.bulb:nth-child(even) { background:#74d9ff; }
@keyframes solar-spin { from { transform:rotate(0deg); } to { transform:rotate(360deg); } }
@keyframes planet-turn { from { filter:brightness(1); } 50% { filter:brightness(1.18); } to { filter:brightness(.92); } }
@keyframes sun-pulse { 50% { transform:scale(1.08); box-shadow:0 0 32px #ffc864,0 0 84px rgba(255,200,100,.65); } }
@keyframes sun-turn { to { background-position:100px 0; } }
@keyframes nebula-drift { from { transform:translate3d(-2%,1%,0) scale(1); } to { transform:translate3d(3%,-2%,0) scale(1.08); } }
@keyframes star-drift { from { background-position:0 0,17px 24px,54px 77px; } to { background-position:28px 18px,-18px 31px,82px 46px; } }
@keyframes bulb-blink { 0%,32%,100% { opacity:.25; box-shadow:0 0 0 transparent; } 16%,25% { opacity:1; box-shadow:0 0 7px 3px rgba(116,217,255,.9),0 0 20px 5px rgba(116,217,255,.35); } }
@keyframes gold-blink { 0%,42%,100% { opacity:.22; box-shadow:0 0 0 transparent; } 21%,33% { opacity:1; box-shadow:0 0 7px 3px rgba(255,211,109,.95),0 0 20px 5px rgba(255,211,109,.4); } }
@keyframes shoot { 0%,72% { opacity:0; transform:translate(0,0) rotate(-28deg) scale(.8); } 76% { opacity:1; } 86% { opacity:0; transform:translate(-190px,75px) rotate(-28deg) scale(1); } 100% { opacity:0; } }
@keyframes badge-glow { 0%,100% { box-shadow:0 0 22px rgba(255,179,100,.1); } 50% { box-shadow:0 0 30px rgba(255,179,100,.28); } }
@media (prefers-reduced-motion: reduce) { *, *:before, *:after { animation-duration:.001ms !important; animation-iteration-count:1 !important; scroll-behavior:auto !important; } }
.star { position:absolute; width:4px; height:4px; border-radius:50%; background:#fff; opacity:.8; animation:twinkle 2.8s ease-in-out infinite; }
.star.s1 { left:11%; top:20%; animation-delay:.4s; }.star.s2 { left:26%; top:9%; animation-delay:1.2s; }.star.s3 { left:70%; top:15%; animation-delay:.8s; }.star.s4 { left:88%; top:32%; animation-delay:1.9s; }.star.s5 { left:63%; top:76%; animation-delay:1.4s; }.star.s6 { left:8%; top:76%; animation-delay:2.1s; }
.shooting-star { position:absolute; z-index:1; width:4px; height:4px; border-radius:50%; background:#fff4cf; box-shadow:0 0 8px 2px #fff, -95px 25px 0 -1px rgba(255,220,157,.25); transform:rotate(-28deg); opacity:0; animation:shoot 7s linear infinite; }
.shooting-star.a { top:17%; left:54%; animation-delay:1.5s; }.shooting-star.b { top:36%; left:88%; animation-delay:4.3s; transform:rotate(-28deg) scale(.7); }.shooting-star.c { top:69%; left:42%; animation-delay:6s; transform:rotate(-28deg) scale(.55); }
.heart-badge { display:inline-flex; align-items:center; gap:9px; margin-top:25px; padding:10px 14px; border:1px solid rgba(255,211,119,.3); border-radius:12px; color:#ffe6b2; background:rgba(255,255,255,.07); box-shadow:0 0 22px rgba(255,179,100,.1); font-size:11px; font-weight:800; animation:badge-glow 3s ease-in-out infinite; }
.heart-badge strong { color:#ff83b0; font-size:18px; }
.asteroid-belt { position:absolute; left:50%; top:50%; width:390px; height:390px; border:0; border-radius:50%; transform:translate(-50%,-50%) rotateX(62deg) rotateZ(-13deg); opacity:.7; animation:belt-spin 42s linear infinite; }
.asteroid-belt:before { content:""; position:absolute; left:50%; top:50%; width:5px; height:5px; border-radius:50%; background:#c49a7c; box-shadow:45px -126px #e1b88c,95px -95px 0 1px #8d7d86,155px -20px #d0a172,136px 69px 0 1px #9f8790,63px 128px #e5b584,-35px 140px 0 1px #ac8d79,-125px 71px #d0a172,-158px -21px 0 1px #897d91,-112px -105px #e1b88c,-30px -143px 0 1px #a68a7c; }
.comet { position:absolute; z-index:1; width:8px; height:8px; border-radius:50%; background:#c9f4ff; box-shadow:0 0 11px 4px #a9eaff, -45px 15px 0 -2px rgba(143,223,255,.5), -75px 25px 0 -3px rgba(143,223,255,.2); opacity:0; animation:comet-fly 12s linear infinite; }
.comet.one { top:25%; left:74%; animation-delay:2s; }.comet.two { top:65%; left:80%; transform:scale(.6); animation-delay:7s; }
.galaxy { position:absolute; width:66px; height:25px; border-radius:50%; opacity:.5; background:radial-gradient(ellipse,#ffe7c0 0 8%,#d89cd9 18%,rgba(106,147,255,.3) 43%,transparent 70%); filter:blur(1px); animation:galaxy-turn 12s ease-in-out infinite alternate; }
.galaxy.one { top:19%; left:39%; transform:rotate(-24deg); }.galaxy.two { right:7%; bottom:24%; transform:rotate(32deg) scale(.7); animation-delay:4s; }
.constellation { position:absolute; z-index:0; width:170px; height:120px; opacity:.3; border-top:1px solid #abdfff; border-right:1px solid #abdfff; transform:rotate(-22deg); }
.constellation:before { content:"✦  ·  ✦     ·  ✦"; position:absolute; top:23px; left:15px; color:#d7efff; font-size:12px; letter-spacing:12px; }
.constellation.a { top:23%; left:10%; }.constellation.b { right:8%; top:58%; transform:rotate(25deg) scale(.7); opacity:.22; }
@keyframes belt-spin { to { transform:translate(-50%,-50%) rotateX(62deg) rotateZ(347deg); } }
@keyframes comet-fly { 0%,72% { opacity:0; transform:translate(0,0) rotate(-25deg); } 76% { opacity:1; } 91% { opacity:0; transform:translate(-240px,105px) rotate(-25deg); } 100% { opacity:0; } }
@keyframes galaxy-turn { from { filter:blur(1px); opacity:.25; } to { filter:blur(3px); opacity:.6; } }
.topbar { position:relative; z-index:2; max-width:1180px; margin:auto; padding:24px 6vw 18px; display:flex; justify-content:space-between; align-items:center; color:#fff; transform:translateZ(45px); }
.brand { display:flex; gap:11px; align-items:center; font-weight:900; letter-spacing:.08em; text-transform:uppercase; font-size:13px; }
.brand-mark { width:34px; height:34px; display:grid; place-items:center; color:var(--night); background:linear-gradient(135deg,var(--peach),var(--pink)); border-radius:12px 12px 12px 3px; transform:rotate(-8deg); box-shadow:0 12px 24px rgba(255,114,170,.35); }
.top-note { opacity:.86; font-size:12px; letter-spacing:.08em; padding:8px 12px; border:1px solid rgba(255,255,255,.2); border-radius:999px; background:rgba(255,255,255,.06); }
.project-label { display:inline-flex; align-items:center; gap:8px; margin-bottom:19px; padding:8px 11px; border:1px solid rgba(255,213,146,.35); border-radius:999px; color:#ffe0ac; background:rgba(255,255,255,.06); font-size:10px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }
.project-label b { width:7px; height:7px; border-radius:50%; background:#6df3d2; box-shadow:0 0 10px #6df3d2; }
.layout { position:relative; z-index:1; max-width:1180px; min-height:calc(100vh - 86px); margin:auto; padding:3vh 6vw 7vh; display:grid; grid-template-columns:minmax(320px,1fr) minmax(390px,470px); gap:8vw; align-items:center; transform-style:preserve-3d; }
.hero { color:#fff; animation:rise .8s ease both; transform:translateZ(80px) rotateY(3deg); transform-style:preserve-3d; }
.kicker { margin:0 0 18px; color:var(--peach); font-size:12px; font-weight:800; letter-spacing:.18em; text-transform:uppercase; }
h1 { max-width:620px; margin:0; font-family:'Space Grotesk',sans-serif; font-size:clamp(3.6rem,7vw,6.9rem); line-height:.88; letter-spacing:0; }
h1 span { color:var(--peach); }
.hero-copy { max-width:450px; margin:29px 0 0; color:#d8dcf4; font-size:16px; line-height:1.75; }
.love-title { max-width:800px; margin:0 0 28px; color:#ff83b0; text-shadow:1px 1px 0 #a62570,2px 2px 0 #7a225e,3px 3px 0 #531a55,0 0 24px rgba(255,89,169,.8),0 0 55px rgba(255,144,204,.38); font-family:'Space Grotesk',sans-serif; font-size:clamp(2.7rem,6vw,6.1rem); line-height:.9; letter-spacing:.02em; font-weight:900; transform:perspective(500px) rotateX(7deg); transform-origin:left center; }
.love-title span { color:#ffd477; }
.motivation { max-width:470px; margin:0 0 25px; color:#ffe0ba; font-size:15px; font-weight:700; line-height:1.7; }
.capability-grid { display:grid; grid-template-columns:repeat(3, minmax(100px, 1fr)); max-width:470px; margin:27px 0 25px; border-top:1px solid rgba(255,255,255,.2); border-bottom:1px solid rgba(255,255,255,.2); }
.capability { padding:13px 11px 13px 0; border-right:1px solid rgba(255,255,255,.16); }
.capability + .capability { padding-left:13px; }.capability:last-child { border-right:0; }
.capability strong { display:block; color:#fff3d2; font-family:'Space Grotesk',sans-serif; font-size:22px; }.capability span { display:block; margin-top:4px; color:#b9c4ea; font-size:9px; letter-spacing:.08em; text-transform:uppercase; }
.feature-row { display:flex; flex-wrap:wrap; gap:10px; margin-top:30px; }
.feature { display:flex; align-items:center; gap:8px; padding:9px 12px; color:#fff; border:1px solid rgba(255,255,255,.2); border-radius:20px; font-size:11px; font-weight:700; background:rgba(255,255,255,.08); }
.feature b { color:var(--peach); font-size:15px; }
.card-wrap { position:relative; }
.card { position:relative; z-index:2; padding:33px; border:1px solid rgba(255,255,255,.7); border-radius:28px; background:rgba(255,253,249,.98); box-shadow:0 28px 80px rgba(8,12,40,.3),0 18px 0 rgba(61,34,104,.28), inset 0 1px 0 rgba(255,255,255,.9); animation:card-in .9s .15s ease both; transform:rotateY(-5deg) rotateX(2deg) translateZ(55px); transform-style:preserve-3d; }
.card-top { display:flex; justify-content:space-between; align-items:start; margin-bottom:28px; }
.card h2 { margin:0 0 7px; font-family:'Space Grotesk',sans-serif; font-size:28px; }
.card-subtitle { margin:0; color:var(--muted); font-size:13px; }
.orb { width:47px; height:47px; display:grid; place-items:center; border-radius:17px 17px 17px 5px; color:#fff; background:linear-gradient(145deg,var(--violet),var(--pink)); font-size:23px; transform:rotate(8deg); box-shadow:0 12px 24px rgba(160,101,255,.36); }
.progress { display:flex; gap:5px; margin-bottom:25px; }
.progress span { height:4px; flex:1; border-radius:10px; background:#eceaf5; transition:background .3s; }
.progress span.active { background:linear-gradient(90deg,var(--violet),var(--pink)); }
.field { margin-bottom:17px; }
.profile-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:4px; }
.profile-row .field { min-width:0; }
.profile-heading { margin:18px 0 10px; color:var(--violet); font-size:10px; font-weight:900; letter-spacing:.12em; text-transform:uppercase; }
.field label { display:block; margin-bottom:8px; color:#4b4c70; font-size:12px; font-weight:800; }
.input-wrap { position:relative; }
.input-wrap input { width:100%; height:50px; padding:0 15px; border:1px solid var(--line); border-radius:13px; color:var(--ink); background:#fbfaff; outline:none; transition:border .2s,box-shadow .2s; }
.input-wrap input:focus { border-color:var(--violet); box-shadow:0 0 0 4px rgba(112,85,217,.12); }
.input-wrap input.invalid { border-color:#dc5874; }
.toggle { position:absolute; top:50%; right:12px; width:32px; height:32px; transform:translateY(-50%); border:0; border-radius:9px; color:var(--muted); background:transparent; }
.toggle:hover { background:#efedfa; }
.hint { min-height:16px; margin:6px 0 0; color:#dc5874; font-size:11px; }
.remember-line { display:flex; justify-content:space-between; align-items:center; margin:4px 0 22px; font-size:12px; }
.check { display:flex; align-items:center; gap:8px; color:var(--muted); }
.check input { accent-color:var(--violet); }
.link { border:0; padding:0; color:var(--violet); background:none; font-size:12px; font-weight:800; }
.link:hover { color:var(--pink); }
.primary { width:100%; min-height:52px; border:0; border-radius:14px; color:#fff; background:linear-gradient(100deg,var(--violet),#ab59c9,var(--pink)); box-shadow:0 10px 22px rgba(112,85,217,.25),inset 0 1px rgba(255,255,255,.35); font-size:13px; font-weight:900; letter-spacing:.05em; transition:transform .2s,box-shadow .2s, filter .2s; transform:translateZ(16px); }
.primary:hover { transform:translateY(-2px); box-shadow:0 16px 32px rgba(112,85,217,.34); filter:saturate(1.08); }
.primary:active { transform:translateY(0); }
.divider { display:flex; align-items:center; gap:10px; margin:22px 0; color:#b1b0c5; font-size:11px; }
.divider:before,.divider:after { content:""; height:1px; flex:1; background:var(--line); }
.helper { display:flex; gap:14px; align-items:end; position:absolute; z-index:3; width:200px; left:-155px; bottom:25px; animation:helper-in 1s .7s ease both; }
.bubble { position:relative; padding:13px 15px; border-radius:16px 16px 3px 16px; color:#493956; background:rgba(255,255,255,.96); box-shadow:0 12px 26px rgba(91,57,131,.18); font-size:11px; font-weight:700; line-height:1.45; border:1px solid rgba(146,118,227,.15); }
.bubble:after { content:""; position:absolute; right:-8px; bottom:3px; border-width:7px 0 0 9px; border-style:solid; border-color:transparent transparent transparent rgba(255,255,255,.96); }
.character { position:relative; width:70px; height:120px; flex:0 0 70px; }
.hair { position:absolute; z-index:2; top:3px; left:8px; width:54px; height:61px; border-radius:50% 50% 42% 42%; background:#30245e; }
.hair:after { content:""; position:absolute; left:20px; top:40px; width:27px; height:64px; border-radius:0 0 50% 50%; background:#30245e; transform:rotate(-13deg); }
.face { position:absolute; z-index:3; left:16px; top:22px; width:40px; height:49px; border-radius:43% 43% 48% 48%; background:#ffd0b0; }
.face:before,.face:after { content:""; position:absolute; top:26px; width:5px; height:7px; border-radius:50%; background:#30245e; }
.face:before { left:10px; }.face:after { right:10px; }
.face-smile { position:absolute; z-index:5; top:38px; left:18px; width:6px; height:4px; border-bottom:2px solid #b64f75; border-radius:50%; }
.ribbon { position:absolute; z-index:5; top:5px; right:0; width:22px; height:25px; border-radius:3px 15px 15px 3px; background:var(--pink); transform:rotate(18deg); }
.ribbon:after { content:""; position:absolute; left:-11px; top:8px; border-width:6px 12px 6px 0; border-style:solid; border-color:transparent var(--pink) transparent transparent; }
.body { position:absolute; z-index:1; left:8px; top:66px; width:58px; height:54px; border-radius:24px 24px 9px 9px; background:linear-gradient(135deg,var(--violet),#b160cd); }
.body:before { content:"✦"; position:absolute; left:25px; top:14px; color:#ffd29f; font-size:17px; }
.arm { position:absolute; z-index:4; top:76px; right:-5px; width:35px; height:13px; border-radius:12px; background:#ffd0b0; transform:rotate(-24deg); }
.stars-row { display:flex; gap:5px; margin-top:18px; color:var(--peach); font-size:15px; }
.modal { position:fixed; inset:0; z-index:10; display:none; place-items:center; padding:20px; background:rgba(10,15,43,.68); backdrop-filter:blur(8px); }
.modal.open { display:grid; }
.modal-box { width:min(420px,100%); padding:30px; border-radius:23px; text-align:center; background:var(--card); box-shadow:0 25px 70px rgba(0,0,0,.3); animation:pop .3s ease both; }
.modal-icon { font-size:45px; }
.modal-box h3 { margin:13px 0 8px; font-family:'Space Grotesk',sans-serif; font-size:24px; }
.modal-box p { margin:0 0 21px; color:var(--muted); font-size:13px; line-height:1.65; }
.secondary { padding:11px 20px; border:1px solid var(--line); border-radius:11px; color:var(--violet); background:#fff; font-size:12px; font-weight:900; }
.secondary:hover { background:#f5f2ff; }
.toast { position:fixed; z-index:20; right:22px; bottom:22px; display:none; max-width:280px; padding:14px 17px; border-radius:13px; color:#fff; background:#272a55; box-shadow:0 12px 30px rgba(0,0,0,.22); font-size:12px; font-weight:700; }
.toast.show { display:block; animation:toast-in .3s ease both; }
.story-slides { background:transparent; }
.slide-panel { position:relative; z-index:2; max-width:1160px; margin:40px auto 0; padding:34px; border:1px solid rgba(255,255,255,.2); border-radius:28px; background:rgba(16,23,51,.72); box-shadow:0 24px 80px rgba(0,0,0,.22); color:#fff; }
.world-panel { padding:46px 38px; }
.slide-badge { display:inline-flex; padding:8px 12px; border:1px solid rgba(255,212,146,.38); border-radius:999px; color:#ffe0ac; background:rgba(255,255,255,.06); letter-spacing:.14em; text-transform:uppercase; font-size:10px; font-weight:900; }
.world-panel h1 { margin:20px 0 10px; font-size:clamp(2.6rem,6vw,5.3rem); line-height:.9; }
.world-panel p { max-width:700px; margin:0 0 24px; color:#dfe4fd; font-size:18px; line-height:1.7; }
.world-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; margin-top:24px; }
.world-tile { padding:20px 16px; border:1px solid rgba(255,255,255,.15); border-radius:18px; background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.04)); display:flex; flex-direction:column; gap:10px; min-height:180px; }
.world-tile span { font-size:28px; color:#ffc98d; }
.world-tile strong { font-size:18px; }
.world-tile small { color:#dfe3ff; line-height:1.6; }
.story-actions { display:flex; align-items:center; gap:12px; margin-top:22px; flex-wrap:wrap; }
.story-actions .primary, .story-actions .ghost { width:auto; min-width:180px; }
.ghost.alt { background:rgba(255,255,255,.08); color:#fff; border:1px solid rgba(255,255,255,.25); }
.story-panel { background:rgba(10,14,33,.82); }
.story-slide-header { display:flex; justify-content:space-between; align-items:end; gap:20px; margin-bottom:18px; }
.story-slide-header h2 { margin:6px 0 0; font-family:'Space Grotesk',sans-serif; font-size:clamp(2.1rem,4vw,3.2rem); }
.kicker.small { margin:0; font-size:10px; letter-spacing:.2em; }
.story-quote { padding:18px 20px; border-left:4px solid #ff9dcb; border-radius:12px; background:rgba(255,255,255,.06); color:#f2d9ff; font-size:1.08rem; line-height:1.7; }
.feature-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin-top:22px; }
.feature-card { position:relative; overflow:hidden; padding:18px 14px; border:1px solid rgba(255,255,255,.14); border-radius:16px; background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.03)); min-height:150px; cursor:pointer; transition:transform .24s ease, border-color .24s ease, box-shadow .24s ease, background .24s ease; transform-style:preserve-3d; box-shadow:0 16px 28px rgba(20,18,44,.18), inset 0 1px rgba(255,255,255,.08); }
.feature-card::before { content:""; position:absolute; inset:-30% -20% auto auto; width:120px; height:120px; border-radius:50%; background:radial-gradient(circle, rgba(255,211,129,.58), rgba(255,211,129,0) 68%); opacity:0; transition:opacity .24s ease, transform .24s ease; transform:translate3d(0,0,0); }
.feature-card::after { content:""; position:absolute; inset:auto auto -30% -15%; width:120px; height:120px; border-radius:50%; background:radial-gradient(circle, rgba(198,150,255,.42), rgba(198,150,255,0) 68%); opacity:0; transition:opacity .24s ease, transform .24s ease; }
.feature-card:hover { transform:translateY(-7px) rotateX(7deg) rotateY(-4deg); border-color:rgba(255,224,153,.45); background:linear-gradient(180deg,rgba(255,255,255,.13),rgba(255,255,255,.05)); box-shadow:0 24px 40px rgba(136,113,255,.22),0 0 0 1px rgba(255,206,120,.25),inset 0 1px rgba(255,255,255,.12); }
.feature-card:hover::before, .feature-card:hover::after { opacity:1; }
.feature-card:hover::before { transform:translate3d(-8px,-10px,20px); }
.feature-card:hover::after { transform:translate3d(10px,8px,18px); }
.feature-card span { position:relative; z-index:1; display:inline-flex; width:38px; height:38px; align-items:center; justify-content:center; border-radius:12px; background:linear-gradient(135deg,#ffc78d,#f59ac1); color:#1d1736; font-weight:900; box-shadow:0 10px 18px rgba(247,145,190,.25); }
.feature-card strong { position:relative; z-index:1; display:block; margin-top:12px; font-size:16px; }
.feature-card small { position:relative; z-index:1; display:block; margin-top:8px; color:#d9dfff; line-height:1.5; }
.detail-panel { position:relative; overflow:hidden; padding:38px 34px 30px; border:1px solid rgba(255,255,255,.18); border-radius:30px; background:linear-gradient(145deg,rgba(23,32,62,.88),rgba(12,18,40,.75)); box-shadow:0 32px 90px rgba(12,10,28,.45), inset 0 1px rgba(255,255,255,.12); backdrop-filter:blur(16px); transform:perspective(1200px) rotateX(0deg) scale(1); }
.detail-panel::before { content:""; position:absolute; inset:-18% 12% auto auto; width:240px; height:240px; border-radius:50%; background:radial-gradient(circle, rgba(255,205,123,.38), rgba(255,205,123,0)); filter:blur(12px); animation:float-star 7s ease-in-out infinite; }
.detail-panel::after { content:"✦ ✦ ✦"; position:absolute; top:18px; right:28px; letter-spacing:.4em; color:rgba(255,214,133,.6); font-size:12px; opacity:.8; animation:float-star 8s ease-in-out infinite reverse; }
.detail-panel .story-slide-header { margin-bottom:26px; }
.detail-panel .story-quote { padding:20px 22px; font-size:1.12rem; background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(255,255,255,.03)); border-left:4px solid #ffb9db; box-shadow:inset 0 1px rgba(255,255,255,.05); }
.detail-visual { position:relative; margin-top:24px; padding:24px; border-radius:18px; background:linear-gradient(135deg,rgba(255,201,141,.12),rgba(159,136,255,.12)); border:1px solid rgba(255,255,255,.12); overflow:hidden; }
.detail-visual::before { content:""; position:absolute; inset:0; background:radial-gradient(circle at 30% 20%, rgba(255,255,255,.18), transparent 28%), radial-gradient(circle at 80% 30%, rgba(144,183,255,.18), transparent 26%), radial-gradient(circle at 60% 80%, rgba(255,136,186,.14), transparent 24%); }
.detail-visual > * { position:relative; z-index:1; }
.detail-badge { display:inline-flex; padding:8px 12px; border-radius:999px; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.12); color:#ffe0ac; font-size:11px; font-weight:900; letter-spacing:.13em; text-transform:uppercase; }
.detail-list-mini { list-style:none; padding:0; margin:18px 0 0; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }
.detail-list-mini li { padding:12px 14px; border-radius:12px; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.1); color:#e9ebff; line-height:1.5; }
.footer { position:absolute; z-index:1; left:6vw; right:6vw; bottom:22px; display:flex; justify-content:space-between; color:rgba(255,255,255,.7); font-size:10px; letter-spacing:.06em; }
.instagram { display:flex; align-items:center; gap:8px; color:#ffd2e1; font-weight:800; }
.instagram-icon { position:relative; display:inline-block; width:17px; height:17px; border:2px solid #ffd2e1; border-radius:5px; }
.instagram-icon:before { content:""; position:absolute; left:3px; top:3px; width:7px; height:7px; border:2px solid #ffd2e1; border-radius:50%; }
.instagram-icon:after { content:""; position:absolute; right:2px; top:2px; width:3px; height:3px; border-radius:50%; background:#ffd2e1; }
.screen { display:none; position:relative; z-index:1; min-height:calc(100vh - 86px); max-width:1180px; margin:auto; padding:4vh 6vw 7vh; transform-style:preserve-3d; }
.screen.visible { display:block; animation:rise .55s ease both; }
#featureDetailScreen.visible .detail-panel { animation:cinematic-enter .75s cubic-bezier(.22,1,.36,1) both; }
.dashboard-head { display:flex; justify-content:space-between; align-items:end; color:#fff; margin-bottom:30px; }
.dashboard-head h1 { font-size:clamp(2.7rem,5vw,5.3rem); }
.dashboard-head p { color:#d8dcf4; font-size:14px; }
.ghost { border:1px solid rgba(255,255,255,.35); border-radius:12px; padding:11px 15px; color:#fff; background:rgba(255,255,255,.1); font-size:12px; font-weight:800; }
.ghost:hover { background:rgba(255,255,255,.2); }
.dashboard-grid { display:grid; grid-template-columns:1.3fr .7fr; gap:20px; }
.welcome-panel,.character-panel,.game-panel { border:1px solid rgba(255,255,255,.25); border-radius:22px; padding:27px; background:rgba(255,255,255,.12); backdrop-filter:blur(8px); color:#fff; transform:rotateY(-3deg) translateZ(32px); box-shadow:0 24px 45px rgba(0,0,0,.2),inset 0 1px rgba(255,255,255,.18); }
.welcome-panel { min-height:270px; display:flex; flex-direction:column; justify-content:space-between; }
.welcome-panel h2 { margin:0; font-family:'Space Grotesk',sans-serif; font-size:34px; }
.welcome-panel p { max-width:510px; color:#d8dcf4; line-height:1.7; }
.dashboard-button { width:auto; align-self:flex-start; padding:14px 20px; }
.character-panel { display:flex; align-items:center; justify-content:center; min-height:270px; }
.big-character { transform:scale(1.55); margin-top:28px; }
.buddy-pair { display:flex; align-items:end; gap:28px; }
.buddy-pair .character { transform:scale(1.35); }
.robot .hair { background:#248ec2; border-radius:50%; }
.robot .hair:after { display:none; }
.robot .face { background:#dff7ff; border:3px solid #248ec2; }
.robot .face:before,.robot .face:after { background:#248ec2; }
.robot .ribbon { background:#f7c96b; }
.robot .ribbon:after { border-right-color:#f7c96b; }
.robot .body { background:linear-gradient(135deg,#248ec2,#72d8e9); }
.robot .body:before { content:"●"; color:#fff; }
.robot .arm { background:#dff7ff; }
.stat-row { display:flex; gap:12px; margin-top:18px; }
.stat { padding:10px 13px; border-radius:12px; color:#ffe0ba; background:rgba(0,0,0,.14); font-size:11px; }
.stat strong { display:block; color:#fff; font-size:19px; }
.dashboard-tools { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:20px; }
.tool-card { padding:17px; border:1px solid rgba(255,255,255,.22); border-radius:16px; color:#fff; background:rgba(255,255,255,.11); box-shadow:0 12px 22px rgba(0,0,0,.12); }
.tool-card h3 { margin:0 0 8px; font-family:'Space Grotesk',sans-serif; font-size:16px; }.tool-card p { min-height:34px; margin:0 0 12px; color:#d8dcf4; font-size:11px; line-height:1.5; }
.tool-card button { padding:9px 11px; border:0; border-radius:9px; color:var(--night); background:var(--peach); font-size:10px; font-weight:900; }
.tool-card button:hover { background:#fff; }
.tool-panel { display:none; margin-top:16px; padding:20px; border-radius:18px; color:var(--ink); background:var(--card); box-shadow:0 18px 36px rgba(0,0,0,.18); }
.tool-panel.open { display:block; animation:pop .3s ease both; }.tool-panel h2 { margin:0 0 12px; font-family:'Space Grotesk',sans-serif; font-size:23px; }
.detail-list { display:grid; grid-template-columns:repeat(3,1fr); gap:9px; margin:0; }.detail-list div { padding:10px; border-radius:10px; background:#f3f1fb; }.detail-list dt { color:var(--muted); font-size:9px; text-transform:uppercase; }.detail-list dd { margin:4px 0 0; font-size:12px; font-weight:800; }
.mini-form { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }.mini-form input,.mini-form textarea { width:100%; padding:10px; border:1px solid var(--line); border-radius:9px; color:var(--ink); background:#fbfaff; }.mini-form textarea { grid-column:1/-1; min-height:70px; resize:vertical; }.mini-form button { justify-self:start; padding:10px 14px; border:0; border-radius:9px; color:#fff; background:var(--violet); font-size:11px; font-weight:900; }
.memory-list { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }.memory { padding:13px; border-left:3px solid var(--pink); background:#fff4f5; }.memory strong { display:block; font-size:12px; }.memory span { display:block; margin-top:5px; color:var(--muted); font-size:11px; }
.countdown { display:flex; gap:10px; margin:12px 0; }.count-box { min-width:62px; padding:11px; border-radius:10px; text-align:center; color:#fff; background:var(--violet); }.count-box strong { display:block; font-size:22px; }.count-box span { font-size:9px; text-transform:uppercase; }
.quote { padding:18px; border-left:4px solid var(--pink); color:#634d52; background:#fff4f5; font-family:'Space Grotesk',sans-serif; font-size:18px; line-height:1.5; }
.chat-log { max-height:145px; overflow:auto; padding:11px; border-radius:10px; background:#f5f3fb; font-size:12px; line-height:1.5; }.chat-line { margin:7px 0; }.chat-line b { color:var(--violet); }.chat-form { display:flex; gap:8px; margin-top:10px; }.chat-form input { flex:1; padding:10px; border:1px solid var(--line); border-radius:9px; }.chat-form button { padding:9px 12px; border:0; border-radius:9px; color:#fff; background:var(--violet); font-weight:900; }
.setting-row { display:flex; flex-wrap:wrap; gap:12px; align-items:center; }.setting-row label { color:var(--muted); font-size:12px; }.setting-row select { padding:9px; border:1px solid var(--line); border-radius:8px; }.theme-dark { --card:#20254f; --ink:#fff; --muted:#c1c4e5; --line:#444979; }.theme-dark .tool-panel { background:#20254f; }.theme-dark .detail-list div { background:#303660; }
.admin-table { width:100%; border-collapse:collapse; font-size:11px; }.admin-table th,.admin-table td { padding:8px; border-bottom:1px solid var(--line); text-align:left; }.admin-table th { color:var(--muted); text-transform:uppercase; }
.arcade-head { display:flex; justify-content:space-between; align-items:center; color:#fff; margin-bottom:22px; }
.arcade-head h1 { font-size:clamp(2.6rem,5vw,5rem); }
.difficulty { display:flex; align-items:center; gap:10px; color:#fff; font-size:12px; font-weight:800; }
.difficulty select { padding:11px 13px; border:1px solid rgba(255,255,255,.35); border-radius:10px; color:#fff; background:rgba(255,255,255,.12); outline:none; }
.difficulty option { color:var(--ink); }
.game-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:15px; }
.game-card { min-height:205px; padding:22px; border:1px solid rgba(255,255,255,.25); border-radius:19px; color:#fff; background:rgba(255,255,255,.12); transform:rotateX(3deg) translateZ(30px); box-shadow:0 18px 30px rgba(0,0,0,.18),inset 0 1px rgba(255,255,255,.18); transition:transform .2s,background .2s; }
.game-card:hover { transform:translateY(-5px); background:rgba(255,255,255,.2); }
.game-icon { font-size:39px; }
.game-card h2 { margin:14px 0 7px; font-family:'Space Grotesk',sans-serif; font-size:22px; }
.game-card p { margin:0 0 16px; color:#d8dcf4; font-size:12px; line-height:1.5; }
.game-launch { padding:10px 13px; border:0; border-radius:10px; color:var(--night); background:var(--peach); font-size:11px; font-weight:900; }
.game-launch:hover { background:#fff; }
.game-area { display:none; margin-top:18px; padding:25px; border-radius:18px; color:var(--ink); background:#fffdf9; }
.game-area.open { display:block; animation:pop .3s ease both; }
.game-area h2 { margin:0 0 8px; font-family:'Space Grotesk',sans-serif; }
.game-area p { color:var(--muted); font-size:13px; }
.game-canvas { position:relative; height:260px; overflow:hidden; border-radius:12px; background:linear-gradient(#e5a56f 0 25%,#b97853 25% 27%,#6f4c43 27% 100%); }
.jungle { position:absolute; inset:0; background:linear-gradient(90deg,rgba(16,75,67,.7),transparent 18% 82%,rgba(16,75,67,.7)),repeating-linear-gradient(80deg,transparent 0 28px,rgba(38,111,69,.5) 29px 34px); }
.temple { position:absolute; top:15px; left:50%; width:150px; height:73px; transform:translateX(-50%); border:8px solid #d8b06c; border-bottom:0; background:#754c47; clip-path:polygon(15% 0,85% 0,100% 100%,0 100%); opacity:.9; }
.temple:after { content:""; position:absolute; left:55px; bottom:0; width:30px; height:52px; background:#261d31; }
.runner-road { position:absolute; left:19%; right:19%; top:0; bottom:0; transform:perspective(320px) rotateX(8deg); transform-origin:bottom; background:linear-gradient(90deg,#9c6b58,#c89769 48%,#9c6b58); border-left:9px solid #dfbc7c; border-right:9px solid #dfbc7c; }
.runner-road:before,.runner-road:after { content:""; position:absolute; top:-20px; bottom:-20px; width:5px; background:repeating-linear-gradient(#f4dca4 0 24px,transparent 24px 52px); animation:road .65s linear infinite; }
.runner-road:before { left:33%; }.runner-road:after { right:33%; }
.runner { position:absolute; z-index:4; bottom:29px; left:calc(50% - 17px); width:34px; height:57px; border-radius:18px 18px 8px 8px; background:#dc496b; transition:left .18s; }
.runner:before { content:""; position:absolute; left:6px; top:-18px; width:22px; height:22px; border-radius:50%; background:#ffd0b0; box-shadow:0 -4px #292045; }
.runner:after { content:""; position:absolute; left:8px; top:8px; width:18px; height:22px; background:#4f3c98; border-radius:7px; }
.obstacle { position:absolute; z-index:5; bottom:35px; width:38px; height:43px; border-radius:6px; background:#5b3d35; box-shadow:inset 0 0 0 5px #8b5c47; animation:obstacle-move var(--game-speed,2.8s) linear infinite; }
.obstacle:before { content:""; position:absolute; left:7px; right:7px; top:8px; height:5px; background:#d8b06c; box-shadow:0 14px #d8b06c; }
.obstacle.lane-left { left:29%; }.obstacle.lane-center { left:calc(50% - 19px); animation-delay:-1.2s; }.obstacle.lane-right { right:29%; animation-delay:-2.1s; }
.game-canvas.easy { --game-speed:4.5s; }.game-canvas.medium { --game-speed:2.8s; }.game-canvas.hard { --game-speed:1.45s; }
.road { position:absolute; left:25%; right:25%; top:0; bottom:0; border-left:4px solid #f7cf87; border-right:4px solid #f7cf87; background:repeating-linear-gradient(0deg,#303b77 0 28px,#fff 28px 34px,#303b77 34px 62px); animation:road .65s linear infinite; }
.vehicle { position:absolute; bottom:16px; left:calc(50% - 18px); width:36px; height:57px; border-radius:12px 12px 6px 6px; background:var(--pink); box-shadow:inset 0 -15px rgba(112,85,217,.4); }
.vehicle:before { content:""; position:absolute; left:7px; top:9px; width:22px; height:17px; border-radius:5px; background:#bfe9f3; }
.bike { width:15px; height:52px; left:calc(50% - 7px); border-radius:9px; background:var(--peach); }
.bike:before { left:2px; width:11px; height:12px; }
.target-zone { position:absolute; inset:0; display:grid; place-items:center; color:#fff; font-size:12px; font-weight:800; pointer-events:none; }
.tap-button { margin-top:12px; padding:11px 16px; border:0; border-radius:10px; color:#fff; background:var(--violet); font-size:11px; font-weight:900; }
.tap-button:hover { background:var(--pink); }
.score { float:right; color:var(--violet); font-weight:900; }
.game-hud { display:flex; gap:10px; margin-bottom:14px; }.hud-chip { padding:8px 10px; border-radius:8px; color:var(--violet); background:#f1effc; font-size:11px; font-weight:900; }
.leaderboard { margin-top:14px; padding:12px; border-radius:10px; background:#f6f4fc; color:var(--muted); font-size:11px; }.leaderboard strong { color:var(--ink); }
.memory-board { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; max-width:360px; }.memory-tile { aspect-ratio:1; border:0; border-radius:9px; color:transparent; background:var(--violet); font-size:22px; }.memory-tile.flipped { color:var(--ink); background:#ffd58e; }
.memory-board { display:none; margin-bottom:12px; }
@keyframes road { to { background-position:0 62px; } }
@keyframes obstacle-move { from { transform:translateY(-320px) scale(.5); } to { transform:translateY(90px) scale(1.35); } }
@keyframes twinkle { 0%,100% { opacity:.2; transform:scale(.7); } 50% { opacity:1; transform:scale(1.4); } }
@keyframes rise { from { opacity:0; transform:translateY(25px); } to { opacity:1; transform:none; } }
@keyframes card-in { from { opacity:0; transform:translateY(35px) rotate(2deg); } to { opacity:1; transform:none; } }
@keyframes helper-in { from { opacity:0; transform:translateX(-20px); } to { opacity:1; transform:none; } }
@keyframes pop { from { opacity:0; transform:scale(.9); } to { opacity:1; transform:scale(1); } }
@keyframes toast-in { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:none; } }
@keyframes bike-bounce { 0%,100% { transform:translateY(0) rotate(-2deg); } 50% { transform:translateY(-22px) rotate(3deg); } }
@keyframes target-pulse { from { box-shadow:0 0 0 0 rgba(245,121,172,.4); } to { box-shadow:0 0 0 12px rgba(245,121,172,0); } }
@keyframes float-star { 0%,100% { transform:translate3d(0,0,0) scale(1); opacity:.3; } 50% { transform:translate3d(18px,-14px,0) scale(1.5); opacity:1; } }
@keyframes cinematic-enter { 0% { opacity:0; transform:perspective(1200px) rotateX(10deg) translateY(28px) scale(.96); filter:blur(8px); } 65% { opacity:1; transform:perspective(1200px) rotateX(0deg) translateY(0) scale(1.02); filter:blur(0); } 100% { opacity:1; transform:perspective(1200px) rotateX(0deg) translateY(0) scale(1); filter:blur(0); } }
@media (max-width:840px) { .layout { grid-template-columns:1fr; max-width:570px; padding-top:7vh; padding-bottom:80px; gap:75px; } .hero { text-align:center; } .hero-copy { margin-left:auto; margin-right:auto; } .feature-row { justify-content:center; } .card-wrap { margin-left:70px; } .footer { display:none; } }
@media (max-width:560px) { .topbar { padding:20px 22px; } .top-note { display:none; } .layout { padding:42px 22px 70px; } h1 { font-size:clamp(3.5rem,16vw,5.8rem); } .hero-copy { font-size:14px; } .card { padding:24px 20px; border-radius:21px; transform:none; } .hero { transform:none; } .card-wrap { margin-left:0; } .helper { left:auto; right:-8px; bottom:-83px; width:200px; transform:scale(.88); transform-origin:right top; } .front-solar { left:calc(50% - 150px); top:37%; width:430px; height:430px; opacity:.42; } .orbit.one { width:125px; height:125px; }.orbit.two { width:210px; height:210px; }.orbit.three { width:310px; height:310px; }.orbit.four { width:410px; height:410px; } .profile-row { grid-template-columns:1fr; gap:0; } }
@media (max-width:840px) { .dashboard-grid,.game-grid { grid-template-columns:1fr; } .dashboard-head,.arcade-head { align-items:start; gap:15px; flex-direction:column; } .screen { padding:35px 22px 80px; } }
</style>
</head>
<body>
<div class="app">
<div class="aurora one"></div><div class="aurora two"></div>
<div class="front-solar" aria-label="Three-dimensional rotating solar system background"><div class="sun"></div><div class="orbit one"><div class="planet-track" style="--orbit-time:5s"><div class="planet one"></div></div></div><div class="orbit two"><div class="planet-track" style="--orbit-time:9s"><div class="planet two"></div></div></div><div class="orbit three"><div class="planet-track" style="--orbit-time:15s"><div class="planet three"></div></div></div><div class="orbit four"><div class="planet-track" style="--orbit-time:23s"><div class="planet four"><span class="planet-ring"></span></div></div></div></div>
<div class="light-string" aria-label="Blinking space lights"><span class="bulb"></span><span class="bulb"></span><span class="bulb"></span><span class="bulb"></span><span class="bulb"></span><span class="bulb"></span><span class="bulb"></span></div>
<i class="star s1"></i><i class="star s2"></i><i class="star s3"></i><i class="star s4"></i><i class="star s5"></i><i class="star s6"></i>
<i class="shooting-star a"></i><i class="shooting-star b"></i><i class="shooting-star c"></i>
<div class="asteroid-belt" aria-hidden="true"></div><i class="comet one"></i><i class="comet two"></i><div class="galaxy one"></div><div class="galaxy two"></div><div class="constellation a"></div><div class="constellation b"></div>
<header class="topbar"><div class="brand"><span class="brand-mark">✦</span> KEINSTEIN</div><div class="top-note">A tiny universe made for you</div></header>
<main class="layout">
<section class="hero">
<div class="project-label"><b></b> M.Tech interactive experience</div>
<p class="kicker">A love story worth remembering</p>
<div class="love-title">KAPIL LOVES GAYATRI</div>
<h1>A life partner<br><span>should feel like home.</span></h1>
<p class="motivation">A beautiful partnership is built in the quiet details: a hand held when words are difficult, a smile shared across a crowded room, and the courage to grow together while still making space for each other’s dreams.</p>
<p class="hero-copy">May your love feel gentle on difficult days, joyful in the smallest moments, and strong enough to turn every new morning into a promise worth keeping.</p>
<div class="capability-grid"><div class="capability"><strong>3D</strong><span>Immersive space</span></div><div class="capability"><strong>∞</strong><span>Shared moments</span></div><div class="capability"><strong>24/7</strong><span>Always connected</span></div></div>
<div class="heart-badge"><strong>♥</strong> A little universe made for two hearts</div>
<div class="feature-row"><span class="feature"><b>✦</b> Personal space</span><span class="feature"><b>♡</b> Made with care</span><span class="feature"><b>☾</b> Always yours</span></div>
</section>
<section class="card-wrap">
<div class="helper"><div class="bubble" id="helperText">Hi love! I’ve got a little magic for you.</div><div class="character"><div class="hair"></div><div class="ribbon"></div><div class="face"><span class="face-smile"></span></div><div class="body"></div><div class="arm"></div></div></div>
<div class="card">
<div class="card-top"><div><h2>Hello, love</h2><p class="card-subtitle" id="subtitle">Let’s begin our little universe.</p></div><div class="orb">✦</div></div>
<div class="progress"><span class="active"></span><span></span><span></span></div>
<form id="loginForm" novalidate>
<div class="field"><label for="name">Your name</label><div class="input-wrap"><input id="name" name="name" placeholder="What should we call you?" maxlength="30" autocomplete="name"><button class="toggle" type="button" tabindex="-1">✎</button></div><p class="hint" id="nameHint"></p></div>
<div class="field"><label for="partner">Partner or best friend</label><div class="input-wrap"><input id="partner" name="partner" placeholder="Someone special" maxlength="30"><button class="toggle" type="button" tabindex="-1">♡</button></div><p class="hint" id="partnerHint"></p></div>
<div class="profile-heading">Education</div>
<div class="profile-row"><div class="field"><label for="course">Course you are studying</label><div class="input-wrap"><input id="course" name="course" placeholder="Your current course" maxlength="60"></div><p class="hint"></p></div><div class="field"><label for="qualification">Highest qualification</label><div class="input-wrap"><input id="qualification" name="qualification" placeholder="e.g. 12th, diploma, degree" maxlength="60"></div><p class="hint"></p></div></div>
<div class="field"><label for="currentStudy">What are you studying now?</label><div class="input-wrap"><input id="currentStudy" name="currentStudy" placeholder="Your current studies or subject" maxlength="80"></div><p class="hint"></p></div>
<div class="field"><label for="email">Email address</label><div class="input-wrap"><input id="email" name="email" type="email" placeholder="you@example.com" autocomplete="email"><button class="toggle" type="button" tabindex="-1">@</button></div><p class="hint" id="emailHint"></p></div>
<div class="field"><label for="password">Create a secret password</label><div class="input-wrap"><input id="password" name="password" type="password" placeholder="At least 6 characters" autocomplete="new-password"><button class="toggle" id="passwordToggle" type="button" tabindex="-1">◉</button></div><p class="hint" id="passwordHint"></p></div>
<div class="remember-line"><label class="check"><input type="checkbox" id="remember"> Remember me</label><button type="button" class="link" id="forgot">Need a hint?</button></div>
<button class="primary" type="submit" id="submit">ENTER THE WORLD OF KAPIL &nbsp; →</button>
</form>
<div class="stars-row">✦ ✦ ✦</div>
</div>
</section>
</main>
<section class="screen story-slides" id="kapilWorldScreen">
<div class="slide-panel world-panel">
<div class="slide-badge">WELCOME TO</div>
<h1>THE WORLD OF KAPIL</h1>
<p>Every little moment with you feels like a new chapter written in stardust, laughter, and love.</p>
<div class="world-grid">
<div class="world-tile"><span>♡</span><strong>Our bond</strong><small>Trust, warmth, and calm togetherness</small></div>
<div class="world-tile"><span>✦</span><strong>Shared dreams</strong><small>Faraway places, simple joys, forever plans</small></div>
<div class="world-tile"><span>☾</span><strong>Gentle memories</strong><small>The moments we keep replaying in our hearts</small></div>
<div class="world-tile"><span>☀</span><strong>Future</strong><small>Built with patience, laughter, and care</small></div>
</div>
<div class="story-actions">
<button class="primary" id="showLoveStoryBtn" type="button">ENTER OUR LOVE STORY →</button>
<button class="ghost alt" id="backToFormBtn" type="button">← BACK</button>
</div>
</div>
</section>
<section class="screen story-slides" id="loveStoryScreen">
<div class="slide-panel story-panel">
<div class="story-slide-header">
<div><p class="kicker small">OUR STORY</p><h2>Kapil &amp; Gayatri</h2></div>
<div class="story-actions compact"><button class="ghost alt" id="backToWorldBtn" type="button">← WORLD</button></div>
</div>
<div class="story-quote">“You are the calm in my chaos, the smile in my silence, and the home I never knew I was missing.”</div>
<div class="feature-grid">
<div class="feature-card" data-feature="our-romance"><span>❤</span><strong>Our romance</strong><small>Warm hugs, deep understanding, and endless comfort</small></div>
<div class="feature-card" data-feature="love-note"><span>✦</span><strong>Love note</strong><small>Words written from the heart when we miss each other</small></div>
<div class="feature-card" data-feature="dream-visits"><span>☁</span><strong>Dream visits</strong><small>Shared wishes, secret plans, and future adventures</small></div>
<div class="feature-card" data-feature="morning-glow"><span>☀</span><strong>Morning glow</strong><small>Sunrise conversations that make the day feel lighter</small></div>
<div class="feature-card" data-feature="travel-plans"><span>✈</span><strong>Travel plans</strong><small>Road trips, café dates, and city walks together</small></div>
<div class="feature-card" data-feature="little-rituals"><span>❀</span><strong>Little rituals</strong><small>Tea breaks, silly jokes, and quiet comfort</small></div>
<div class="feature-card" data-feature="shared-laughter"><span>♥</span><strong>Shared laughter</strong><small>Joy that arrives in the simplest everyday moments</small></div>
<div class="feature-card" data-feature="forever-promise"><span>✧</span><strong>Forever promise</strong><small>Choosing each other again and again</small></div>
<div class="feature-card" data-feature="timeline"><span>★</span><strong>Timeline</strong><small>Every chapter, every smile, every step forward</small></div>
<div class="feature-card" data-feature="late-night-talks"><span>☾</span><strong>Late-night talks</strong><small>Heartfelt conversations under the moonlight</small></div>
<div class="feature-card" data-feature="gallery"><span>✺</span><strong>Gallery</strong><small>Photos, joy, and the story of us in frames</small></div>
<div class="feature-card" data-feature="growth"><span>△</span><strong>Growth</strong><small>Becoming softer, kinder, and more whole together</small></div>
<div class="feature-card" data-feature="support"><span>♡</span><strong>Support</strong><small>Standing by each other through every storm and calm</small></div>
<div class="feature-card" data-feature="inside-jokes"><span>✦</span><strong>Inside jokes</strong><small>The moments that feel like a secret language</small></div>
<div class="feature-card" data-feature="daily-checkins"><span>☼</span><strong>Daily check-ins</strong><small>Even small messages become beautiful memories</small></div>
<div class="feature-card" data-feature="spark"><span>⚡</span><strong>Spark</strong><small>The excitement that still appears when we meet</small></div>
<div class="feature-card" data-feature="endless-love"><span>∞</span><strong>Endless love</strong><small>A future that keeps growing brighter</small></div>
<div class="feature-card" data-feature="true-beauty"><span>✪</span><strong>True beauty</strong><small>Being loved in all your quiet, real, honest ways</small></div>
<div class="feature-card" data-feature="cafe-dates"><span>☕</span><strong>Café dates</strong><small>Simple plans that turn into unforgettable moments</small></div>
<div class="feature-card" data-feature="future-home"><span>❋</span><strong>Future home</strong><small>A life full of warmth, laughter, and peace</small></div>
<div class="feature-card" data-feature="playlist"><span>𝄞</span><strong>Playlist</strong><small>Our songs and the feelings they carry with them</small></div>
<div class="feature-card" data-feature="plans"><span>▣</span><strong>Plans</strong><small>Dreams we talk about with hope and excitement</small></div>
<div class="feature-card" data-feature="care"><span>✿</span><strong>Care</strong><small>Choosing tenderness in every ordinary moment</small></div>
<div class="feature-card" data-feature="forever"><span>❁</span><strong>Forever</strong><small>A story still unfolding, and always beautifully</small></div>
<div class="feature-card" data-feature="stargazing"><span>✧</span><strong>Stargazing</strong><small>Quiet nights, wishes, and memories written in the sky</small></div>
<div class="feature-card" data-feature="small-gestures"><span>❋</span><strong>Small gestures</strong><small>The little things that keep love alive every day</small></div>
<div class="feature-card" data-feature="future-ring"><span>◌</span><strong>Future ring</strong><small>Promises, dreams, and forever shaped in one beautiful vision</small></div>
<div class="feature-card" data-feature="slow-dance"><span>♡</span><strong>Slow dance</strong><small>Holding each other close while the world fades away</small></div>
<div class="feature-card" data-feature="heart-home"><span>♥</span><strong>Heart home</strong><small>Where comfort, love, and belonging finally feel complete</small></div>
</div>
</div>
</section>
<section class="screen story-slides" id="featureDetailScreen">
<div class="slide-panel detail-panel">
<div class="story-slide-header">
<div><p class="kicker small">DETAIL</p><h2 id="detailTitle">Our romance</h2></div>
<div class="story-actions compact"><button class="ghost alt" id="backToStoryBtn" type="button">← BACK TO STORY</button></div>
</div>
<div class="story-quote" id="detailText">This is how we make our love feel warm, safe, and unforgettable.</div>
<div class="detail-visual">
<div class="detail-badge">Kapil &amp; Gayatri</div>
<ul id="detailMeta" class="detail-list-mini"></ul>
</div>
</div>
</section>
<section class="screen" id="dashboardScreen">
<div class="dashboard-head"><div><p class="kicker">KEINSTEIN · Constellation complete</p><h1>Welcome, <span id="dashboardName">traveler</span>.</h1><p>Your personal adventure universe is ready.</p></div><button class="ghost" id="dashboardLogout">← SIGN OUT</button></div>
<div class="dashboard-grid"><div class="welcome-panel"><div><h2>Your story starts here ✦</h2><p id="dashboardMessage">Your blue buddy has prepared a bright little space for you and your favorite person.</p><div class="stat-row"><div class="stat"><strong>01</strong>new quest</div><div class="stat"><strong>∞</strong>possibilities</div><div class="stat"><strong>✦</strong>good vibes</div></div></div><button class="primary dashboard-button" id="arcadeButton">ENTER THE ARCADE &nbsp; →</button></div><div class="character-panel"><div class="buddy-pair"><div class="character big-character"><div class="hair"></div><div class="ribbon"></div><div class="face"><span class="face-smile"></span></div><div class="body"></div><div class="arm"></div></div><div class="character big-character robot"><div class="hair"></div><div class="ribbon"></div><div class="face"><span class="face-smile"></span></div><div class="body"></div><div class="arm"></div></div></div></div></div>
<div class="dashboard-tools"><div class="tool-card"><h3>Profile</h3><p>See your saved account and education details.</p><button data-panel="profilePanel">OPEN PROFILE</button></div><div class="tool-card"><h3>Love story</h3><p>Write a note for your partner and keep it close.</p><button data-panel="storyPanel">EDIT STORY</button></div><div class="tool-card"><h3>Memories</h3><p>Keep a simple timeline of moments together.</p><button data-panel="memoryPanel">VIEW MEMORIES</button></div><div class="tool-card"><h3>Special date</h3><p>Set a date and watch the countdown together.</p><button data-panel="datePanel">SET COUNTDOWN</button></div><div class="tool-card"><h3>Daily quote</h3><p>Get a fresh romantic thought each day.</p><button id="quoteButton">NEW QUOTE</button></div><div class="tool-card"><h3>Mika chat</h3><p>Ask your friendly guide for a little encouragement.</p><button data-panel="chatPanel">CHAT NOW</button></div><div class="tool-card"><h3>Music</h3><p>Toggle a gentle ambient sound layer.</p><button id="musicButton">MUSIC OFF</button></div><div class="tool-card"><h3>Settings</h3><p>Choose your theme and preferred language.</p><button data-panel="settingsPanel">SETTINGS</button></div><div class="tool-card"><h3>Admin</h3><p>View saved accounts from the local database.</p><button data-panel="adminPanel">OPEN ADMIN</button></div></div>
<div class="tool-panel" id="profilePanel"><h2>Your saved profile</h2><dl class="detail-list"><div><dt>Name</dt><dd id="profileName">-</dd></div><div><dt>Partner</dt><dd id="profilePartner">-</dd></div><div><dt>Course</dt><dd id="profileCourse">-</dd></div><div><dt>Qualification</dt><dd id="profileQualification">-</dd></div><div><dt>Current study</dt><dd id="profileStudy">-</dd></div></dl></div>
<div class="tool-panel" id="storyPanel"><h2>Our love story</h2><div class="mini-form"><input id="storyTitle" placeholder="Story title"><textarea id="storyText" placeholder="Write something beautiful about your partner..."></textarea><button id="storySave">SAVE STORY</button></div><p id="storySaved"></p></div>
<div class="tool-panel" id="memoryPanel"><h2>Memory timeline</h2><div class="memory-list" id="memoryList"><div class="memory"><strong>Today</strong><span>Your KEINSTEIN journey began.</span></div></div><div class="mini-form" style="margin-top:12px"><input id="memoryTitle" placeholder="Memory title"><input id="memoryDate" type="date"><input id="memoryNote" placeholder="One line to remember"><button id="memorySave">ADD MEMORY</button></div></div>
<div class="tool-panel" id="datePanel"><h2>Countdown to a special date</h2><div class="mini-form"><input id="specialDate" type="datetime-local"><button id="dateSave">START COUNTDOWN</button></div><div class="countdown" id="countdown"><div class="count-box"><strong>--</strong><span>days</span></div><div class="count-box"><strong>--</strong><span>hours</span></div><div class="count-box"><strong>--</strong><span>minutes</span></div></div></div>
<div class="tool-panel" id="quotePanel"><h2>Today’s thought</h2><div class="quote" id="quoteText">Love is built from a thousand small choices to stay kind.</div></div>
<div class="tool-panel" id="chatPanel"><h2>Talk with Mika</h2><div class="chat-log" id="chatLog"><div class="chat-line"><b>Mika:</b> Tell me what is on your heart.</div></div><div class="chat-form"><input id="chatInput" placeholder="Say hello to Mika"><button id="chatSend">SEND</button></div></div>
<div class="tool-panel" id="settingsPanel"><h2>Experience settings</h2><div class="setting-row"><label><input id="darkToggle" type="checkbox"> Deep night theme</label><label for="language">Language</label><select id="language"><option>English</option><option>Hindi</option><option>Telugu</option></select><span id="languageStatus"></span></div></div>
<div class="tool-panel" id="adminPanel"><h2>Admin account list</h2><table class="admin-table"><thead><tr><th>Name</th><th>Partner</th><th>Email</th><th>Course</th></tr></thead><tbody id="adminRows"><tr><td colspan="4">Loading...</td></tr></tbody></table></div>
</section>
<section class="screen" id="arcadeScreen">
<div class="arcade-head"><div><p class="kicker">KEINSTEIN · Choose your challenge</p><h1>Temple <span>runner.</span></h1></div><div class="difficulty"><label for="difficulty">Difficulty</label><select id="difficulty"><option value="easy">Easy · slow</option><option value="medium" selected>Medium · fast</option><option value="hard">Hard · very fast</option></select><button class="ghost" id="arcadeBack">← DASHBOARD</button></div></div>
<div class="game-grid"><article class="game-card"><div class="game-icon">🏃</div><h2>Temple Escape</h2><p>Guide the masked ninja through an ancient temple. Dodge pillars and survive the run.</p><button class="game-launch" data-game="runner">PLAY RUN</button></article><article class="game-card"><div class="game-icon">🏎️</div><h2>Neon Drift</h2><p>Keep your car on the road and chase a high score.</p><button class="game-launch" data-game="car">PLAY RACE</button></article><article class="game-card"><div class="game-icon">🏍️</div><h2>Skyline Bike</h2><p>Tap to jump through the moonlit city course.</p><button class="game-launch" data-game="bike">PLAY RIDE</button></article><article class="game-card"><div class="game-icon">🚀</div><h2>Cosmic Blaster</h2><p>Defend the star map by firing at incoming space rocks.</p><button class="game-launch" data-game="shooter">PLAY SHOOTER</button></article><article class="game-card"><div class="game-icon">🧠</div><h2>Memory Match</h2><p>Flip cards and match the symbols with the fewest moves.</p><button class="game-launch" data-game="memory">PLAY MEMORY</button></article></div>
<div class="game-area" id="gameArea"><div class="game-hud"><span class="hud-chip" id="lives">♥ Lives: 3</span><span class="hud-chip" id="coins">◈ Coins: 0</span><span class="hud-chip" id="level">Level: 1</span></div><span class="score" id="score">Score: 0</span><h2 id="gameTitle">Temple Escape</h2><p id="gameInstructions">Choose a difficulty, then switch lanes to avoid the temple obstacles.</p><div class="game-canvas" id="gameCanvas"><div class="jungle"></div><div class="temple"></div><div class="runner-road"></div><div class="obstacle lane-left"></div><div class="obstacle lane-center"></div><div class="obstacle lane-right"></div><div class="target-zone">ANCIENT TEMPLE RUN</div><div class="runner" id="vehicle"></div></div><div class="memory-board" id="memoryBoard"></div><button class="tap-button" id="gameAction">SWITCH LANE &nbsp; →</button><div class="leaderboard"><strong>Leaderboard</strong> · You &nbsp; <span id="leaderScore">0</span> pts &nbsp; · Mika 120 pts &nbsp; · Gayatri 99 pts</div></div>
</section>
<div class="footer"><span>© 2026 · Keep looking up</span><span class="instagram"><span class="instagram-icon" aria-hidden="true"></span> Instagram · kapil_xarania_</span></div>
</div>
<div class="modal" id="modal"><div class="modal-box"><div class="modal-icon" id="modalIcon">🌟</div><h3 id="modalTitle">Your star map is ready!</h3><p id="modalText">Mika has saved a place for you in the constellation.</p><button class="primary" id="closeModal">LET’S GO &nbsp; ✦</button></div></div>
<div class="toast" id="toast"></div>
<script>
const $ = (selector) => document.querySelector(selector);
const nameInput = $('#name');
const partnerInput = $('#partner');
const emailInput = $('#email');
const passwordInput = $('#password');
const helperText = $('#helperText');
const toast = $('#toast');
const solarSystem = $('.front-solar');
const loginLayout = $('.layout');
const dashboardScreen = $('#dashboardScreen');
const arcadeScreen = $('#arcadeScreen');
const kapilWorldScreen = $('#kapilWorldScreen');
const loveStoryScreen = $('#loveStoryScreen');
const featureDetailScreen = $('#featureDetailScreen');
let currentScore = 0;
let activeGame = 'car';
let runnerLane = 1;
let memoryFirst = null;
let memoryLocked = false;
let savedProfile = {};
let musicContext = null;
let musicOscillator = null;
let countdownTimer = null;
const tips = [
 'Start with your name — I promise it looks good here.',
 'A partner, a best friend, or your favorite person all count.',
 'Your email is just for your private star map.',
 'Almost there! Make your password something memorable.',
 'You’re doing great. The stars are lining up.',
 'That name has excellent main-character energy.',
 'Every good story needs a wonderful supporting character.',
 'I like your choices. This is going to be lovely.',
 'A little courage, a little curiosity, and we’re ready.',
 'Your tiny universe is waiting for you.'
];
let tipIndex = 0;
function showTip(text) { helperText.textContent = text; }
function nextTip() { tipIndex = (tipIndex + 1) % tips.length; showTip(tips[tipIndex]); }
function clean(value) { return value.trim().replace(/\s+/g, ' '); }
function setHint(id, message) { $(id).textContent = message; }
function mark(input, valid) { input.classList.toggle('invalid', !valid); }
function validateName() {
 const value = clean(nameInput.value);
 const valid = value.length >= 2;
 mark(nameInput, valid);
 setHint('#nameHint', valid || !value ? '' : 'Please enter at least 2 characters.');
 return valid;
}
function validatePartner() {
 const value = clean(partnerInput.value);
 const valid = value.length >= 2;
 mark(partnerInput, valid);
 setHint('#partnerHint', valid || !value ? '' : 'A name with at least 2 characters works best.');
 return valid;
}
function validateEmail() {
 const value = clean(emailInput.value);
 const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
 mark(emailInput, valid);
 setHint('#emailHint', valid || !value ? '' : 'Please check the email format.');
 return valid;
}
function validatePassword() {
 const value = passwordInput.value;
 const valid = value.length >= 6;
 mark(passwordInput, valid);
 setHint('#passwordHint', valid || !value ? '' : 'Use 6 or more characters.');
 return valid;
}
function updateWelcome() {
 const name = clean(nameInput.value);
 const partner = clean(partnerInput.value);
 if (name) $('#subtitle').textContent = `Nice to meet you, ${name}.`;
 else $('#subtitle').textContent = 'Let’s make today memorable.';
 if (partner) showTip(`I’ll save a little constellation for ${partner}.`);
}
nameInput.addEventListener('input', () => { validateName(); updateWelcome(); });
partnerInput.addEventListener('input', () => { validatePartner(); updateWelcome(); });
emailInput.addEventListener('input', validateEmail);
passwordInput.addEventListener('input', validatePassword);
passwordInput.addEventListener('focus', () => showTip(tips[3]));
setInterval(nextTip, 6000);
$('#passwordToggle').addEventListener('click', () => {
 passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
 $('#passwordToggle').textContent = passwordInput.type === 'password' ? '◉' : '◎';
});
$('#forgot').addEventListener('click', () => {
 showTip('Try a favorite word plus a number. Your secret is yours alone.');
 showToast('Mika’s hint: make it memorable, never predictable.');
});
function showToast(message) {
 toast.textContent = message;
 toast.classList.add('show');
 clearTimeout(window.toastTimer);
 window.toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
}
function openModal(title, text, icon) {
 $('#modalTitle').textContent = title;
 $('#modalText').textContent = text;
 $('#modalIcon').textContent = icon;
 $('#modal').classList.add('open');
}
function showScreen(screen) {
 loginLayout.style.display = 'none';
 solarSystem.classList.add('hidden');
 [dashboardScreen, arcadeScreen, kapilWorldScreen, loveStoryScreen, featureDetailScreen].forEach((element) => element.classList.remove('visible'));
 if (screen) {
  screen.classList.add('visible');
  if (screen === featureDetailScreen) {
   requestAnimationFrame(() => {
    featureDetailScreen.classList.remove('detail-film');
    void featureDetailScreen.offsetWidth;
    featureDetailScreen.classList.add('detail-film');
   });
  }
 }
}
function showLogin() {
 loginLayout.style.display = '';
 solarSystem.classList.remove('hidden');
 [dashboardScreen, arcadeScreen, kapilWorldScreen, loveStoryScreen, featureDetailScreen].forEach((element) => element.classList.remove('visible'));
}
function showKapilWorld() {
 const name = clean(nameInput.value) || 'traveler';
 const partner = clean(partnerInput.value) || 'your favorite person';
 const course = clean($('#course').value) || 'your studies';
 savedProfile = { name, partner, course, qualification:clean($('#qualification').value), currentStudy:clean($('#currentStudy').value) };
 $('#dashboardName').textContent = name;
 $('#dashboardMessage').textContent = `Mika has prepared a bright little space for you and ${partner}. Your path in ${course} is part of your adventure.`;
 $('#modal').classList.remove('open');
 showScreen(kapilWorldScreen);
}
function showLoveStorySlide() {
 showScreen(loveStoryScreen);
}
function openPanel(panelId) {
 document.querySelectorAll('.tool-panel').forEach((panel) => panel.classList.remove('open'));
 const panel = $(`#${panelId}`);
 panel.classList.add('open');
 if (panelId === 'profilePanel') renderProfile();
 if (panelId === 'adminPanel') loadAdminAccounts();
 panel.scrollIntoView({ behavior:'smooth', block:'nearest' });
}
document.querySelectorAll('[data-panel]').forEach((button) => button.addEventListener('click', () => openPanel(button.dataset.panel)));
function renderProfile() {
 const values = { Name:'name', Partner:'partner', Course:'course', Qualification:'qualification', Study:'currentStudy' };
 Object.entries(values).forEach(([label, key]) => { const target = $(`#profile${label}`); if (target) target.textContent = savedProfile[key] || 'Not provided'; });
}
function loadAdminAccounts() {
 fetch('/api/accounts').then((response) => response.json()).then((data) => {
  const rows = data.accounts.map((account) => `<tr><td>${account.name}</td><td>${account.partner}</td><td>${account.email}</td><td>${account.course || '-'}</td></tr>`).join('');
  $('#adminRows').innerHTML = rows || '<tr><td colspan="4">No saved accounts yet.</td></tr>';
 }).catch(() => { $('#adminRows').innerHTML = '<tr><td colspan="4">Admin data is unavailable.</td></tr>'; });
}
const quotes = ['Love is built from a thousand small choices to stay kind.', 'The best memories begin as ordinary moments shared with someone special.', 'Home is not a place; it is the peace you feel beside the right person.', 'Two people grow closer every time they choose understanding over pride.'];
$('#quoteButton').addEventListener('click', () => { openPanel('quotePanel'); $('#quoteText').textContent = quotes[Math.floor(Math.random() * quotes.length)]; });
$('#storySave').addEventListener('click', () => { const title = clean($('#storyTitle').value) || 'Our story'; const text = clean($('#storyText').value) || 'A beautiful story still being written.'; localStorage.setItem('keinsteinStory', JSON.stringify({ title, text })); $('#storySaved').textContent = `${title} saved for ${savedProfile.partner || 'your partner'}.`; showToast('Your love story is saved locally ✦'); });
$('#memorySave').addEventListener('click', () => { const title = clean($('#memoryTitle').value) || 'A special day'; const note = clean($('#memoryNote').value) || 'A moment worth remembering.'; const date = $('#memoryDate').value || new Date().toISOString().slice(0,10); const memory = document.createElement('div'); memory.className = 'memory'; memory.innerHTML = `<strong>${title}</strong><span>${date} · ${note}</span>`; $('#memoryList').prepend(memory); });
$('#dateSave').addEventListener('click', () => { const value = $('#specialDate').value; if (!value) return showToast('Choose a special date first.'); startCountdown(new Date(value)); });
function startCountdown(target) { clearInterval(countdownTimer); const tick = () => { const remaining = Math.max(0, target - new Date()); const units = [86400000, 3600000, 60000]; $('#countdown').innerHTML = units.map((unit, index) => `<div class="count-box"><strong>${Math.floor(remaining / unit) % (index ? (index === 1 ? 24 : 60) : 9999)}</strong><span>${['days','hours','minutes'][index]}</span></div>`).join(''); }; tick(); countdownTimer = setInterval(tick, 60000); }
$('#chatSend').addEventListener('click', () => { const input = $('#chatInput'); const message = clean(input.value); if (!message) return; $('#chatLog').insertAdjacentHTML('beforeend', `<div class="chat-line"><b>You:</b> ${message}</div>`); const reply = message.toLowerCase().includes('love') ? 'Love grows when you make room for honesty and kindness.' : 'That sounds important. Keep going, I’m listening.'; $('#chatLog').insertAdjacentHTML('beforeend', `<div class="chat-line"><b>Mika:</b> ${reply}</div>`); input.value = ''; });
$('#musicButton').addEventListener('click', () => { if (musicContext) { musicContext.close(); musicContext = null; musicOscillator = null; $('#musicButton').textContent = 'MUSIC OFF'; showToast('Ambient music paused.'); return; } musicContext = new AudioContext(); musicOscillator = musicContext.createOscillator(); const gain = musicContext.createGain(); musicOscillator.frequency.value = 196; gain.gain.value = .025; musicOscillator.connect(gain).connect(musicContext.destination); musicOscillator.start(); $('#musicButton').textContent = 'MUSIC ON'; showToast('Soft ambient sound started.'); });
$('#darkToggle').addEventListener('change', (event) => document.body.classList.toggle('theme-dark', event.target.checked));
$('#language').addEventListener('change', (event) => { $('#languageStatus').textContent = `${event.target.value} selected`; });
$('#closeModal').addEventListener('click', showKapilWorld);
$('#modal').addEventListener('click', (event) => { if (event.target.id === 'modal') $('#modal').classList.remove('open'); });
$('#dashboardLogout').addEventListener('click', showLogin);
$('#arcadeButton').addEventListener('click', () => showScreen(arcadeScreen));
$('#arcadeBack').addEventListener('click', () => showScreen(dashboardScreen));
$('#showLoveStoryBtn').addEventListener('click', showLoveStorySlide);
$('#backToWorldBtn').addEventListener('click', showKapilWorld);
$('#backToFormBtn').addEventListener('click', showLogin);
$('#backToStoryBtn').addEventListener('click', showLoveStorySlide);
const featureDetails = {
  'our-romance': { title: 'Our romance', text: 'Our romance feels like a soft sunrise over a quiet city, gentle, warm, and full of meaning. Every smile, every shared silence, and every comforting glance turns ordinary moments into something deeply personal. It is the kind of love that feels like home: safe, beautiful, and glowing from the inside, always.', points: ['Warm hugs', 'Gentle trust', 'Shared joy'] },
  'love-note': { title: 'Love note', text: 'A love note is where feeling becomes language, beautiful and honest in the simplest form. Even a short message can carry the weight of longing, comfort, and affection. It says, “I was thinking of you,” and in that tiny sentence, love becomes visible, alive, and unforgettable in the deepest way.', points: ['Sweet messages', 'Kind words', 'Heartfelt timing'] },
  'dream-visits': { title: 'Dream visits', text: 'Dream visits are the quiet spaces where hope takes shape. We meet in the future, a little brighter each time, imagining adventures, shared goals, and a life that grows softer and more beautiful together. They are not just wishes but promises written in stardust, trust, and the courage to keep reaching for tomorrow.', points: ['Dream plans', 'Big hopes', 'Future together'] },
  'morning-glow': { title: 'Morning glow', text: 'Morning glow is the brightness that appears when two hearts begin the day in calm understanding. The first conversation, the warm smile, the small ritual of being near each other turns the most ordinary morning into something luminous. It is love working gently, making the whole world feel lighter, kinder, and wonderfully alive.', points: ['Sunrise smiles', 'Calm start', 'Sweet routines'] },
  'travel-plans': { title: 'Travel plans', text: 'Travel plans are about more than destinations; they are about discovering the world together, one laugh, one street, one memory at a time. Every road trip, train ride, city walk, and late-night detour becomes a chapter of our story. Through every new place, love grows more vivid, courageous, and beautifully shared.', points: ['Road trips', 'City walks', 'New memories'] },
  'little-rituals': { title: 'Little rituals', text: 'Little rituals are the heartbeat of love: tea, messages, jokes, quiet glances, and the tiny acts that say, “I am here with you.” They look small from the outside, but they create a rhythm of comfort and belonging. In these gentle habits, warmth grows, trust deepens, and the relationship becomes a home for both souls.', points: ['Tea time', 'Inside jokes', 'Comfort'] },
  'shared-laughter': { title: 'Shared laughter', text: 'Shared laughter is pure light. It is the moment a joke lands just right, the smile that comes without effort, and the happiness of feeling completely at ease. In those bright, honest seconds, love feels effortless and joyful. It reminds us that the richest connection is not only serious or deep but also playful, free, and wonderfully alive.', points: ['Smiles', 'Lightness', 'Bond'] },
  'forever-promise': { title: 'Forever promise', text: 'A forever promise is not spoken once and forgotten; it is lived through patience, loyalty, softness, and steady care. It means choosing each other again and again, even in silence, uncertainty, and difficult seasons. It is a quiet vow that love is not just a feeling but a practiced devotion becoming stronger with every passing day.', points: ['Trust', 'Loyalty', 'Patience'] },
  'timeline': { title: 'Timeline', text: 'Our timeline is a beautiful map of becoming. Each first hello, each small step, each hard moment and each joyful one adds shape to the story we are writing together. Looking back, we see not just moments, but growth. Looking forward, we feel the future opening gently, full of possibility, tenderness, and a love that keeps unfolding in its own time.', points: ['First hello', 'Growing together', 'Forever steps'] },
  'late-night-talks': { title: 'Late-night talks', text: 'Late-night talks carry the truest version of the heart. In the stillness, we share fears, dreams, memories, and the honest feelings we do not always say in daylight. They are soft, intimate, and deeply comforting, like a lantern glowing in the dark. Those conversations create closeness and remind us that love is strongest when it is sincere.', points: ['Honesty', 'Closeness', 'Calm'] },
  'gallery': { title: 'Gallery', text: 'Our gallery is a living archive of joy. Every photo, every captured smile, every moment in a frame holds a feeling too vivid to forget. These memories become proof that love is not only in grand gestures but in the little glows of life: quiet laughter, warm embraces, shining eyes, and the beautiful truth that we were here and we were happy together.', points: ['Snapshots', 'Moments', 'Love in frames'] },
  'growth': { title: 'Growth', text: 'Growth in love means becoming softer, wiser, and kinder without losing your own light. Together, we learn to listen deeper, forgive faster, and celebrate each other more honestly. The relationship becomes a space where both hearts can bloom, not in competition but in reflection, trust, and the quiet confidence that we are better because we are growing side by side.', points: ['Kindness', 'Strength', 'Balance'] },
  'support': { title: 'Support', text: 'Support is the quiet power behind a strong relationship. It is the hand held in hard moments, the patient listening, the steady faith that says, “I am with you.” In love, support is not only carrying sorrow but also making room for hope, cheering for each other’s dreams, and turning fear into courage simply by being present, grounded, and deeply caring.', points: ['Safety', 'Patience', 'Togetherness'] },
  'inside-jokes': { title: 'Inside jokes', text: 'Inside jokes are the secret language of a beautiful bond. They are the playful comments, the nonsense that only the two of us understand, and the laughter that turns a normal moment into a treasured memory. These tiny exchanges build a world of closeness, as if love has its own private universe—a place filled with teasing, joy, and the comfort of being known very well.', points: ['Secrets', 'Laughs', 'Connection'] },
  'daily-checkins': { title: 'Daily check-ins', text: 'Daily check-ins are small but powerful signs of love. A simple message, a gentle question, a little bit of attention can carry warmth across a long day. They say, “I see you, I care about you, and I want to know how your heart feels.” In that rhythm of care, love remains alive, close, and beautifully present even from a distance.', points: ['Care', 'Attention', 'Warmth'] },
  'spark': { title: 'Spark', text: 'The spark is the electric feeling that still glows between us, even after years of familiarity. It is the excitement of seeing each other, the rush of connection, and the beautiful reminder that love is not only steady but alive. That spark keeps things bright, keeps curiosity alive, and makes every new moment feel full of possibility, tenderness, and wonder.', points: ['Excitement', 'Electricity', 'Connection'] },
  'endless-love': { title: 'Endless love', text: 'Endless love is the kind that keeps stretching beyond the moment, beyond the ordinary, and toward a future filled with hope. It is the faith that love can grow deeper, wider, and brighter with time. Even when life is uncertain, this kind of love remains steady—full of trust, beauty, and a quiet certainty that what we share is something powerful, lasting, and wonderfully real.', points: ['Hope', 'Future', 'Forever'] },
  'true-beauty': { title: 'True beauty', text: 'True beauty is not only how someone looks, but how they make the heart feel. It is the comfort of being seen without pretence, the safety of being accepted honestly, and the joy of being loved in your most unguarded form. This kind of beauty is gentle and deep, shining in the way love makes a person feel valued, peaceful, and fully alive.', points: ['Presence', 'Acceptance', 'Love'] },
  'cafe-dates': { title: 'Café dates', text: 'Café dates are where the day slows down and love feels quiet and beautiful. Warm drinks, soft conversations, and the rhythm of sitting close to each other create a scene that is simple yet unforgettable. In these small moments, life becomes peaceful and vivid at the same time. The world may be busy, but with each other, every sip and every glance turns into a memory worth keeping.', points: ['Coffee', 'Conversation', 'Peace'] },
  'future-home': { title: 'Future home', text: 'Future home is the dream of a life built with warmth, laughter, and belonging. It is not just a place to live but a feeling of ease, comfort, and emotional safety. With each other, even ordinary days can feel like home. We imagine a space where kindness lives in every corner, peace grows in every room, and love becomes the gentle architecture of our everyday life.', points: ['Warmth', 'Belonging', 'Home'] },
  'playlist': { title: 'Playlist', text: 'Our playlist is the soundtrack of emotions that words cannot fully hold. Every song carries a memory, a mood, or a moment we shared. They remind us of the times we laughed, dreamt, missed each other, or felt deeply close. In music, love becomes something you can hear, feel, and revisit again and again, making the story of us richer, softer, and endlessly alive.', points: ['Songs', 'Sentiment', 'Memories'] },
  'plans': { title: 'Plans', text: 'Our plans are woven from hope, intention, and the beautiful courage to imagine a life together. They are the dreams we talk about with excitement, the choices we make with care, and the future we build one thoughtful step at a time. In every plan, there is trust, possibility, and the quiet confidence that love gives shape to even the biggest dreams.', points: ['Dreams', 'Goals', 'Trust'] },
  'care': { title: 'Care', text: 'Care is how love shows up in the details: the gentleness, the patience, the small acts of noticing and helping. It is in the comfort of being listened to, the kindness in a difficult moment, and the tenderness of making someone feel safe. Care turns love into a living experience, one that is steady, warm, and deeply beautiful in the ordinary rhythm of daily life.', points: ['Kindness', 'Tenderness', 'Attention'] },
  'forever': { title: 'Forever', text: 'Forever is more than a grand word; it is a conscious promise to keep choosing each other with love, grace, and sincerity. It means staying open-hearted, staying faithful, and believing that what is real can grow stronger with time. In that promise, life becomes more meaningful, and every ordinary day becomes a quiet celebration of a love that is patient, beautiful, and undeniably enduring.', points: ['Promise', 'Grace', 'Sincerity'] },
  'stargazing': { title: 'Stargazing', text: 'Stargazing turns the night into a soft canvas of dreams and quiet wonder. As the sky fills with light, we imagine a future where our hopes shine just as brightly. Wrapped in the stillness, we talk about wishes, calm moments, and the beautiful feeling of seeing life unfold gently together under the stars.', points: ['Night wishes', 'Quiet wonder', 'Shared dreams'] },
  'small-gestures': { title: 'Small gestures', text: 'The smallest gestures often hold the greatest love. A message at the right time, a gentle touch, a thoughtful act, or a warm smile can change the entire mood of a day. They remind us that love is not only grand and cinematic but also beautifully alive in the everyday details that make two hearts feel close.', points: ['Thoughtfulness', 'Warmth', 'Little joys'] },
  'future-ring': { title: 'Future ring', text: 'The future ring is a vision of hope, commitment, and the gentle promise of forever. It lives in our dreams of what is yet to come: a life filled with trust, beauty, laughter, and the kind of love that grows brighter with time. In that promise, even the distant future feels warm, exciting, and beautifully ours.', points: ['Commitment', 'Hope', 'Beautiful future'] },
  'slow-dance': { title: 'Slow dance', text: 'A slow dance is when the world fades away and only the rhythm of love remains. In each movement, there is comfort, trust, and the feeling of being completely at peace together. It is a reminder that love sometimes feels most beautiful in stillness, where two hearts become one gentle motion and the rest of the world simply disappears.', points: ['Trust', 'Harmony', 'Togetherness'] },
  'heart-home': { title: 'Heart home', text: 'Heart home is where comfort meets belonging. It is the place where the heart feels safe, understood, and fully accepted. With each other, ordinary life becomes warm and meaningful, and every familiar moment turns into a gentle reminder that love is not only passion but also peace, rest, and the quiet joy of always being home in one another.', points: ['Belonging', 'Peace', 'Safety'] }
};

document.querySelectorAll('.feature-card').forEach((card) => {
  card.addEventListener('click', () => {
    const detail = featureDetails[card.dataset.feature];
    if (!detail) return;
    $('#detailTitle').textContent = detail.title;
    $('#detailText').textContent = detail.text;
    $('#detailMeta').innerHTML = detail.points.map((point) => `<li>${point}</li>`).join('');
    showScreen(featureDetailScreen);
  });
});
function startGame(game) {
 activeGame = game;
 currentScore = 0;
 $('#score').textContent = 'Score: 0';
 $('#gameArea').classList.add('open');
 const vehicle = $('#vehicle');
 $('#memoryBoard').style.display = 'none';
 document.querySelectorAll('.game-canvas > *').forEach((element) => { element.style.display = ''; });
 vehicle.className = game === 'bike' ? 'vehicle bike' : 'vehicle';
	if (game === 'runner') {
	vehicle.className = 'runner';
	$('#gameCanvas').className = `game-canvas ${$('#difficulty').value}`;
	$('#gameTitle').textContent = 'Temple Escape';
	$('#gameInstructions').textContent = 'Switch lanes to avoid the pillars. Easy is slow, medium is fast, hard is very fast.';
	$('#gameAction').textContent = 'SWITCH LANE  →';
 } else if (game === 'car') {
  $('#gameTitle').textContent = 'Neon Drift';
  $('#gameInstructions').textContent = 'Press the button when the car reaches the target zone.';
  vehicle.style.animation = 'none';
	$('#gameAction').textContent = 'TAP TO SCORE';
 } else if (game === 'bike') {
  $('#gameTitle').textContent = 'Skyline Bike';
  $('#gameInstructions').textContent = 'Tap to make your rider jump over the glowing road lines.';
  vehicle.style.animation = 'bike-bounce 1.2s ease-in-out infinite';
	$('#gameAction').textContent = 'TAP TO SCORE';
	 } else if (game === 'shooter') {
	  vehicle.className = 'vehicle';
	  $('#gameTitle').textContent = 'Cosmic Blaster';
	  $('#gameInstructions').textContent = 'Tap to fire at space rocks and collect coins.';
	  $('#gameAction').textContent = 'FIRE LASER  ✦';
	 } else if (game === 'memory') {
	  document.querySelectorAll('.game-canvas > *').forEach((element) => { element.style.display = 'none'; });
	  $('#memoryBoard').style.display = 'grid';
	  $('#gameTitle').textContent = 'Memory Match';
	  $('#gameInstructions').textContent = 'Find every matching pair. Each match earns coins and points.';
	  $('#gameAction').textContent = 'NEW BOARD';
	  setupMemory();
 } else {
  $('#gameTitle').textContent = 'Star Strike';
  $('#gameInstructions').textContent = 'Tap quickly to fire star energy at the target.';
  vehicle.style.animation = 'target-pulse .8s ease-in-out infinite alternate';
	$('#gameAction').textContent = 'TAP TO SCORE';
 }
 $('#gameArea').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
function setupMemory() {
 memoryFirst = null; memoryLocked = false;
 const symbols = ['✦','♥','☾','◆','✦','♥','☾','◆'].sort(() => Math.random() - .5);
 $('#memoryBoard').innerHTML = symbols.map((symbol, index) => `<button class="memory-tile" data-symbol="${symbol}" data-index="${index}">${symbol}</button>`).join('');
 document.querySelectorAll('.memory-tile').forEach((tile) => tile.addEventListener('click', () => {
  if (memoryLocked || tile.classList.contains('flipped')) return;
  tile.classList.add('flipped');
  if (!memoryFirst) { memoryFirst = tile; return; }
  if (memoryFirst.dataset.symbol === tile.dataset.symbol) { currentScore += 2; $('#coins').textContent = `◈ Coins: ${currentScore}`; $('#score').textContent = `Score: ${currentScore}`; memoryFirst = null; } else { memoryLocked = true; setTimeout(() => { memoryFirst.classList.remove('flipped'); tile.classList.remove('flipped'); memoryFirst = null; memoryLocked = false; }, 650); }
 }));
}
document.querySelectorAll('.game-launch').forEach((button) => button.addEventListener('click', () => startGame(button.dataset.game)));
$('#difficulty').addEventListener('change', () => {
 if (activeGame === 'runner') $('#gameCanvas').className = `game-canvas ${$('#difficulty').value}`;
 showToast(`Difficulty set to ${$('#difficulty').value}. Good luck, runner ✦`);
});
$('#gameAction').addEventListener('click', () => {
 if (activeGame === 'memory') { setupMemory(); return; }
 if (activeGame === 'runner') {
  runnerLane = (runnerLane + 1) % 3;
  $('#vehicle').style.left = runnerLane === 0 ? '29%' : runnerLane === 1 ? 'calc(50% - 17px)' : 'calc(71% - 17px)';
  currentScore += 1;
  showToast('Lane change! Keep your eyes on the pillars ✦');
  $('#score').textContent = `Score: ${currentScore}`;
  return;
 }
 currentScore += activeGame === 'action' ? 2 : 1;
 $('#score').textContent = `Score: ${currentScore}`;
 showToast(activeGame === 'bike' ? 'Great jump! Keep riding ✦' : activeGame === 'car' ? 'Clean drift! Keep going ✦' : 'Direct hit! Spark collected ✦');
});
$('#loginForm').addEventListener('submit', (event) => {
 event.preventDefault();
 const valid = validateName() & validatePartner() & validateEmail() & validatePassword();
 if (!valid) { showTip('A few details need your attention. I’ll wait right here.'); return; }
 const name = clean(nameInput.value);
 const partner = clean(partnerInput.value);
 $('#submit').textContent = 'WELCOME TO KAPIL’S WORLD  ✦';
 showTip(`Welcome, ${name}! ${partner} is going to love this.`);
 const account = { name, partner, course:clean($('#course').value), qualification:clean($('#qualification').value), currentStudy:clean($('#currentStudy').value), email:clean(emailInput.value), password:passwordInput.value };
 fetch('/api/accounts', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(account) }).then((response) => response.json()).then((result) => { if (result.error) showToast(result.error); }).catch(() => showToast('Saved for this session; database is unavailable.'));
 openModal(`Welcome, ${name}!`, `Your private star map for you and ${partner} is ready. This is the beginning of something wonderful.`, '🌌');
});
document.querySelectorAll('.toggle').forEach((button) => {
 if (button.id !== 'passwordToggle') button.addEventListener('click', () => nextTip());
});
</script>
</body>
</html>'''


STORY_PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Our Love Story | KEINSTEIN</title>
<style>
:root {
  --bg: #0d153a;
  --bg-2: #1a214f;
  --card: rgba(255,255,255,0.08);
  --card-strong: rgba(255,255,255,0.12);
  --border: rgba(255,255,255,0.18);
  --text: #eef2ff;
  --muted: #d2d9ff;
  --peach: #ffc98d;
  --pink: #f59ac1;
  --violet: #9f88ff;
  --mint: #88f0d0;
}
* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; font-family: Arial, sans-serif; background: radial-gradient(circle at top, #27356e 0%, var(--bg) 38%, #090d1e 100%); color: var(--text); }
body { padding: 26px; }
a { color: inherit; text-decoration: none; }
.container { max-width: 1180px; margin: 0 auto; }
.topbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; }
.brand { font-weight: 800; letter-spacing: .15em; text-transform: uppercase; font-size: 12px; }
.brand-mark { display: inline-grid; place-items: center; width: 26px; height: 26px; border-radius: 8px; background: linear-gradient(135deg, var(--peach), var(--pink)); color: #26163d; margin-right: 8px; }
.nav { display: flex; gap: 10px; align-items: center; }
.nav a, .nav button { border: 1px solid var(--border); background: rgba(255,255,255,0.05); color: var(--text); padding: 10px 14px; border-radius: 12px; font-weight: 700; cursor: pointer; }
.hero { display: grid; grid-template-columns: 1.2fr .8fr; gap: 24px; align-items: stretch; }
.card { border: 1px solid var(--border); border-radius: 26px; background: linear-gradient(180deg, var(--card), rgba(255,255,255,0.04)); box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.hero-copy { padding: 32px; }
.kicker { text-transform: uppercase; letter-spacing: .2em; font-size: 11px; color: var(--peach); font-weight: 800; margin: 0 0 18px; }
.hero-copy h1 { margin: 0; font-size: clamp(2.6rem, 5vw, 5rem); line-height: 0.95; }
.hero-copy h1 span { color: var(--peach); }
.story-text { color: var(--muted); line-height: 1.8; font-size: 16px; max-width: 620px; margin-top: 20px; }
.badge-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }
.badge { padding: 9px 12px; border-radius: 999px; background: rgba(255,255,255,0.06); border: 1px solid var(--border); font-size: 12px; font-weight: 700; }
.profile-panel { padding: 26px; display: flex; flex-direction: column; justify-content: center; }
.avatar { width: 160px; height: 160px; margin: 0 auto 16px; border-radius: 32px; background: linear-gradient(135deg, rgba(255,201,141,.9), rgba(245,154,193,.8), rgba(159,136,255,.9)); display: grid; place-items: center; font-size: 54px; box-shadow: 0 18px 40px rgba(159,136,255,.25); }
.small-title { text-align: center; font-size: 12px; letter-spacing: .2em; text-transform: uppercase; color: var(--muted); margin: 0 0 12px; }
.profile-card p { margin: 0; color: var(--muted); line-height: 1.7; text-align: center; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 22px; margin-top: 28px; }
.section-card { padding: 26px; }
.section-card h2 { margin: 0 0 18px; font-size: clamp(1.6rem, 2vw, 2.2rem); }
.list { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
.list li { padding: 12px 14px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 14px; color: var(--muted); line-height: 1.6; }
.timeline { display: grid; gap: 12px; }
.timeline-item { position: relative; padding-left: 18px; border-left: 2px solid rgba(255,255,255,0.18); padding-bottom: 6px; }
.timeline-item:before { content: ''; position: absolute; left: -7px; top: 3px; width: 12px; height: 12px; border-radius: 50%; background: linear-gradient(135deg, var(--pink), var(--peach)); }
.timeline-item strong { display: block; margin-bottom: 4px; color: var(--text); }
.gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.photo { min-height: 150px; border-radius: 18px; display: grid; place-items: center; font-size: 38px; border: 1px solid var(--border); background: linear-gradient(135deg, rgba(255,201,141,.18), rgba(159,136,255,.2)); }
.quote-box { padding: 26px; border-left: 4px solid var(--peach); background: rgba(255,255,255,0.04); border-radius: 16px; color: var(--muted); font-size: 1.08rem; line-height: 1.8; }
.footer { margin-top: 28px; padding-top: 18px; color: var(--muted); text-align: center; font-size: 12px; letter-spacing: .13em; text-transform: uppercase; }
@media (max-width: 840px) {
  .hero, .grid { grid-template-columns: 1fr; }
  .topbar { flex-direction: column; gap: 12px; }
  .nav { flex-wrap: wrap; justify-content: center; }
  .gallery { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<div class="container">
  <header class="topbar">
    <div class="brand"><span class="brand-mark">✦</span>KEINSTEIN</div>
    <nav class="nav">
      <a href="/">Home</a>
      <button onclick="window.location.href='/'">Back to main page</button>
    </nav>
  </header>

  <main>
    <section class="hero">
      <div class="card hero-copy">
        <p class="kicker">About us</p>
        <h1>Our love story<br><span>is a warm little universe.</span></h1>
        <p class="story-text">This is the space where the little details live: the first smile, the quiet conversations, the laughter in ordinary days, and the feeling that home is not a place but a person who makes your heart soft and strong at the same time.</p>
        <div class="badge-row">
          <span class="badge">♡ Gentle love</span>
          <span class="badge">☀️ Shared dreams</span>
          <span class="badge">✦ Forever growing</span>
        </div>
      </div>

      <aside class="card profile-panel">
        <div class="avatar">♥</div>
        <p class="small-title">Kapil &amp; Gayatri</p>
        <div class="profile-card">
          <p>Two hearts, one rhythm, and a story that keeps unfolding in the most beautiful way.</p>
        </div>
      </aside>
    </section>

    <section class="grid">
      <article class="card section-card">
        <h2>About me</h2>
        <ul class="list">
          <li>I am the kind of person who believes love grows with patience, laughter, and small acts of care.</li>
          <li>I value calm moments, meaningful talks, and the comfort of being fully understood.</li>
          <li>I like building dreams with someone who feels like peace, adventure, and home all at once.</li>
        </ul>
      </article>

      <article class="card section-card">
        <h2>About us</h2>
        <ul class="list">
          <li>We are a bond of trust, warmth, and gentle understanding.</li>
          <li>We make life feel better just by being in it together.</li>
          <li>We choose kindness, softness, and joy in even the smallest moments.</li>
        </ul>
      </article>

      <article class="card section-card">
        <h2>Dreams together</h2>
        <ul class="list">
          <li>Travel to beautiful places and create memories that last forever.</li>
          <li>Build a future filled with laughter, teamwork, and deep respect.</li>
          <li>Keep making each other feel loved in ways that are genuine and lasting.</li>
        </ul>
      </article>
    </section>

    <section class="grid" style="margin-top: 22px;">
      <article class="card section-card">
        <h2>Our timeline</h2>
        <div class="timeline">
          <div class="timeline-item">
            <strong>First hello</strong>
            The moment the conversation felt easy and natural.
          </div>
          <div class="timeline-item">
            <strong>Small joys</strong>
            The everyday moments began to feel brighter and more meaningful.
          </div>
          <div class="timeline-item">
            <strong>Growing closer</strong>
            Trust, comfort, and affection kept becoming stronger.
          </div>
          <div class="timeline-item">
            <strong>Forever future</strong>
            A promise still being written, one beautiful day at a time.
          </div>
        </div>
      </article>

      <article class="card section-card">
        <h2>Favorite things</h2>
        <ul class="list">
          <li>Quiet evenings with heartfelt conversation.</li>
          <li>Warm smiles and little surprises that mean everything.</li>
          <li>Walking through life together, no matter what the day brings.</li>
        </ul>
      </article>

      <article class="card section-card">
        <h2>Our promise</h2>
        <div class="quote-box">
          “No matter how life changes, I want our love to remain gentle, honest, and brave — full of warmth, faith, and the courage to keep choosing each other.”
        </div>
      </article>
    </section>

    <section class="card section-card" style="margin-top: 24px;">
      <h2>Sweet memories</h2>
      <div class="gallery">
        <div class="photo">🌙</div>
        <div class="photo">💌</div>
        <div class="photo">✨</div>
      </div>
    </section>
  </main>

  <footer class="footer">Made with love • Keep growing together</footer>
</div>
</body>
</html>
'''

class WebsiteHandler(BaseHTTPRequestHandler):
	def serve_page_file(self, file_name):
		page_path = PAGE_DIR / file_name
		if not page_path.exists():
			self.send_error(404)
			return
		content = page_path.read_bytes()
		self.send_response(200)
		self.send_header('Content-Type', 'text/html; charset=utf-8')
		self.send_header('Content-Length', str(len(content)))
		self.end_headers()
		self.wfile.write(content)

	def do_GET(self):
		path = self.path.split('?', 1)[0]
		if path == '/api/accounts':
			with sqlite3.connect(DATABASE) as connection:
				rows = connection.execute('SELECT id, name, partner, email, course, created_at FROM accounts ORDER BY id DESC').fetchall()
			self.send_json({'accounts': [dict(zip(('id', 'name', 'partner', 'email', 'course', 'created_at'), row)) for row in rows]})
			return
		if path in PAGE_ROUTES:
			self.serve_page_file(PAGE_ROUTES[path])
			return
		if path in ('/story', '/story.html'):
			self.serve_page_file('story.html')
			return
		if path not in ('/', '/index.html'):
			self.send_error(404)
			return
		content = PAGE.encode('utf-8')
		self.send_response(200)
		self.send_header('Content-Type', 'text/html; charset=utf-8')
		self.send_header('Content-Length', str(len(content)))
		self.end_headers()
		self.wfile.write(content)

	def do_POST(self):
		if self.path != '/api/accounts':
			self.send_error(404)
			return
		try:
			length = int(self.headers.get('Content-Length', '0'))
			payload = json.loads(self.rfile.read(length).decode('utf-8'))
			required = ('name', 'partner', 'email', 'password')
			if any(not str(payload.get(key, '')).strip() for key in required):
				self.send_json({'error': 'Name, partner, email, and password are required.'}, 400)
				return
			password_hash = hashlib.sha256(payload['password'].encode('utf-8')).hexdigest()
			with sqlite3.connect(DATABASE) as connection:
				cursor = connection.execute('''INSERT INTO accounts
					(name, partner, address, phone, mother, father, course, qualification, current_study, email, password_hash)
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
					payload['name'].strip(), payload['partner'].strip(), payload.get('address', '').strip(),
					payload.get('phone', '').strip(), payload.get('mother', '').strip(), payload.get('father', '').strip(),
					payload.get('course', '').strip(), payload.get('qualification', '').strip(),
					payload.get('currentStudy', '').strip(), payload['email'].strip().lower(), password_hash))
				account_id = cursor.lastrowid
			self.send_json({'id': account_id, 'message': 'Account saved.'}, 201)
		except sqlite3.IntegrityError:
			self.send_json({'error': 'That email already has an account.'}, 409)
		except (ValueError, json.JSONDecodeError):
			self.send_json({'error': 'Please send valid account data.'}, 400)

	def send_json(self, payload, status=200):
		content = json.dumps(payload).encode('utf-8')
		self.send_response(status)
		self.send_header('Content-Type', 'application/json; charset=utf-8')
		self.send_header('Content-Length', str(len(content)))
		self.end_headers()
		self.wfile.write(content)

	def log_message(self, format, *args):
		return


def main():
	server = HTTPServer((HOST, PORT), WebsiteHandler)
	print(f'Website running at http://{HOST}:{PORT}')
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print('\nWebsite stopped.')
	finally:
		server.server_close()


if __name__ == '__main__':
	main()
