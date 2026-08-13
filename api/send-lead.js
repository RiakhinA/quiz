export default async function handler(req, res) {
  const allowedOrigin = "https://riakhina.github.io";
  res.setHeader("Access-Control-Allow-Origin", allowedOrigin);
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");

  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const { name, contact, lang, answerTexts = [], questions = [] } = req.body || {};
  if (!name || !contact) return res.status(400).json({ error: "Name and contact are required" });

  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) return res.status(500).json({ error: "Telegram is not configured" });

  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"
  }[c]));

  let text = `<b>🎯 Новая заявка с квиза «Карта выхода»!</b>\n\n`;
  text += `<b>Имя:</b> ${esc(name)}\n<b>Контакт:</b> ${esc(contact)}\n<b>Язык:</b> ${esc(lang).toUpperCase()}\n\n<b>Ответы:</b>\n`;
  questions.forEach((q, i) => {
    text += `${i + 1}. ${esc(q)}\n→ ${esc(answerTexts[i] || "—")}\n`;
  });

  const tg = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text, parse_mode: "HTML" })
  });

  if (!tg.ok) {
    console.error("Telegram error", await tg.text());
    return res.status(502).json({ error: "Telegram request failed" });
  }

  return res.status(200).json({ ok: true });
}
