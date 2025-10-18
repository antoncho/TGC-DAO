"use client";
import React, { useState } from "react";
import FadeIn from "./FadeIn";
import TextInput from "./TextInput";
import RadioInput from "./RadioInput";
import Button from "./Button";

const ContactForm = () => {
  const [status, setStatus] = useState({ state: "idle", message: "" });

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus({ state: "submitting", message: "" });
    const form = e.currentTarget;
    const formData = new FormData(form);
    // Honeypot
    formData.set("website", "");

    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Failed to send message.");
      }
      setStatus({ state: "success", message: "Thanks — we’ll be in touch shortly." });
      form.reset();
    } catch (err) {
      setStatus({ state: "error", message: err.message || "Something went wrong." });
    }
  }

  return (
    <FadeIn>
      <form onSubmit={handleSubmit} noValidate>
        <h2 className="font-display text-base font-semibold text-neutral-950">
          Work inquiries
        </h2>
        <div className="isolate mt-6 -space-y-px rounded-2xl bg-white/50">
          <TextInput label="Name" name="name" autoComplete="name" required />
          <TextInput
            label="Email"
            type="email"
            name="email"
            autoComplete="email"
            required
          />
          <TextInput
            label="Company"
            name="company"
            autoComplete="organization"
          />
          <TextInput label="Phone" type="tel" name="phone" autoComplete="tel" />
          <TextInput label="Message" name="message" required />
          {/* Honeypot field (hidden) */}
          <input type="text" name="website" className="hidden" tabIndex="-1" autoComplete="off" />
          <div className="border border-neutral-300 px-6 py-8 first:rounded-t-2xl last:rounded-b-2xl">
            <fieldset>
              <legend className="text-base/6 text-neutral-500">Budget</legend>
            </fieldset>
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-8">
              <RadioInput label="$25K – $50K" name="budget" value="25" />
              <RadioInput label="$50K – $100K" name="budget" value="50" />
              <RadioInput label="$100K – $150K" name="budget" value="100" />
              <RadioInput label="More than $150K" name="budget" value="150" />
            </div>
          </div>
        </div>
        <Button type="submit" className="mt-10" disabled={status.state === "submitting"}>
          Let’s work together
        </Button>
        {status.message && (
          <p
            className={`mt-4 text-sm ${
              status.state === "success" ? "text-green-600" : "text-red-600"
            }`}
            role="status"
          >
            {status.message}
          </p>
        )}
      </form>
    </FadeIn>
  );
};

export default ContactForm;
