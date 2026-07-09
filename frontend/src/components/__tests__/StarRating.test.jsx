import { render, screen } from "@testing-library/react";
import StarRating from "../StarRating";

describe("StarRating", () => {
  it("shows 'No reviews yet' when value is null", () => {
    render(<StarRating value={null} />);
    expect(screen.getByText("No reviews yet")).toBeInTheDocument();
  });

  it("shows the numeric average and review count", () => {
    render(<StarRating value={4.5} count={12} />);
    expect(screen.getByText("4.5 (12)")).toBeInTheDocument();
  });

  it("can hide the numeric label", () => {
    render(<StarRating value={3.2} showNumber={false} />);
    expect(screen.queryByText(/3\.2/)).not.toBeInTheDocument();
  });
});
