export const runtime = "nodejs";

import nodemailer from "nodemailer";

function sanitize(input) {
  if (typeof input !== "string") return "";
  return input.replace(/[\0\x08\x09\x1a\n\r\'\"\\\%]/g, (c) => {
    switch (c) {
      case "\0":
        return "\\0";
      case "\x08":
        return "\\b";
      case "\x09":
        return "\\t";
      case "\x1a":
        return "\\z";
      case "\n":
        return "\\n";
      case "\r":
        return "\\r";
      case "'":
        return "\\'";
      case '"':
        return "\\\"";
      case "\\":
        return "\\\\";
      case "%":
        return "\\%";
      default:
        return c;
    }
  });
}

async function sendWithResend(payload) {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) return { ok: false, error: "RESEND_API_KEY not set" };

  const to = process.env.CONTACT_RECIPIENT || "thegenuine.collective@gmail.com";
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: "The Genuine Collective <onboarding@resend.dev>",
      to: [to],
      reply_to: payload.email || undefined,
      subject: `New contact form submission – ${payload.name || payload.email || "Unknown"}`,
      text: payload.text,
      html: payload.html,
    }),
  });
  if (!res.ok) {
    const e = await res.text();
    return { ok: false, error: e || res.statusText };
  }
  return { ok: true };
}

async function sendWithSMTP(payload) {
  const host = process.env.SMTP_HOST;
  const port = Number(process.env.SMTP_PORT || 587);
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;
  if (!host || !user || !pass) return { ok: false, error: "SMTP env not set" };

  const transporter = nodemailer.createTransport({
    host,
    port,
    secure: !!(process.env.SMTP_SECURE === "true" || port === 465),
    auth: { user, pass },
  });

  const to = process.env.CONTACT_RECIPIENT || "thegenuine.collective@gmail.com";
  const from = process.env.SMTP_FROM || `The Genuine Collective <${user}>`;

  await transporter.sendMail({
    from,
    to,
    subject: `New contact form submission – ${payload.name || payload.email || "Unknown"}`,
    text: payload.text,
    html: payload.html,
    replyTo: payload.email || undefined,
  });

  return { ok: true };
}

function buildMessage(data) {
  const name = sanitize(data.name || "");
  const email = sanitize(data.email || "");
  const company = sanitize(data.company || "");
  const phone = sanitize(data.phone || "");
  const message = sanitize(data.message || "");
  const budget = sanitize(data.budget || "");

  const lines = [
    `Name: ${name}`,
    `Email: ${email}`,
    company && `Company: ${company}`,
    phone && `Phone: ${phone}`,
    budget && `Budget: ${budget}`,
    "",
    "Message:",
    message,
  ].filter(Boolean);

  const text = lines.join("\n");
  const html = `<div>
    <p><strong>Name:</strong> ${name || ""}</p>
    <p><strong>Email:</strong> ${email || ""}</p>
    ${company ? `<p><strong>Company:</strong> ${company}</p>` : ""}
    ${phone ? `<p><strong>Phone:</strong> ${phone}</p>` : ""}
    ${budget ? `<p><strong>Budget:</strong> ${budget}</p>` : ""}
    <hr />
    <p>${(message || "").replace(/\n/g, "<br/>")}</p>
  </div>`;

  return { text, html };
}

export async function POST(request) {
  try {
    const contentType = request.headers.get("content-type") || "";
    let data = {};
    if (contentType.includes("application/json")) {
      data = await request.json();
    } else {
      const form = await request.formData();
      form.forEach((value, key) => {
        data[key] = value?.toString?.() ?? "";
      });
    }

    // Honeypot field to reduce bot spam
    if (data.website) {
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    }

    const name = (data.name || "").toString().trim();
    const email = (data.email || "").toString().trim();
    const message = (data.message || "").toString().trim();
    if (!name || !email || !message) {
      return new Response(
        JSON.stringify({ error: "Missing required fields (name, email, message)." }),
        { status: 400 }
      );
    }

    const { text, html } = buildMessage(data);
    const payload = { ...data, text, html };

    // Prefer Resend if configured, else SMTP
    let result = { ok: false };
    if (process.env.RESEND_API_KEY) {
      result = await sendWithResend(payload);
    }
    if (!result.ok && process.env.SMTP_HOST) {
      result = await sendWithSMTP(payload);
    }
    if (!result.ok) {
      return new Response(
        JSON.stringify({
          error:
            "Email service not configured. Set RESEND_API_KEY or SMTP_HOST/SMTP_USER/SMTP_PASS.",
        }),
        { status: 500 }
      );
    }

    return new Response(JSON.stringify({ ok: true }), { status: 200 });
  } catch (err) {
    console.error("/api/contact error", err);
    return new Response(
      JSON.stringify({ error: "Failed to send message.", details: `${err}` }),
      { status: 500 }
    );
  }
}

