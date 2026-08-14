export default async function handler(req, res) {
  const allowedOrigin = "https://riakhina.github.io";
  res.setHeader("Access-Control-Allow-Origin", allowedOrigin);
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");

  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const {
    name = "",
    contact = "",
    lang,
    answerTexts = [],
    questions = [],
    utm = {},
    bookingDate = "",
    bookingTime = "",
    bookingCustom = "",
    bookingComment = "",
    contactChannel = "",
    mode = "form"
  } = req.body || {};

  if (mode === "form" && (!name || !contact)) {
    return res.status(400).json({ error: "Name and contact are required" });
  }

  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) return res.status(500).json({ error: "Telegram is not configured" });

  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"
  }[c]));

  const title = mode === "early_social_click"
    ? "⚡ Ранний контакт: человек решил написать сам"
    : mode === "social_click"
      ? "💬 Запись: человек выбрал написать сам"
      : "🎯 Новая заявка с квиза «Карта выхода»!";

  let text = `<b>${title}</b>\n\n`;
  text += `<b>Имя:</b> ${esc(name || "не указано")}\n`;
  if (contact) text += `<b>Контакт:</b> ${esc(contact)}\n`;
  if (contactChannel) text += `<b>Способ связи:</b> ${esc(contactChannel)}\n`;
  if (mode === "early_social_click") text += `<b>Этап:</b> до выбора даты и времени\n<b>Время:</b> не выбирал\n`;
  if (bookingDate || bookingTime) {
    text += `<b>Желаемое время:</b> ${esc([bookingDate, bookingTime].filter(Boolean).join(" · "))}\n`;
  }
  if (bookingCustom) text += `<b>Своё время:</b> ${esc(bookingCustom)}\n`;
  if (bookingComment) text += `<b>Комментарий:</b> ${esc(bookingComment)}\n`;
  text += `<b>Язык:</b> ${esc(lang || "—").toUpperCase()}\n`;

  if (utm && (utm.source || utm.medium || utm.campaign || utm.content || utm.term)) {
    text += `<b>Источник:</b> ${esc(utm.source || '—')} / ${esc(utm.medium || '—')} / ${esc(utm.campaign || '—')}\n`;
    if (utm.content) text += `<b>UTM content:</b> ${esc(utm.content)}\n`;
    if (utm.term) text += `<b>UTM term:</b> ${esc(utm.term)}\n`;
  }

  if (questions.length) {
    text += `\n<b>Ответы:</b>\n`;
    questions.forEach((q, i) => {
      text += `${i + 1}. ${esc(q)}\n→ ${esc(answerTexts[i] || "—")}\n`;
    });
  }

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
