import streamlit as st
import socket
import threading
import os
import struct
import secrets
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="CipherTransfer", page_icon="⚡", layout="wide")

# ══════════════════════════════════════════════════════════════
# MIDNIGHT PLASMA CSS
# Deep navy bg · Electric violet primary · Cyan highlights · Rose accent
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Syne:wght@400;600;800&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    background-color: #0a0e1a !important;
    color: #c8d4f0 !important;
    font-family: 'Syne', sans-serif !important;
}
.stApp {
    background: radial-gradient(ellipse at 20% 0%, #1a1f3a 0%, #0a0e1a 55%) !important;
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── Header ── */
.plasma-header {
    background: linear-gradient(135deg, #0f1330 0%, #1a1040 100%);
    border: 1px solid #6c3eff33;
    border-radius: 16px;
    padding: 2.2rem 2.8rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.plasma-header::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle, #6c3eff18 0%, transparent 70%);
}
.plasma-header::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 20%;
    width: 320px; height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, #00e5ff10 0%, transparent 70%);
}
.plasma-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #eeeeff;
    letter-spacing: -0.02em;
    margin: 0 0 0.3rem;
    position: relative;
    z-index: 1;
}
.plasma-title .v  { color: #6c3eff; }
.plasma-title .c  { color: #00e5ff; }
.plasma-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #6c3eff99;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin: 0;
    position: relative;
    z-index: 1;
}
.plasma-chips {
    margin-top: 1rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}
.plasma-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    padding: 0.22rem 0.7rem;
    border-radius: 20px;
    border: 1px solid;
}
.plasma-chip.v { color: #6c3eff; border-color: #6c3eff44; background: #6c3eff11; }
.plasma-chip.c { color: #00e5ff; border-color: #00e5ff44; background: #00e5ff0d; }
.plasma-chip.p { color: #ff6b9d; border-color: #ff6b9d44; background: #ff6b9d0d; }

/* ── Tab buttons ── */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    background: #0f1330 !important;
    border: 1px solid #6c3eff44 !important;
    color: #a090d0 !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.4rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #6c3eff22 !important;
    border-color: #6c3eff !important;
    color: #c8b8ff !important;
    box-shadow: 0 0 20px #6c3eff33, inset 0 0 20px #6c3eff08 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Section label ── */
.sec-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #6c3eff;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin: 1.4rem 0 0.55rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-label::before {
    content: '';
    width: 3px; height: 14px;
    background: linear-gradient(180deg, #6c3eff, #00e5ff);
    border-radius: 2px;
    display: inline-block;
    flex-shrink: 0;
}
.step-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 0.14rem 0.5rem;
    border-radius: 4px;
    background: #6c3eff22;
    border: 1px solid #6c3eff44;
    color: #9d7aff;
}

/* ── Content boxes ── */
.plasma-box {
    background: #0f1330;
    border: 1px solid #6c3eff22;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    color: #c8d4f0;
    word-break: break-all;
    line-height: 1.8;
}
.plasma-box.cipher {
    background: #0c1128;
    border-color: #6c3eff44;
    border-left: 2px solid #6c3eff;
    color: #00e5ff;
}
.plasma-box.key-box {
    background: #120a20;
    border-color: #ff6b9d33;
    border-left: 2px solid #ff6b9d;
    color: #ffb8d4;
}
.plasma-box.plain-box {
    background: #0d1228;
    border-color: #00e5ff22;
    color: #c8d4f0;
    font-family: 'Syne', sans-serif;
    font-size: 0.86rem;
    line-height: 1.65;
    word-break: normal;
}
.plasma-box.denied {
    background: #180810;
    border-color: #ff6b9d22;
    border-left: 2px solid #ff6b9d;
    text-align: center;
    padding: 2.8rem 1.5rem;
}
.plasma-box.granted {
    background: #08182a;
    border-color: #00e5ff44;
    border-left: 2px solid #00e5ff;
    padding: 1.1rem 1.4rem;
}

/* ── Badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    padding: 0.28rem 0.75rem;
    border-radius: 20px;
    margin: 0.35rem 0 0.15rem;
}
.badge.locked   { color: #6c3eff; background: #6c3eff15; border: 1px solid #6c3eff44; }
.badge.denied-b { color: #ff6b9d; background: #ff6b9d12; border: 1px solid #ff6b9d44; }
.badge.success  { color: #00e5ff; background: #00e5ff10; border: 1px solid #00e5ff44; }

/* ── Access denied / granted ── */
.denied-icon  { font-size: 2rem; display: block; text-align: center; margin-bottom: 0.5rem; }
.denied-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem; font-weight: 800;
    color: #ff6b9d; text-align: center;
    letter-spacing: 0.05em; margin-bottom: 0.3rem;
}
.denied-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; text-align: center;
    color: #ff6b9d55; letter-spacing: 0.06em;
}
.granted-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.92rem; font-weight: 700;
    color: #00e5ff; letter-spacing: 0.04em;
}
.key-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem; font-weight: 600;
    color: #ff6b9d; letter-spacing: 0.12em;
    text-transform: uppercase; margin-bottom: 0.5rem;
}
.footnote {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: #ff6b9d66;
    margin-top: 0.35rem; letter-spacing: 0.04em;
}
.integrity-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: #00e5ff;
    background: #00e5ff0e; border: 1px solid #00e5ff44;
    padding: 0.22rem 0.65rem; border-radius: 20px;
    letter-spacing: 0.1em; margin-top: 0.45rem;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #6c3eff18 !important; margin: 0.8rem 0 !important; }

/* ── File uploader ── */
.stFileUploader > div {
    border: 1px dashed #6c3eff44 !important;
    background: #0f1330 !important;
    border-radius: 10px !important;
}
.stFileUploader label { color: #6c3eff !important; font-size: 0.78rem !important; }
[data-testid="stFileUploadDropzone"] p { color: #a090d0 !important; }

/* ── Text input ── */
.stTextInput > div > div > input {
    background: #0f1330 !important;
    border: 1px solid #6c3eff33 !important;
    border-radius: 9px !important;
    color: #c8d4f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.76rem !important;
    caret-color: #00e5ff !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6c3eff !important;
    box-shadow: 0 0 0 3px #6c3eff20 !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #6c3eff55 !important; }

/* ── Alerts ── */
.stAlert { border-radius: 9px !important; font-family: 'Syne', sans-serif !important; }

/* ── Download button ── */
.stDownloadButton > button {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    background: linear-gradient(135deg, #6c3eff, #4c20df) !important;
    border: none !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.4rem !important;
    width: 100% !important;
    box-shadow: 0 4px 20px #6c3eff44 !important;
    letter-spacing: 0.04em !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #7d52ff, #5c30ef) !important;
    box-shadow: 0 6px 28px #6c3eff60 !important;
    transform: translateY(-1px) !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# THREAD-SAFE GLOBALS
# ══════════════════════════════════════════════════════════════
_server_ready = threading.Event()
_result: dict = {}

KEY_DIR = "keys"
HOST    = "127.0.0.1"
PORT    = 65432

# ══════════════════════════════════════════════════════════════
# CRYPTO
# ══════════════════════════════════════════════════════════════
def get_rsa_keys():
    os.makedirs(KEY_DIR, exist_ok=True)
    priv_p = os.path.join(KEY_DIR, "server_private.pem")
    pub_p  = os.path.join(KEY_DIR, "server_public.pem")
    if os.path.exists(priv_p):
        with open(priv_p, "rb") as f:
            priv = serialization.load_pem_private_key(f.read(), password=None)
        with open(pub_p, "rb") as f:
            pub  = serialization.load_pem_public_key(f.read())
    else:
        priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pub  = priv.public_key()
        with open(priv_p, "wb") as f:
            f.write(priv.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()))
        with open(pub_p, "wb") as f:
            f.write(pub.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo))
    return priv, pub

def recv_exact(conn, n):
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection dropped")
        buf += chunk
    return buf

def recv_framed(conn):
    return recv_exact(conn, struct.unpack(">I", recv_exact(conn, 4))[0])

def send_framed(conn, data: bytes):
    conn.sendall(struct.pack(">I", len(data)) + data)

def aes_encrypt(key: bytes, plaintext: bytes) -> bytes:
    nonce = secrets.token_bytes(12)
    return nonce + AESGCM(key).encrypt(nonce, plaintext, None)

def aes_decrypt(key: bytes, payload: bytes) -> bytes:
    return AESGCM(key).decrypt(payload[:12], payload[12:], None)

# ══════════════════════════════════════════════════════════════
# SERVER THREAD
# ══════════════════════════════════════════════════════════════
def _server_worker():
    global _result
    _result = {}
    try:
        priv, pub = get_rsa_keys()
        pub_pem = pub.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((HOST, PORT))
            srv.listen(1)
            _server_ready.set()
            srv.settimeout(30)
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                _result["error"] = "Timed out"
                return
        with conn:
            send_framed(conn, pub_pem)
            enc_key     = recv_framed(conn)
            session_key = priv.decrypt(
                enc_key,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(), label=None))
            filename  = recv_framed(conn).decode()
            payload   = recv_framed(conn)
            decrypted = aes_decrypt(session_key, payload)
            os.makedirs("received_files", exist_ok=True)
            with open(os.path.join("received_files", filename), "wb") as f:
                f.write(decrypted)
            conn.sendall(b"OK")
        _result = {"decrypted_bytes": decrypted}
    except Exception as e:
        _result["error"] = str(e)

# ══════════════════════════════════════════════════════════════
# CLIENT
# ══════════════════════════════════════════════════════════════
def _send_file(file_bytes: bytes, filename: str):
    session_key = secrets.token_bytes(32)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        pub = serialization.load_pem_public_key(recv_framed(s))
        enc = pub.encrypt(
            session_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(), label=None))
        send_framed(s, enc)
        send_framed(s, filename.encode())
        payload = aes_encrypt(session_key, file_bytes)
        send_framed(s, payload)
        s.recv(8)
    cipher_b64   = base64.b64encode(payload).decode()
    combined_key = base64.b64encode(session_key).decode() + "_" + cipher_b64
    return cipher_b64, combined_key

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
for k, v in {
    "tab": "sender", "cipher_b64": "", "combined_key": "",
    "filename": "", "transfer_done": False,
    "decrypted_bytes": b"", "decrypt_result": "", "decrypt_ok": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="plasma-header">
  <div class="plasma-title">
    <span class="v">⚡</span> Cipher<span class="c">Transfer</span>
  </div>
  <p class="plasma-subtitle">End-to-end encrypted file transfer over TCP sockets</p>
  <div class="plasma-chips">
    <span class="plasma-chip v">AES-256-GCM</span>
    <span class="plasma-chip c">RSA-2048</span>
    <span class="plasma-chip p">Python Sockets</span>
    <span class="plasma-chip v">Streamlit</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB SWITCHER
# ══════════════════════════════════════════════════════════════
t1, t2 = st.columns(2)
with t1:
    if st.button("💾  Sender — Encrypt & Lock", use_container_width=True):
        st.session_state.tab = "sender"
with t2:
    if st.button("🔓  Receiver — Enter Key & Unlock", use_container_width=True):
        st.session_state.tab = "receiver"

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ▌ SENDER
# ══════════════════════════════════════════════════════════════
if st.session_state.tab == "sender":
    st.markdown('<div class="sec-label"><span class="step-pill">SENDER</span>&nbsp; Upload · Encrypt · Share Key</div>', unsafe_allow_html=True)

    # 01 — upload
    st.markdown('<div class="sec-label"><span class="step-pill">01</span>&nbsp; Select file to encrypt</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=None, label_visibility="collapsed")

    # 02 — original preview
    if uploaded:
        raw = uploaded.read()
        uploaded.seek(0)
        st.markdown('<div class="sec-label"><span class="step-pill">02</span>&nbsp; Original file content</div>', unsafe_allow_html=True)
        try:
            preview = raw.decode("utf-8", errors="replace")
        except Exception:
            preview = f"[Binary file — {len(raw)} bytes]"
        st.markdown(f'<div class="plasma-box plain-box">{preview}</div>', unsafe_allow_html=True)

    # 03 — encrypt
    st.markdown('<div class="sec-label"><span class="step-pill">03</span>&nbsp; Encrypt &amp; send</div>', unsafe_allow_html=True)
    if st.button("⚡  Encrypt File & Generate Key", use_container_width=True):
        if not uploaded:
            st.warning("Please select a file first.")
        else:
            file_bytes = uploaded.read()
            filename   = uploaded.name
            _server_ready.clear()
            t = threading.Thread(target=_server_worker, daemon=True)
            t.start()
            if not _server_ready.wait(timeout=6):
                st.error("⚠ Server failed to start. If port 65432 is busy, restart the app.")
            else:
                try:
                    cipher_b64, combined_key = _send_file(file_bytes, filename)
                    t.join(timeout=6)
                    st.session_state.cipher_b64    = cipher_b64
                    st.session_state.combined_key  = combined_key
                    st.session_state.filename      = filename
                    st.session_state.transfer_done = True
                    if "decrypted_bytes" in _result:
                        st.session_state.decrypted_bytes = _result["decrypted_bytes"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Transfer failed: {e}")

    # 04 — ciphertext
    if st.session_state.transfer_done and st.session_state.cipher_b64:
        st.markdown(
            '<div class="sec-label"><span class="step-pill">04</span>&nbsp;'
            ' Encrypted ciphertext'
            ' <span style="color:#ff6b9d;font-size:0.65rem;margin-left:6px;">'
            '(unreadable without key)</span></div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div class="plasma-box cipher">{st.session_state.cipher_b64}</div>',
            unsafe_allow_html=True)
        st.markdown('<span class="badge locked">⬡ Locked · AES-256-GCM</span>', unsafe_allow_html=True)

        # 05 — key
        st.markdown(
            '<div class="sec-label" style="margin-top:1.3rem">'
            '<span class="step-pill">05</span>&nbsp;'
            ' Your decryption key — give this to the receiver</div>',
            unsafe_allow_html=True)
        st.markdown(f"""
<div class="plasma-box key-box">
  <div class="key-label">🔑 Decryption key — share with receiver</div>
  {st.session_state.combined_key}
</div>
<p class="footnote">⚠ Without this key, the message is mathematically impossible to recover.</p>
""", unsafe_allow_html=True)
        st.success(f"✅  '{st.session_state.filename}' encrypted and transferred successfully.")

# ══════════════════════════════════════════════════════════════
# ▌ RECEIVER
# ══════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="sec-label"><span class="step-pill">RECEIVER</span>&nbsp; Enter Key · Decrypt · Download</div>', unsafe_allow_html=True)

    # 01 — paste ciphertext
    st.markdown('<div class="sec-label"><span class="step-pill">01</span>&nbsp; Intercepted transmission</div>', unsafe_allow_html=True)
    cipher_input = st.text_input(
        "", value=st.session_state.cipher_b64,
        label_visibility="collapsed",
        placeholder="Paste the ciphertext here...")
    if cipher_input:
        preview = cipher_input[:300] + ("..." if len(cipher_input) > 300 else "")
        st.markdown(f'<div class="plasma-box cipher">{preview}</div>', unsafe_allow_html=True)
        st.markdown('<span class="badge denied-b">◉ Encrypted · Contents hidden</span>', unsafe_allow_html=True)

    # 02 — decrypted panel
    st.markdown('<div class="sec-label" style="margin-top:1.2rem"><span class="step-pill">02</span>&nbsp; Decrypted message</div>', unsafe_allow_html=True)
    if not st.session_state.decrypt_ok:
        st.markdown("""
<div class="plasma-box denied">
  <span class="denied-icon">🔒</span>
  <div class="denied-title">Access Denied</div>
  <p class="denied-sub">Enter the decryption key below to unlock this message</p>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class="plasma-box granted">
  <div class="granted-title">🔓 Access Granted — Message Decrypted</div>
</div>
<div class="plasma-box plain-box" style="margin-top:6px;">{st.session_state.decrypt_result}</div>
<span class="integrity-badge">✓ Integrity Verified</span>
""", unsafe_allow_html=True)

    # 03 — key input
    st.markdown('<div class="sec-label" style="margin-top:1.2rem"><span class="step-pill">03</span>&nbsp; Enter decryption key</div>', unsafe_allow_html=True)
    key_input = st.text_input(
        "", label_visibility="collapsed",
        placeholder="Paste decryption key here...",
        type="password")

    if st.button("🔓  Unlock & Decrypt", use_container_width=True):
        if not cipher_input:
            st.warning("Paste the ciphertext first.")
        elif not key_input:
            st.warning("Paste the decryption key.")
        else:
            try:
                parts = key_input.split("_", 1)
                if len(parts) != 2:
                    raise ValueError("Invalid key format — copy the full key from the Sender tab.")
                session_key = base64.b64decode(parts[0])
                payload     = base64.b64decode(cipher_input)
                decrypted   = aes_decrypt(session_key, payload)
                st.session_state.decrypt_result  = decrypted.decode("utf-8", errors="replace")
                st.session_state.decrypt_ok      = True
                st.session_state.decrypted_bytes = decrypted
                st.rerun()
            except Exception as e:
                st.error(f"Decryption failed — wrong key or corrupted data. ({e})")
                st.session_state.decrypt_ok = False

    # 04 — download
    if st.session_state.decrypt_ok and st.session_state.decrypted_bytes:
        st.markdown('<div class="sec-label" style="margin-top:1.2rem"><span class="step-pill">04</span>&nbsp; Download decrypted file</div>', unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download Decrypted File",
            data=st.session_state.decrypted_bytes,
            file_name=st.session_state.filename or "decrypted_file.txt",
            use_container_width=True)
