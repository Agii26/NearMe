import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import BusinessCard from "../BusinessCard";

function renderCard(business) {
  return render(
    <MemoryRouter>
      <BusinessCard business={business} />
    </MemoryRouter>
  );
}

describe("BusinessCard", () => {
  it("renders name, category, and distance", () => {
    renderCard({
      id: 1,
      name: "Better Days Café",
      category: { name: "Food & Dining" },
      distance_km: 0.6,
      is_open_now: true,
    });
    expect(screen.getByText("Better Days Café")).toBeInTheDocument();
    expect(screen.getByText(/Food & Dining/)).toBeInTheDocument();
    expect(screen.getByText(/0.6km/)).toBeInTheDocument();
    expect(screen.getByText("open")).toBeInTheDocument();
  });

  it("shows 'closed' when is_open_now is false", () => {
    renderCard({ id: 2, name: "IronWorks", category: { name: "Retail" }, distance_km: 2.1, is_open_now: false });
    expect(screen.getByText("closed")).toBeInTheDocument();
  });

  it("omits the status label entirely when hours are unknown", () => {
    renderCard({ id: 3, name: "QC Family Clinic", category: { name: "Health" }, distance_km: 0.5, is_open_now: null });
    expect(screen.queryByText("open")).not.toBeInTheDocument();
    expect(screen.queryByText("closed")).not.toBeInTheDocument();
  });

  it("links to the business's profile page", () => {
    renderCard({ id: 42, name: "Test Biz", category: { name: "Retail" }, distance_km: 1, is_open_now: true });
    expect(screen.getByRole("link")).toHaveAttribute("href", "/business/42");
  });
});
