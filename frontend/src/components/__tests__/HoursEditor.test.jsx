import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import HoursEditor from "../HoursEditor";

describe("HoursEditor", () => {
  it("renders all seven days", () => {
    render(<HoursEditor hours={{}} onChange={() => {}} />);
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].forEach((day) => {
      expect(screen.getByText(day)).toBeInTheDocument();
    });
  });

  it("checking 'Closed' for a day sets its hours to an empty array", async () => {
    const onChange = jest.fn();
    render(<HoursEditor hours={{ mon: [["09:00", "18:00"]] }} onChange={onChange} />);
    const mondayRow = screen.getByText("Monday").closest("div");
    const checkbox = mondayRow.querySelector('input[type="checkbox"]');
    await userEvent.click(checkbox);
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ mon: [] }));
  });

  it("unchecking 'Closed' restores a default 09:00-18:00 span", async () => {
    const onChange = jest.fn();
    render(<HoursEditor hours={{ mon: [] }} onChange={onChange} />);
    const mondayRow = screen.getByText("Monday").closest("div");
    const checkbox = mondayRow.querySelector('input[type="checkbox"]');
    await userEvent.click(checkbox);
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ mon: [["09:00", "18:00"]] }));
  });

  it("does not mutate other days when one day changes", async () => {
    const onChange = jest.fn();
    render(<HoursEditor hours={{ tue: [["10:00", "14:00"]] }} onChange={onChange} />);
    const mondayRow = screen.getByText("Monday").closest("div");
    const checkbox = mondayRow.querySelector('input[type="checkbox"]');
    await userEvent.click(checkbox);
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ tue: [["10:00", "14:00"]] }));
  });
});
