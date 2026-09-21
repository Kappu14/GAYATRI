from http.server import BaseHTTPRequestHandler, HTTPServer


HOST = "127.0.0.1"
PORT = 8001

PAGE = """<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>For You, Always</title>
	<style>
		@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Playfair+Display:wght@500;600;700&display=swap');
		:root { --ink: #2f2430; --wine: #8b3046; --rose: #d96c78; --paper: #fffaf3; --gold: #d8a85b; }
		* { box-sizing: border-box; }
		body { margin: 0; color: var(--ink); background: #f3ddd2; font-family: 'DM Mono', monospace; }
		.page { min-height: 100vh; overflow: hidden; position: relative; background: radial-gradient(circle at 80% 0%, #f9c7b9 0 18%, transparent 38%), linear-gradient(135deg, #f6e8d7, #edc4c3 55%, #b95b6d); }
		.page::before { content: ''; position: absolute; inset: 0; opacity: .32; background-image: radial-gradient(#fff 1px, transparent 1px); background-size: 24px 24px; pointer-events: none; }
		nav, main, footer { position: relative; z-index: 1; max-width: 1120px; margin: auto; padding-left: 7vw; padding-right: 7vw; }
		nav { padding-top: 28px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; }
		.mark { color: var(--wine); font-weight: 500; }
		.date { color: #76545c; }
		main { min-height: calc(100vh - 92px); padding-top: 11vh; padding-bottom: 7vh; display: grid; grid-template-columns: 1.05fr .95fr; gap: 8vw; align-items: center; }
		.eyebrow { color: var(--wine); font-size: 12px; letter-spacing: .16em; text-transform: uppercase; margin-bottom: 24px; }
		h1 { max-width: 650px; margin: 0; font-family: 'Playfair Display', Georgia, serif; font-size: clamp(3.8rem, 8vw, 7.5rem); line-height: .88; letter-spacing: 0; font-weight: 600; }
		h1 em { color: var(--wine); font-weight: 500; }
		.intro { max-width: 420px; margin: 32px 0; font-size: 14px; line-height: 1.8; color: #634d52; }
		.name-form { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 440px; margin: 28px 0 18px; }
		.name-form label { display: grid; gap: 8px; color: var(--wine); font-size: 10px; letter-spacing: .08em; text-transform: uppercase; }
		.name-form input { width: 100%; border: 1px solid rgba(139,48,70,.45); border-radius: 2px; padding: 13px 12px; color: var(--ink); background: rgba(255,250,243,.66); font: 13px 'DM Mono', monospace; outline: none; }
		.name-form input:focus { border-color: var(--wine); box-shadow: 0 0 0 3px rgba(139,48,70,.1); }
		button { border: 1px solid var(--wine); border-radius: 2px; color: var(--paper); background: var(--wine); font: 500 12px 'DM Mono', monospace; letter-spacing: .08em; padding: 15px 19px; cursor: pointer; transition: transform .2s, background .2s; }
		button:hover { transform: translateY(-3px); background: #6d2337; }
		.letter { position: relative; background: var(--paper); padding: 42px 38px 40px; box-shadow: 18px 18px 0 rgba(139,48,70,.18); transform: rotate(2.5deg); animation: arrive .9s ease both; }
		.letter::before { content: '♥'; position: absolute; right: 25px; top: 18px; color: var(--rose); font-size: 22px; }
		.letter-label { color: var(--rose); font-size: 11px; letter-spacing: .12em; text-transform: uppercase; }
		.letter h2 { margin: 38px 0 23px; font-family: 'Playfair Display', Georgia, serif; font-size: 35px; font-weight: 600; }
		.letter p { margin: 0 0 18px; font-size: 13px; line-height: 1.9; color: #604d50; }
		.signature { color: var(--wine) !important; font-family: 'Playfair Display', Georgia, serif; font-size: 27px !important; font-style: italic; margin-top: 28px !important; }
		.rose-gift { display: grid; place-items: center; min-height: 115px; margin: 0 0 20px; text-align: center; }
		.rose { display: none; font-size: 72px; line-height: 1; filter: drop-shadow(0 8px 5px rgba(139,48,70,.18)); animation: bloom .65s ease both; }
		.rose.visible { display: block; }
		.rose-caption { margin: 10px 0 0; color: var(--wine); font-size: 11px; }
		.little-things { max-width: 440px; margin-top: 24px; border-top: 1px solid rgba(139,48,70,.25); padding-top: 20px; }
		.little-things-title { color: var(--wine); font-size: 10px; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 13px; }
		.little-things-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
		.mini-button { padding: 11px 7px; color: var(--wine); background: rgba(255,250,243,.5); border-color: rgba(139,48,70,.35); font-size: 10px; letter-spacing: 0; }
		.mini-button:hover { color: var(--paper); }
		.surprise { min-height: 20px; margin: 14px 0 0; color: #634d52; font-family: 'Playfair Display', Georgia, serif; font-size: 18px; font-style: italic; line-height: 1.4; }
		footer { padding-bottom: 24px; color: #76545c; font-size: 11px; display: flex; justify-content: space-between; }
		.heart { position: fixed; z-index: 2; bottom: -30px; color: var(--wine); pointer-events: none; animation: float 4s linear forwards; }
		@keyframes arrive { from { opacity: 0; transform: translateY(30px) rotate(2.5deg); } to { opacity: 1; transform: rotate(2.5deg); } }
		@keyframes float { to { transform: translateY(-110vh) rotate(25deg); opacity: 0; } }
		@keyframes bloom { from { opacity: 0; transform: scale(.35) rotate(-18deg); } to { opacity: 1; transform: scale(1) rotate(0); } }
		@media (max-width: 720px) { nav { padding-top: 20px; } main { padding-top: 70px; display: block; } h1 { font-size: clamp(3.6rem, 18vw, 6rem); } .intro { margin: 26px 0; } .name-form { grid-template-columns: 1fr; } .letter { margin: 72px 4px 30px; padding: 34px 25px; } footer { font-size: 9px; } }
	</style>
</head>
<body>
	<div class="page">
		<nav><span class="mark">Kapil's little note</span><span class="date">14 / 02 / always</span></nav>
		<main>
			<section>
				<div class="eyebrow">A message from the heart</div>
				<h1>For <span id="partnerHeading">Gayatri</span>,<br><em>always.</em></h1>
				<p class="intro">Some feelings deserve more than a text message. This is a tiny corner of the internet, made just to say: you make ordinary days feel extraordinary.</p>
				<div class="name-form">
					<label>Your name<input id="senderName" value="Kapil" maxlength="30" autocomplete="name"></label>
					<label>Partner's name<input id="partnerName" value="Gayatri" maxlength="30" autocomplete="name"></label>
				</div>
				<button id="heartButton" type="button">GIVE A ROSE &nbsp; 🌹</button>
				<div class="little-things">
					<div class="little-things-title">Choose a little surprise</div>
					<div class="little-things-grid">
						<button class="mini-button" id="complimentButton" type="button">A COMPLIMENT</button>
						<button class="mini-button" id="reasonButton" type="button">A REASON</button>
						<button class="mini-button" id="dateButton" type="button">DATE IDEA</button>
					</div>
					<div class="surprise" id="surprise" aria-live="polite"></div>
				</div>
			</section>
			<article class="letter">
				<div class="letter-label">Open when you need a smile</div>
				<div class="rose-gift"><div id="rose" class="rose" aria-live="polite">🌹<div id="roseCaption" class="rose-caption">A rose for Gayatri</div></div></div>
				<h2>Dear <span id="partnerLetter">Gayatri</span>,</h2>
				<p>Thank you for all the small moments that somehow become my favorite memories.</p>
				<p>Wherever the day takes us, I hope you know that being with you feels like coming home.</p>
				<p class="signature">With all my heart,<br><span id="senderLetter">Kapil</span></p>
			</article>
		</main>
		<footer><span>Made with intention</span><span>✦ Keep this close</span></footer>
	</div>
	<script>
		const button = document.querySelector('#heartButton');
		const senderName = document.querySelector('#senderName');
		const partnerName = document.querySelector('#partnerName');
		const rose = document.querySelector('#rose');
		const surprise = document.querySelector('#surprise');
		const surprises = {
			compliment: ['Your smile makes every room feel warmer.', 'You make kindness look effortless.', 'You are wonderfully, completely yourself.'],
			reason: ['I love the way you make little moments unforgettable.', 'I love how safe and understood you make me feel.', 'I love that life is brighter with you in it.'],
			date: ['A sunset walk, your favorite dessert, and no phones.', 'A cozy movie night with snacks chosen by you.', 'A little day trip somewhere neither of us has been.']
		};
		const showSurprise = (type) => {
			updateNames();
			const choice = surprises[type][Math.floor(Math.random() * surprises[type].length)];
			surprise.textContent = choice.replace('you', partnerName.value.trim() || 'you');
		};
		document.querySelector('#complimentButton').addEventListener('click', () => showSurprise('compliment'));
		document.querySelector('#reasonButton').addEventListener('click', () => showSurprise('reason'));
		document.querySelector('#dateButton').addEventListener('click', () => showSurprise('date'));
		const updateNames = () => {
			const sender = senderName.value.trim() || 'Someone special';
			const partner = partnerName.value.trim() || 'your love';
			document.querySelector('#partnerHeading').textContent = partner;
			document.querySelector('#partnerLetter').textContent = partner;
			document.querySelector('#senderLetter').textContent = sender;
			document.querySelector('#roseCaption').textContent = `A rose for ${partner}`;
		};
		senderName.addEventListener('input', updateNames);
		partnerName.addEventListener('input', updateNames);
		button.addEventListener('click', () => {
			updateNames();
			rose.classList.remove('visible');
			void rose.offsetWidth;
			rose.classList.add('visible');
			for (let i = 0; i < 9; i++) {
				const heart = document.createElement('span');
				heart.className = 'heart'; heart.textContent = i % 2 ? '♥' : '♡';
				heart.style.left = `${35 + Math.random() * 30}%`;
				heart.style.fontSize = `${16 + Math.random() * 18}px`;
				heart.style.animationDelay = `${Math.random() * .6}s`;
				document.body.appendChild(heart);
				heart.addEventListener('animationend', () => heart.remove());
			}
			button.textContent = 'ROSE GIFTED  🌹';
			setTimeout(() => { button.innerHTML = 'GIVE A ROSE &nbsp; 🌹'; }, 1800);
		});
	</script>
</body>
</html>"""


class WebsiteHandler(BaseHTTPRequestHandler):
		def do_GET(self):
				if self.path not in ("/", "/index.html"):
						self.send_error(404)
						return
				content = PAGE.encode("utf-8")
				self.send_response(200)
				self.send_header("Content-Type", "text/html; charset=utf-8")
				self.send_header("Content-Length", str(len(content)))
				self.end_headers()
				self.wfile.write(content)

		def log_message(self, format, *args):
				return


if __name__ == "__main__":
		server = HTTPServer((HOST, PORT), WebsiteHandler)
		print(f"Website running at http://{HOST}:{PORT}")
		try:
				server.serve_forever()
		except KeyboardInterrupt:
				print("\nWebsite stopped.")
		finally:
				server.server_close()
