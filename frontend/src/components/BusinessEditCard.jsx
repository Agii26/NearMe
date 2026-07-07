import { useState } from "react";
import { updateBusiness, uploadBusinessPhoto } from "../api/client";
import { useAuthStore } from "../store/authStore";
import HoursEditor from "./HoursEditor";
import FormField, { inputStyle } from "./FormField";

export default function BusinessEditCard({ business, categories, onSaved }) {
  const accessToken = useAuthStore((state) => state.accessToken);
  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState(business.name);
  const [categoryId, setCategoryId] = useState(business.category?.id || "");
  const [contactPhone, setContactPhone] = useState(business.contact_phone || "");
  const [contactEmail, setContactEmail] = useState(business.contact_email || "");
  const [hours, setHours] = useState(business.hours || {});
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  async function handleSave(event) {
    event.preventDefault();
    setStatus("saving");
    setError(null);
    try {
      await updateBusiness(
        business.id,
        { name, category: categoryId || null, contact_phone: contactPhone, contact_email: contactEmail, hours },
        accessToken
      );
      setStatus("saved");
      onSaved?.();
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  async function handlePhotoChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      await uploadBusinessPhoto(business.id, file, accessToken);
      onSaved?.();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div style={{ border: "1px solid var(--color-border)", borderRadius: "12px", padding: "14px", marginBottom: "12px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <p style={{ fontFamily: "var(--font-heading)", fontWeight: 600, fontSize: "15px", color: "var(--color-text-primary)", margin: 0 }}>
          {business.name}
        </p>
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          style={{ background: "none", border: "none", color: "var(--color-accent)", fontSize: "13px", cursor: "pointer" }}
        >
          {isOpen ? "Close" : "Edit"}
        </button>
      </div>

      {isOpen && (
        <form onSubmit={handleSave} style={{ marginTop: "12px" }}>
          <FormField label="Name">
            <input style={inputStyle} value={name} onChange={(e) => setName(e.target.value)} />
          </FormField>

          <FormField label="Category">
            <select style={inputStyle} value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              <option value="">No category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </FormField>

          <FormField label="Contact phone">
            <input style={inputStyle} value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} />
          </FormField>

          <FormField label="Contact email">
            <input style={inputStyle} value={contactEmail} onChange={(e) => setContactEmail(e.target.value)} />
          </FormField>

          <label style={{ fontSize: "13px", fontWeight: 500, color: "var(--color-text-primary)", display: "block", marginBottom: "8px" }}>
            Hours
          </label>
          <HoursEditor hours={hours} onChange={setHours} />

          <FormField label="Add a photo">
            <input type="file" accept="image/*" onChange={handlePhotoChange} style={{ fontSize: "12px" }} />
          </FormField>

          {error && <p style={{ color: "var(--color-danger)", fontSize: "12px", marginTop: "10px" }}>{error}</p>}

          <button
            type="submit"
            disabled={status === "saving"}
            style={{
              marginTop: "8px",
              padding: "10px 16px",
              borderRadius: "10px",
              border: "none",
              background: "var(--color-accent)",
              color: "#ffffff",
              fontSize: "13px",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            {status === "saving" ? "Saving…" : status === "saved" ? "Saved \u2713" : "Save changes"}
          </button>
        </form>
      )}
    </div>
  );
}
