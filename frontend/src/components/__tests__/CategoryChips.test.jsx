import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CategoryChips from "../CategoryChips";

const categories = [
  { slug: "food-dining", name: "Food & Dining" },
  { slug: "retail", name: "Retail" },
];

describe("CategoryChips", () => {
  it("always renders an 'All' option in addition to the given categories", () => {
    render(<CategoryChips categories={categories} selectedSlug="all" onSelect={() => {}} />);
    expect(screen.getByRole("tab", { name: "All" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Food & Dining" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Retail" })).toBeInTheDocument();
  });

  it("marks the currently selected slug as aria-selected", () => {
    render(<CategoryChips categories={categories} selectedSlug="retail" onSelect={() => {}} />);
    expect(screen.getByRole("tab", { name: "Retail" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: "All" })).toHaveAttribute("aria-selected", "false");
  });

  it("calls onSelect with the clicked category's slug", async () => {
    const onSelect = jest.fn();
    render(<CategoryChips categories={categories} selectedSlug="all" onSelect={onSelect} />);
    await userEvent.click(screen.getByRole("tab", { name: "Retail" }));
    expect(onSelect).toHaveBeenCalledWith("retail");
  });
});
