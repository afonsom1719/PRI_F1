import React from "react";
import Select from "react-select";
import "./LanguageOptions.css";

interface DropdownProps {
    options: string[];
    codes: string[];
    onSelect: (value: string) => void;
    label?: string;
}

const Dropdown: React.FC<DropdownProps> = ({ options, codes, onSelect, label }) => {
    const handleChange = (selectedOption: any) => {
        const newValue = selectedOption.value;
        onSelect(newValue);
    };

    const customOptions = options.map((option, index) => ({
        value: option,
        label: (
            <span style={{ color: "rgb(60, 60, 60)" }}>
                <img
                    src={`https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/${codes[index].toLowerCase()}.svg`}
                    className="flag-icon"
                    style={{ width: "20px", height: "15px", objectFit: "contain" }}
                />
            </span>
        )
    }));

    return (
        <div className="dropdown">
            <Select className="dropdown-select" options={customOptions} menuPlacement="auto" onChange={handleChange} defaultValue={customOptions[0]} />
        </div>
    );
};

export default Dropdown;
