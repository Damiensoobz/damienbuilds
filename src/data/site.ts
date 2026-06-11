// ─────────────────────────────────────────────────────────────
// Single source of truth for figures that appear in more than one
// place on the site. Update here once; every page reads from this.
// ─────────────────────────────────────────────────────────────

/**
 * Founding-client spots still available.
 * Shown on the homepage (Work section) AND the pricing page — drive
 * both from this constant so the counter can never contradict itself.
 */
export const FOUNDING_SPOTS_REMAINING = 3;

/** Total founding spots on offer (used in prose: "3 founding clients"). */
export const FOUNDING_SPOTS_TOTAL = 3;

/**
 * Web3Forms access key — powers the contact form AND the launch-notify popup.
 *
 * Get yours free (no account, no card) at https://web3forms.com :
 *   1. Enter the email address where you want submissions delivered.
 *   2. They email you an access key (a UUID like "a1b2c3d4-...").
 *   3. Paste it below, replacing YOUR_ACCESS_KEY_HERE.
 *
 * The key is meant to live in the public page source — it only allows
 * sending submissions to your inbox, nothing else.
 */
export const WEB3FORMS_ACCESS_KEY = "3096dcb9-fa86-4011-9b1d-3d5b4f1e21c8";

/** Headline prices, written once so the pages stay in sync. */
export const PRICING = {
  standard: "R5,000",
  founding: "R2,500",
  siteRescueAudit: "R850",
  carePlanMonthly: "R500",
  ownDomainDiscount: "R900",
} as const;
