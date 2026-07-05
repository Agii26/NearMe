import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SearchBar from "../SearchBar";

describe("SearchBar", () => {
  it("calls onChange with the typed value", async () => {
    const onChange = jest.fn();
    render(<SearchBar value="" onChange={onChange} onUseMyLocation={() => {}} isUsingDeviceLocation={false} />);
    await userEvent.type(screen.getByLabelText("Search for a business or category"), "cafe");
    expect(onChange).toHaveBeenCalledTimes(4); // one call per keystroke
    expect(onChange).toHaveBeenLastCalledWith("e");
  });

  it("calls onUseMyLocation when the location button is clicked", async () => {
    const onUseMyLocation = jest.fn();
    render(<SearchBar value="" onChange={() => {}} onUseMyLocation={onUseMyLocation} isUsingDeviceLocation={false} />);
    await userEvent.click(screen.getByTitle("Use my location"));
    expect(onUseMyLocation).toHaveBeenCalledTimes(1);
  });

  it("reflects the active state via aria-pressed when using device location", () => {
    render(<SearchBar value="" onChange={() => {}} onUseMyLocation={() => {}} isUsingDeviceLocation={true} />);
    expect(screen.getByTitle("Use my location")).toHaveAttribute("aria-pressed", "true");
  });
});
